from safety_minitor import SafetyFrameResults, SafetyMonitor, PATCH_COORDS_LIST
import threading
import time
from fixture_checker import CheckFixtures 
from collections import deque


class ThreadSafeQueue:
    def __init__(self, max_size=10):
        self.queue = deque(maxlen=max_size)
        self.lock = threading.Lock()

    def get(self):
        """Returns the latest element without removing it."""
        with self.lock:
            if self.queue:
                return self.queue[-1]
            return None  # Return None if the queue is empty

    def put(self, element):
        """Adds an element to the queue at the front."""
        with self.lock:
            self.queue.appendleft(element)

    def clear(self):
        """Clears the queue."""
        with self.lock:
            self.queue.clear()


ref_img_path = 'images/reference.png'
paths = [(485, 345, 20, 15), # Component 1
    (465, 365, 20, 15), # Component 2
    (440, 395, 20, 15), # Component 3
    (415, 420, 20, 15)] # Component 4
fixture_checker = CheckFixtures(paths, ref_img_path)

FixtureStatusQueue = ThreadSafeQueue(2)
DistanceQueue = ThreadSafeQueue(2)
ImageStreamQueue = ThreadSafeQueue(2)

def add_frames_to_queues(m: SafetyMonitor, verbose: bool = False):
    while True:
        try:
            frames = m.get_frames()
            if verbose: 
                print("Got frames")

            if frames:
                if verbose:
                    print("Running distance job")
                DistanceJob(
                    m,
                    frames,
                    DistanceQueue
                )

            if frames:
                if verbose:
                    print("Running Image queue job")
                ImageStreamJob(m, frames, ImageStreamQueue)
            
            # Calculate 1 or 0 values of if a fixture is in the fixture holder or not.

            fixtures = fixture_checker.check_all_patches(frames.color_image, frames.depth_image)
            v = ",".join(map(lambda x: str(x), fixtures))
            FixtureStatusQueue.put(v)


        except Exception as e:
            print(e)

        time.sleep(1/20)
def DistanceJob(m: SafetyMonitor, s: SafetyFrameResults, q) -> None:
    try:
        poses = m.calculate_poses(s.color_image)
        distance = m.calculate_human_robot_distance(
            poses, s.depth_frame, s.color_image
        )
        q.put(distance)
    except Exception as e:
        print(f"####################{e}")



def ImageStreamJob(m: SafetyMonitor, s: SafetyFrameResults, q) -> None:
    # Copy the image array to ensure no race condition/mutation errors
    color_image = s.color_image.copy()
    poses = m.calculate_poses(color_image)
    color_image = m.apply_landmark_overlay(color_image, poses)
    color_image = m.apply_some_graphic(s.color_image, PATCH_COORDS_LIST)
    q.put(s.color_image)

def get_queue(q, h: str):
    print(f"{h} {q.get()}")

if __name__ == "__main__":
    m = SafetyMonitor()
    m.start()

    _async = False

    if _async:
        threading.Thread(target=add_frames_to_queues, args=(m))
    else:
        threading.Thread(target=lambda: get_queue(DistanceQueue, "Getting distance ")).start()
        add_frames_to_queues(m)

    print(DistanceQueue.get())
    print(ImageStreamQueue.get())