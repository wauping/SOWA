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

   
def adjust_gamma(image, gamma):
        invGamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** invGamma) * 255
        for i in np.arange(0, 256)]).astype("uint8")
        return cv2.LUT(image, table) 


class Detection(QThread):
    changePixmap = pyqtSignal(QImage)

    def __init__(self):
        super().__init__()


    def run(self):
        self.running = True
        net = cv2.dnn.readNet("weights/best_3.onnx", "cfg/yolov8.yaml") 

        layer_names = net.getLayerNames()
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

        starting_time = time.time()
        
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 0)
        if not cap.isOpened():
            print('Camera is not available')
            exit()

        while self.running:
            ret, frame = cap.read()
            if ret:
                gamma_corrected = adjust_gamma(frame, gamma=1.0)
                
                img_yuv = cv2.cvtColor(gamma_corrected, cv2.COLOR_BGR2YUV)
                img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
                corrected_frame = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
                
                blob = cv2.dnn.blobFromImage(corrected_frame, 0.00392, (640, 640), (0, 0, 0), True, crop=False)
                net.setInput(blob)
                outs = net.forward(output_layers)
                boxes = []
                confidences = []
                for i in range(outs[0][0][0].shape[0]):
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
                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))

                indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.8, 0.3)
                
                for i in range(len(boxes)):
                    if i in indexes:
                        x, y, w, h = boxes[i]
                        confidence = confidences[i]
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 119, 0), 1)
                        cv2.putText(frame, 'pistol' + " {0:.1%}".format(confidence), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 119, 0), 1)
                        elapsed_time = starting_time - time.time()
                        if elapsed_time <= -10:
                            starting_time = time.time()
                            self.save_detection(frame) 

                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(640, 640, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)

            time.sleep(0.1)
        cap.release()
        cv2.destroyAllWindows()
    
    def save_detection(self, frame):
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
            filename = f'E:\\UNIVERSITY\\DIPLOM\\SOWA\\web\\project\\media\\frame-{new_alert_id}.jpg'
            frame_name = f'frame-{new_alert_id}.jpg'
        else:
            filename = f'E:\\UNIVERSITY\\DIPLOM\\SOWA\\web\\project\\media\\frame-1.jpg'
            frame_name = 'frame-1.jpg'

        cv2.imwrite(filename, frame)
        print(f'Frame saved as {frame_name}')
        self.post_detection(filename)

    def post_detection(self, image_path):
        
        try:
            with open(image_path, 'rb') as file:
                files = {'file': file}
                
                upload_image = requests.post('http://punchclub.ru:8080/', files=files)
                print(upload_image.text)

            url = 'http://localhost:1337/alerts'
            data = {"user_id": login_window.sesh['user_id'],
                    "location": login_window.sesh['location'],
                    "image": upload_image.text}
            try:
                response = requests.post(url, data=data)
            except requests.exceptions.ConnectionError as e:
                response = "No response"
            print(data)
            # HTTP 200
            if response.ok:
                print('Alert was sent to the server')
                login_window.smtpObj.sendmail("sowa.notification@gmail.com", login_window.sesh['user_email'], 
                              f" {login_window.sesh['username']}! \n\n Система SOWA обнаружила огнестрельное  оружие! \n\n Местоположение: {login_window.sesh['location']}".encode('utf-8'))
            # Bad response
            else:
                print('Unable to send alert to the server') 
        except Exception as e:
            print(e)
            print('Unable to access server')
  