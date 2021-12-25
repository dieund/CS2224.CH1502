import glob,os
import cv2
import numpy as np

from whoosh.fields import Schema, TEXT, ID, NUMERIC
from whoosh import index
from whoosh.qparser import QueryParser
from whoosh.query import *

#Begin ========== Khởi tạo các thông số yolov4 =============
CONFIDENCE = 0.4
SCORE_THRESHOLD = 0.5
IOU_THRESHOLD = 0.5
config_path = "yolo-coco/yolov4.cfg"
weights_path = "yolo-coco/yolov4.weights"
LABELS = open("yolo-coco/coco.names").read().strip().split("\n")
net = cv2.dnn.readNetFromDarknet(config_path, weights_path)
ln = net.getLayerNames()
ln = [ln[i - 1] for i in net.getUnconnectedOutLayers()]
#end ========== Khởi tạo các thông số yolov4 =============

#Hàm detectIndex phát hiện và lấy các đối tượng trong hình
# Input: File hình
# output List[dic[class_id,confidence]]
def detectIndex(filename):
    image = cv2.imread(filename)
    h, w = image.shape[:2]
    blob = cv2.dnn.blobFromImage(image, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)

    layer_outputs = net.forward(ln)
    ret  = []
    boxes, confidences, class_ids = [], [], []
    for output in layer_outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > CONFIDENCE:
                box = detection[:4] * np.array([w, h, w, h])
                (centerX, centerY, width, height) = box.astype("int")
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))
                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                class_ids.append(class_id)
    idxs = cv2.dnn.NMSBoxes(boxes, confidences, SCORE_THRESHOLD, IOU_THRESHOLD)
    if len(idxs) > 0:
        for i in idxs.flatten():
            ret.append(LABELS[class_ids[i]])
    return ret

# Hàm build schema
# input null
# output (thư mục indexdir của ham)
def buildIndex():
    schema = Schema(filename=TEXT(stored=True), obj=ID(stored=True), objname=TEXT(stored = True), )
    if not os.path.exists("indexdir"):
       os.mkdir("indexdir")
    ix = index.create_in("indexdir", schema) 
    writer = ix.writer()
    
    listFile =[]
    for filename in glob.glob("image_download/*.jpg"):
        listFile.append(filename)
    for filename in glob.glob("image_download/*.png"):
        listFile.append(filename)
        
    for filename in listFile:
        print(filename)
        objdetection = detectIndex(filename)
        print(objdetection)
        if len(objdetection) > 0:
            class_names = ' '.join(objdetection)
            writer.add_document(filename=filename,objname=class_names)
    writer.commit()


def searchImage(filename):

    img_grayscale = cv2.imread(filename)
    cv2.imshow('source:',img_grayscale)

    objdetection = detectIndex(filename)
    if len(objdetection)>0:
        myqueryItem = []
        print("\nInput:");
        print('File: ',filename)
        print("Content:",' '.join(objdetection),"\n")
        for obj in objdetection:
            myqueryItem.append(Term("objname",obj))
        myquery = And(myqueryItem)
        
        ix = index.open_dir("indexdir")
        
        with ix.searcher() as searcher:
            results = searcher.search(myquery)    
            print("Result\nFile:" ,results[0]["filename"])
            print("Content:" ,results[0]["objname"])
            img_grayscale = cv2.imread(results[0]["filename"])
            cv2.imshow('Result:',img_grayscale)
            
        #searcher.close()
    cv2.waitKey()



#buildIndex();

searchImage('./images/cam3.jpeg')