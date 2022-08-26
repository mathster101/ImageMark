import matrix_op as mop
import multiprocessing as mp
import procs as p
import cv2
from timeit import default_timer as timer
import numpy as np

def load_image(path, CHUNK_SIZE):
    #load and crop image
    img = cv2.imread(path)
    rows = img.shape[0]
    cols = img.shape[1]
    lrows = int( CHUNK_SIZE * int(rows/CHUNK_SIZE) )
    lcols = int( CHUNK_SIZE * int(cols/CHUNK_SIZE) )
    img = img[0:lrows, 0:lcols, : ]
    return img

def extract_chunks(img, CHUNK_SIZE):
    chunk_data = []
    for row  in range(CHUNK_SIZE, img.shape[0] + 1, CHUNK_SIZE):
        prev_row = row - CHUNK_SIZE
        prev_col = 0 
        for col  in range(CHUNK_SIZE, img.shape[1] + 1, CHUNK_SIZE):
            data = {}
            #img = cv2.rectangle(img, (col,row), (prev_col,prev_row), (row/10,col/10,col), 2)
            data["br"] = (row, col)
            data["tl"] = (prev_row, prev_col)
            data["matrix"]   = img[prev_row : row, prev_col : col, :]
            chunk_data.append(data)
            prev_row = row - CHUNK_SIZE
            prev_col = col
    return chunk_data, img

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

if __name__ == "__main__":    
    CORES = 4
    CHUNK_SIZE = 10
    img = load_image("test2.png", CHUNK_SIZE)
    chunk_data, img1 = extract_chunks(img, CHUNK_SIZE)
    p.multi_core(img1, CHUNK_SIZE, chunk_data)
    t = single_core(chunk_data, img1)
    print(t,"seconds")
    #cv2.destroyAllWindows()    