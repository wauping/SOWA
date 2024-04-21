from  PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QImage
import cv2
import numpy as np
import time 

class Detection(QThread):
    def init(self):
        super(Detection, self).init()

    changePixmap = pyqtSignal(QImage)

    def run(self):
        self.running = True

        net = cv2.dnn.readNet("weights/best.onnx", "cfg/yolov9-c.yaml")
        classes = []

        with open('obj.names', 'r') as f:
            classes = [line.strip() for line in f.readlines()]

        layer_names = net.getLayerNames()
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
        print(output_layers)
        colors = np.random.uniform(0, 255, size=(len(classes), 3))

        font = cv2.FONT_HERSHEY_PLAIN
        starting_time = time.time()
        
        # cap = cv2.VideoCapture(0)
        
        cap = cv2.VideoCapture('VIDEO\Weaponized_2.avi')
        # cap.open('https://videos3.earthcam.com/fecnetwork/9974.flv/chunklist_w1421640637.m3u8')
        try:
            while self.running:
                ret, frame = cap.read()
                if (ret):
                    height, width, channels = frame.shape


                    blob = cv2.dnn.blobFromImage(frame, 0.00392, (640, 640), (0, 0, 0), True, crop=False)
                    net.setInput(blob)
                    outs = net.forward(output_layers)

                    class_ids = []
                    confidences = []
                    boxes = []
                    for out in outs:
                        for detection in out:
                            scores = detection[5:]
                            class_id = np.unravel_index(np.argmax(scores), scores.shape)
                            confidence = scores[class_id]

                            if confidence > 0.9:
                                center_x = int(detection[0] * width)
                                center_y = int(detection[1] * height)
                                w = int(detection[2] * width)
                                h = int(detection[3] * height)

                                x = int(center_x - w / 2)
                                y = int(center_y - h / 2)

                                boxes.append([x, y, w, h])
                                confidences.append(float(confidence))
                                class_ids.append(class_ids)

                    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.8, 0.3)

                    for i in range(len(boxes)):
                        if i in indexes:
                            x, y, w, h = boxes[i]
                            label = str(classes[class_ids[i]])
                            confidence = confidences[i]
                            color = (256, 0, 0)
                            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
                            cv2.putText(frame, label + " {0:.1%}".format(confidence), (x, y - 20), font, 3, color, 3)

                            elapsed_time = starting_time - time.time()

                            if elapsed_time <= -10:
                                starting_time = time.time()
                                self.save_detection(frame)

                    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    bytesPerLine = channels * width 
                    convertToQtFormat = QImage(rgbImage.data, width, height, bytesPerLine, QImage.Format_RGB888)
                    p = convertToQtFormat.scaled(1500, 953, Qt.KeepAspectRatio)
                    # p = convertToQtFormat.scaled(854, 480, Qt.KeepAspectRatio)
                    self.changePixmap.emit(p)
        finally:
            cap.release()

    def save_detection(self, frame):
        cv2.imwrite('saved_frame/frame.jpg', frame)
        print('Frame saved')