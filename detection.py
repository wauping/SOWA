from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QImage
import cv2
import numpy as np
import time
import requests





class Detection(QThread):
    changePixmap = pyqtSignal(QImage)

    def init(self):
        super(Detection, self).init()

    def run(self):
        self.running = True
        net = cv2.dnn.readNet("weights/best.onnx", "cfg/yolov8.yaml") 
        # classes = []
        # with open('obj.names', 'r') as f:
        #     classes = [line.strip() for line in f.readlines()]

        layer_names = net.getLayerNames()
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
        print(output_layers)

        starting_time = time.time()
        
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 0)
        if not cap.isOpened():
            print('Camera is not available')
            exit()

        while self.running:
            ret, frame = cap.read()
            if ret:
                # height, width, channels = frame.shape
                blob = cv2.dnn.blobFromImage(frame, 0.00392, (640, 640), (0, 0, 0), True, crop=False)
                net.setInput(blob)
                outs = net.forward(output_layers)
                # boxes = []
                # confidences = []
                for i in range(outs[0][0][0].shape[0]):
                    # print(outs[0][0][0].shape[0])
                    x = outs[0][0][0][i]
                    y = outs[0][0][1][i]
                    w = outs[0][0][2][i]
                    h = outs[0][0][3][i]
                    confidence = outs[0][0][4][i]  
                    

                    if confidence > 0.2:
                        center_x = int(x)
                        center_y = int(y)
                        w = int(w)
                        h = int(h)
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)
                        # x1 = int((x - w / 2))
                        # y1 = int((y - h / 2))
                        # x2 = int((x + w / 2))
                        # y2 = int((y + h / 2))
                        # boxes.append([x, y, w, h])
                        # confidences.append(float(confidence))
                        # indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.8, 0.3)
                        # for i in range(len(boxes)):
                            # cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                        cv2.putText(frame, 'pistol' + " {0:.1%}".format(confidence), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                        elapsed_time = starting_time - time.time()
                        if elapsed_time <= -10:
                            starting_time = time.time()
                            self.save_detection(frame)
                        

                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(1500, 953, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)

            time.sleep(0.1)
        cap.release()
        cv2.destroyAllWindows()
    
    def save_detection(self, frame):
        cv2.imwrite('saved_frame/frame.jpg', frame)
        print('Frame saved')
        self.post_detection()
        
    def post_detection(self):
        try:
            url = 'http://localhost:1337/alerts'
            # headers = {'Authorization': 'Token ' + self.token}
            # files = {'image': open('saved_frame/frame.jpg', 'rb')}
            data = {"user_id": 1,"location": "gde"}
            response = requests.post(url, data=data)  
	    	# HTTP 200
            if response.ok:
                print('Alert was sent to the server')
	    	# Bad response
            else:
                print('Unable to send alert to the server') 
        except Exception:
            print('Unable to access server')