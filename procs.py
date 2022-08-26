import multiprocessing as mp
import cv2
import matrix_op as mop
import time
from timeit import default_timer as timer
import random

def chunk_process(chunk_data, queue):
    chunk = chunk_data["matrix"]
    chunk_data["matrix"] = 255 * mop.edgify(chunk)
    #send to disp proc
    queue.put(chunk_data)
    return chunk_data

def chunk_process2(in_queue, out_queue, disp_queue):
    flag = True
    hungry_sent = False
    while flag:
        print("cp")
        print(in_queue.qsize(), out_queue.qsize())
        if not in_queue.empty():
            chunk_data = in_queue.get()
            if chunk_data == "TERMINATE":
                print("kill cmd")
                flag = False
            else:
                chunk = chunk_data["matrix"]
                chunk_data["matrix"] = 255 * mop.edgify(chunk)
                disp_queue.put(chunk_data)
                hungry_sent = False
                print(in_queue.qsize(), out_queue.qsize())
                if in_queue.empty():
                    if not hungry_sent:
                        out_queue.put("HUNGRY")
                        hungry_sent = True
                        print(in_queue.qsize(), out_queue.qsize())
                        print("pp")
                    pass
        else:
            if not hungry_sent:
                out_queue.put("HUNGRY")
                hungry_sent = True
            pass
    #send to disp proc

def display_process(original_image, queue):
    screen = original_image
    cv2.namedWindow("ImageMark", cv2.WINDOW_KEEPRATIO)
    flag = True
    while flag:
        if queue.empty() != True:
            chunk_data = queue.get()
            if chunk_data == "STOP":
                time.sleep(2)
                flag = False
                continue
            chunk = chunk_data["matrix"]
            screen[chunk_data["tl"][0]:chunk_data["br"][0],chunk_data["tl"][1]:chunk_data["br"][1],:] = chunk
        cv2.imshow("ImageMark", screen)
        cv2.setWindowProperty('ImageMark', 1, cv2.WINDOW_NORMAL)
        cv2.resizeWindow("ImageMark", 500, 500)
        cv2.waitKey(1)

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

def multi_core(img,chunk_data):
    CORES = 4
    chunk_data = chunk_data[::-1]
    flag = True
    procs = []
    queue = mp.Queue()
    disp = mp.Process(target=display_process, args=(img,queue, ))
    disp.start()
    start = timer()
    for i in range(CORES):
        procs.append( mp.Process(target=chunk_process, args=(chunk_data.pop(), queue,)) )
        procs[i].start()
    while flag:
        for i in list(range(len(procs)))[::-1]:
            if procs[i].is_alive() == False:
                procs.pop(i)
        if len(procs) < CORES and len(chunk_data) > 0:
            #random.shuffle(chunk_data)
            for i in range(CORES - len(procs)):
                #procs.append( mp.Process(target=chunk_process, args=(chunk_data.pop(), queue,)) )
                procs = [mp.Process(target=chunk_process, args=(chunk_data.pop(), queue,))] + procs
                procs[0].start()
        if len(procs) <= 1 and len(chunk_data) == 0:
            flag = False
            queue.put("STOP")
    end = timer()
    print(end - start,"seconds")
    return True

def multi_core2(img, chunk_data):
    CORES = 4
    chunk_data = chunk_data[::-1]
    procs = []
    #display proc and queue
    disp_queue = mp.Queue()
    disp =  mp.Process(target=display_process, args=(img,disp_queue, ))
    disp.start()
    start = timer()
    ##########################
    for i in range(CORES):
        temp = dict()
        temp["in"]   = mp.Queue()
        temp["out"]  = mp.Queue()
        temp["proc"] = mp.Process(target=chunk_process2, args=(temp["in"], temp["out"], disp_queue,))
        temp["status"] = "Free"
        procs.append(temp)
    for i in range(CORES):
        procs[i]["proc"].start()  
    active = True
    while len(procs) > 0:
        for i in range(len(procs) - 1, -1, -1):
            try:
                if procs[i]["status"] == False:
                    continue
            except Exception as e:
                pass

            if len(chunk_data) == 0 and procs[i]["in"].empty():
                print("len procs = ",len(procs), " i = ",i)
                procs[i]["in"].put("TERMINATE")
            else:
                if procs[i]["out"].empty() != True:
                    data = procs[i]["out"].get()
                    if data == "HUNGRY":
                        procs[i]["in"].put(chunk_data.pop())
                        #print(i, "l = ", procs[i]["in"].qsize(),procs[i]["out"].qsize())

    end = timer()
    disp_queue.put("STOP")
    print(end - start, "seconds")


if __name__ == "__main__":
    pass