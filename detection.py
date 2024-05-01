from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QImage
import cv2
import numpy as np
import time, requests, os
import login_window


def clear_frames_directory():
    directory = 'E:\\UNIVERSITY\\DIPLOM\\SOWA\\web\\project\\media'
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")          


class Detection(QThread):
    changePixmap = pyqtSignal(QImage)

    def __init__(self):
        super().__init__()

    def run(self):
        self.running = True
        net = cv2.dnn.readNet("weights/best_3.onnx", "cfg/yolov8.yaml") 

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
                blob = cv2.dnn.blobFromImage(frame, 0.00392, (640, 640), (0, 0, 0), True, crop=False)
                net.setInput(blob)
                outs = net.forward(output_layers)
                for i in range(outs[0][0][0].shape[0]):
                    # print(outs[0][0][0].shape[0])
                    x = outs[0][0][0][i]
                    y = outs[0][0][1][i]
                    w = outs[0][0][2][i]
                    h = outs[0][0][3][i]
                    confidence = outs[0][0][4][i]  
                    

                    if confidence > 0.85:
                        center_x = int(x)
                        center_y = int(y)
                        w = int(w)
                        h = int(h)
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)
                        # boxes.append(w, h, x ,y)
                        # x1 = int((x - w / 2))
                        # y1 = int((y - h / 2))
                        # x2 = int((x + w / 2))
                        # y2 = int((y + h / 2))
                        # boxes.append([x, y, w, h])
                        # confidences.append(float(confidence))
                        # indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.8, 0.3)
                        # for i in range(len(boxes)):
                            # cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
                        cv2.putText(frame, 'pistol' + " {0:.1%}".format(confidence), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 1)
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
        # filename = f'E:\\UNIVERSITY\\DIPLOM\\SOWA\\web\\project\\media\\frame_{login_window.sesh[""]}.jpg'
        url = 'http://localhost:1337/alerts'
        response = requests.get(url)
        if response.ok:
                alerts = response.json()
                print(alerts)
                new_alert_id = None
                for alert in reversed(alerts):
                    if alert['user_id'] == login_window.sesh['user_id']:
                        new_alert_id = alert['id'] + 1
                        break
        if new_alert_id is not None:       
            filename = f'E:\\UNIVERSITY\\DIPLOM\\SOWA\\web\\project\\media\\frame_{new_alert_id}.jpg'
            frame_name = f'frame_{new_alert_id}.jpg'
        else:
            filename = f'E:\\UNIVERSITY\\DIPLOM\\SOWA\\web\\project\\media\\frame_1.jpg'
            frame_name = 'frame_1.jpg'

        cv2.imwrite(filename, frame)
        print(f'Frame saved as {frame_name}')
        self.post_detection(frame_name)

    def post_detection(self, image):
        try:
            url = 'http://localhost:1337/alerts'
            data = {"user_id": login_window.sesh['user_id'],
                    "location": login_window.sesh['location']}
            response = requests.post(url, data=data)
            print(data)
	    	# HTTP 200
            if response.ok:
                print('Alert was sent to the server')
	    	# Bad response
            else:
                print('Unable to send alert to the server') 
        except Exception:
            print('Unable to access server')
  