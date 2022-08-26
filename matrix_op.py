import cv2
import numpy as np

def edgify(mat):
    KERNEL = 5
    mat = np.array(mat)
    mat_modified = mat.copy()
    for r in range(len(mat)):
        for c in range(len(mat[0])):
            top = max(0, r - int(KERNEL/2))
            bottom = min(len(mat) + 1, r + int(KERNEL/2) + 1)
            left = max(0, c - int(KERNEL/2))
            right = min(len(mat[0]) + 1, c + int(KERNEL/2) + 1)
            slice = mat[top:bottom,left:right,:]
            if slice.shape[0] == 0 or slice.shape[1] == 0:
                mat_modified[r][c][:] = 1
                continue
            else:
                mat_modified[r][c][:] = np.std(slice)
    return mat_modified / np.max(mat_modified)#scale to [0,1]
            




if __name__ == "__main__":
    img = cv2.imread("test.png",2)
    modif = edgify(img)
    cv2.imshow("op",modif)
    cv2.waitKey(0) 
    cv2.destroyAllWindows()