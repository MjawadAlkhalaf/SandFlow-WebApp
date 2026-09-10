import cv2

def processJPEG(img):

    #uploaded picture dimension
    height, width = img.shape[:2]

    #resizing thrshold
    min_side = 1800
    max_side = 3000

    #Longest part of the ticket depending if it is portrait or landscape
    longest = max(height,width)

    #Resizing if image is too small
    if longest < min_side:
        scale = min_side/longest

        #rezcaling the image
        img = cv2.resize(img, None, fx = scale, fy=scale, interpolation = cv2.INTER_CUBIC)

    #resize if the image is too big
    elif longest > max_side:
        scale = max_side/longest
        img = cv2.resize(img, None, fx=scale, fy= scale, interpolation= cv2.INTER_AREA)

    #getting color components of a picture (brightness, green-red color scale, blue-yellow color scale)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2Lab)

    bright, red2green, blue2yellow = cv2.split(lab)

    #Creating histogram grid
    div_hist = cv2.createCLAHE(clipLimit= 2, tileGridSize=(8,8))

    #apllying histogram brightness
    bright = div_hist.apply(bright)

    #merging components back to geth
    lab = cv2.merge((bright, red2green, blue2yellow))

    #converting the image back to BGR
    img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR )
    

    return img