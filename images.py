import cv2

def path_to_img(path):
    bgr_img = cv2.imread(path)
    return cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
