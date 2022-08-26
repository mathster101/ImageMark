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
    cv2.namedWindow("ImageMark", cv2.WINDOW_NORMAL)
    flag = True
    while flag:
        if queue.empty() != True:
            chunk_data = queue.get()
            if chunk_data == "STOP":
                time.sleep(6)
                flag = False
                continue
            chunk = chunk_data["matrix"]
            screen[chunk_data["tl"][0]:chunk_data["br"][0],chunk_data["tl"][1]:chunk_data["br"][1],:] = chunk
        cv2.imshow("ImageMark", screen)
        cv2.waitKey(200)

def multi_core(img, CHUNK_SIZE, chunk_data):
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
        procs[-1].start()
    while flag:
        for i in range(len(procs) - 1,0,-1):
            if procs[i].is_alive() == False:
                procs.pop(i)
        if len(procs) < CORES and len(chunk_data) > 0:
            #random.shuffle(chunk_data)
            for i in range(CORES - len(procs)):
                procs.append( mp.Process(target=chunk_process, args=(chunk_data.pop(), queue,)) )
                procs[-1].start()
        if len(procs) <= 1 and len(chunk_data) == 0:
            flag = False
            queue.put("STOP")
    end = timer()
    print(end - start,"seconds")
    return True




if __name__ == "__main__":
    pass