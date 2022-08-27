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

def chunk_process2(in_queue, out_queue, disp_queue, lock):
    terminate = False
    while terminate == False:
        if in_queue.empty() == False:
            lock.acquire()
            data = in_queue.get()
            lock.release()
            if data == "TERMINATE":
                terminate = True
            elif data == None:
                continue
            else:
                send = dict({})
                chunk = data["matrix"]
                send["matrix"] = 255* mop.edgify(chunk)
                send["br"] = data["br"]
                send["tl"] = data["tl"]
                lock.acquire()
                disp_queue.put(send)
                lock.release()
        else:
            lock.acquire()
            if out_queue.empty() == True:
                out_queue.put("HUNGRY")
            lock.release()
    print("Terminated")    


def multi_core2(img, chunk_data):
    CORES = 4
    chunk_data = chunk_data[::-1]
    procs = []
    kappa = mp.Lock()
    #display proc and queue
    disp_queue = mp.Queue()
    disp =  mp.Process(target=display_process, args=(img,disp_queue, ))
    disp.start()
    start = timer()
    Flag = True
    num_terminated = 0
    ##########################
    for i in range(CORES):
        temp = dict()
        temp["in"]   = mp.Queue()
        temp["out"]  = mp.Queue()
        temp["lock"] = mp.Lock()
        temp["proc"] = mp.Process(target=chunk_process2, args=(temp["in"], temp["out"], disp_queue, temp["lock"],))
        procs.append(temp)
        procs[-1]["proc"].start()

    while Flag:
        for i in range(len(procs)):
            if len(chunk_data) > 0:
                #Core is requesting a chunk
                kappa.acquire()
                if procs[i]["out"].empty() != True:
                    msg = procs[i]["out"].get()
                    if msg == "HUNGRY":
                        chunk = chunk_data.pop()
                        procs[i]["in"].put(chunk)
                kappa.release()
            else:
                procs[i]["in"].put("TERMINATE")
                procs[i]["proc"].terminate()
                num_terminated += 1
                if num_terminated == CORES:
                    Flag = False
    end = timer()
    time.sleep(3)#doesnt exit gracefully without this
    disp_queue.put("STOP")
    print(end - start)    


if __name__ == "__main__":
    pass