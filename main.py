import random
import procs as p
import cv2

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
    random.shuffle(chunk_data)
    return chunk_data, img

if __name__ == "__main__":    
    CORES = 4
    CHUNK_SIZE = 300
    img = load_image("test3.png", CHUNK_SIZE)
    chunk_data, img1 = extract_chunks(img, CHUNK_SIZE)
    p.multi_core(img1, chunk_data, CORES)
    #p.single_core(chunk_data, img1)
    