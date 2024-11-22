from safety_minitor import SafetyFrameResults, SafetyMonitor, PATCH_COORDS_LIST
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import threading
import time

def add_frames_to_queues(m: SafetyMonitor, qdistance, qimage, executor: ThreadPoolExecutor):
    while True:
        frames = m.get_frames()
        print(f"Queue size is currently {qimage.qsize()}")
        # Send distance job to the pool
        executor.submit(
            DistanceJob,
            m,
            frames,
            qdistance,
        )

        executor.submit(
            ImageStreamJob,
            m,
            frames,
            qdistance,
        )

        time.sleep(1/15)



def DistanceJob(m: SafetyMonitor, s: SafetyFrameResults, q: Queue) -> None:
    print("Starting to calculate distance")
    poses = m.calculate_poses(s.color_image)
    distance = m.calculate_human_robot_distance(
        poses, s.depth_frame, s.color_image
    )
    print(distance)
    q.put(distance)



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




if __name__ == "__main__":
    testAsyncThreadPool()
"""