import multiprocessing as mp
import os
import threading
import time

def camThread(running, frameBuffer):
    print("camThread pid:", os.getpid(), " tid:", threading.current_thread().ident)
    import pyrealsense2 as rs2
    ctx = rs2.context()
    devs = ctx.query_devices()
    print("query_devices %d" % devs.size())

    pipe = rs2.pipeline()

    pipe.start()
    for i in range(10):
        while frameBuffer.full():
            time.sleep(0.1)
        frame = pipe.wait_for_frames()
        frameBuffer.put(frame.frame_number)
        print("frame_number: %d" % frame.frame_number)
    pipe.stop()
    
    running.put(False)

def TestMultiProcess():
    print("TestMultiProcess pid:", os.getpid(), " tid:", threading.current_thread().ident)
    frameBuffer = mp.Queue()
    running = mp.Queue()
    p = mp.Process(target=camThread, args=(running, frameBuffer,))
    p.start()

    while running.empty():
        if frameBuffer.empty():
            time.sleep(0.1)
            continue
        print("recv frame %d" % frameBuffer.get())
    
    p.join()

if __name__ == '__main__':
    print("mainThread pid:", os.getpid(), " tid:", threading.current_thread().ident)
    TestMultiProcess()
