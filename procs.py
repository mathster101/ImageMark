import multiprocessing as mp
import cv2
import matrix_op as mop
import time
from timeit import default_timer as timer
import numpy as np
def display_process(original_image, CORES, queue):
    screen = original_image
    cv2.namedWindow("ImageMark", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("ImageMark", lambda *args : None)
    flag = True
    counter = 0
    while flag:
        counter += 1
        if queue.qsize() > CORES * 3:
            print("INCREASE CHUNK SIZE!")
        if queue.empty() != True:
            chunk_data = queue.get()
            if chunk_data == "STOP":
                time.sleep(2)
                flag = False
                continue
            chunk = chunk_data["matrix"]
            screen[chunk_data["tl"][0]:chunk_data["br"][0],chunk_data["tl"][1]:chunk_data["br"][1],:] = chunk
        if counter%30000 == 0:
            cv2.imshow("ImageMark", screen)
            cv2.setWindowProperty('ImageMark', 1, cv2.WINDOW_NORMAL)
            cv2.resizeWindow("ImageMark", int(len(screen[0])/5), int(len(screen)/5))
            cv2.waitKey(1)
            counter = 0
    print("disp terminated")

def single_core(chunk_data, img):
    cv2.namedWindow("Single Core", cv2.WINDOW_KEEPRATIO)
    start = timer()
    for cd in chunk_data:
        img[cd["tl"][0]:cd["br"][0],cd["tl"][1]:cd["br"][1],:] = 255 * mop.edgify(cd["matrix"])
        cv2.imshow("Single Core", img)
        key = cv2.waitKey(1)
    end = timer()
    cv2.destroyAllWindows()   
    return end - start # elapsed

def chunk_process(in_queue, disp_queue):
    from os import getpid
    print(getpid()%21)
    while not in_queue.empty():
        chunk_data = in_queue.get()
        chunk_data["matrix"] = 255 * mop.edgify(chunk_data["matrix"])
        chunk_data["matrix"] = cv2.applyColorMap(chunk_data["matrix"].astype(np.uint8), getpid()%21)
        #send to disp proc
        disp_queue.put(chunk_data)
    #print("end of life")
    quit()

def multi_core(img, chunk_data, CORES):
    chunk_data = chunk_data[::-1]
    procs = []
    kappa = mp.Lock()
    #display proc and queue
    disp_queue = mp.Queue()
    disp =  mp.Process(target=display_process, args=(img, CORES, disp_queue, ))
    disp.start()
    start = timer()
    ##########################
    for i in range(CORES):
        temp = dict()
        temp["in"]   = mp.Queue()
        temp["lock"] = mp.Lock()
        temp["proc"] = mp.Process(target=chunk_process, args=(temp["in"], disp_queue, ))
        procs.append(temp)
    while len(chunk_data) > 0:
        for i  in range(CORES):
            if len(chunk_data) == 0:
                continue
            procs[i]["in"].put(chunk_data.pop())
    for i in range(CORES):
        procs[i]["proc"].daemon = True
        procs[i]["proc"].start()
 
    for i in range(CORES):
        procs[i]["proc"].join()
        #print("killed one")
    end = timer()
    disp_queue.put("STOP")
    print(end - start)
    
if __name__ == "__main__":
    pass