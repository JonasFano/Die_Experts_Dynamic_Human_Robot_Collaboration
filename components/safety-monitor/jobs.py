from safety_minitor import SafetyFrameResults, SafetyMonitor, PATCH_COORDS_LIST
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import threading
import time

def add_frames_to_queues(m: SafetyMonitor, qdistance, qimage, executor: ThreadPoolExecutor):
    while True:
        try:
            frames = m.get_frames()
        except Exception as e:
            print()
            print(e)
            print()

        if frames:
            DistanceJob(
                m,
                frames,
                qdistance
            )

        time.sleep(1/20)

def DistanceJob(m: SafetyMonitor, s: SafetyFrameResults, q: Queue) -> None:
    try:
        poses = m.calculate_poses(s.color_image)
        distance = m.calculate_human_robot_distance(
            poses, s.depth_frame, s.color_image
        )
        q.put(distance)
    except Exception as e:
        print(f"####################{e}")



def ImageStreamJob(m: SafetyMonitor, s: SafetyFrameResults, q: Queue) -> None:
    # Copy the image array to ensure no race condition/mutation errors
    print("Creating image with overlay")
    color_image = s.color_image.copy()
    poses = m.calculate_poses(color_image)
    m.apply_landmark_overlay(color_image, poses)
    m.apply_some_graphic(s.color_image, PATCH_COORDS_LIST)
    q.put(s.color_image)

"""

def testSync():
    m = SafetyMonitor()
    m.start()

    frames = m.get_frames()
    testQueue = Queue()
    testQueue2 = Queue()

    DistanceJob(m, frames, testQueue)
    ImageStreamJob(m, frames, testQueue2)

    print(testQueue.get())
    print(testQueue2.get())


def testAsyncThreadPool():
    m = SafetyMonitor()
    m.start()

    testQueue = Queue()
    testQueue2 = Queue()

    threading.Thread(target=add_frames_to_queues, args=(m, testQueue, testQueue2)).start()

    while True:
        print(testQueue.get())
        print(testQueue2.get())
        time.sleep(1)



"""
if __name__ == "__main__":
    m = SafetyMonitor()
    m.start()

    q1 = Queue()
    q2 = Queue()

    add_frames_to_queues(m, q1,q2, ThreadPoolExecutor())