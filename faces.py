#-*-coding:utf-8-*-
import face_recognition
import cv2
import numpy as np
import os
import datetime
import string
import paramiko
import urllib.request


def CatchPICFromVideo():
     
    #视频来源，可以来自一段已存好的视频，也可以直接来自USB摄像头
    cap = cv2.VideoCapture(0)

    #告诉OpenCV使用人脸识别分类器
    classfier = cv2.CascadeClassifier("/home/pi/face/haarcascade_frontalface_alt.xml")

    #识别出人脸后要画的边框的颜色，RGB格式, color是一个不可增删的数组
    color = (0, 255, 0)

    
    while cap.isOpened():
        ok, frame = cap.read() #读取一帧数据
        if not ok:
            break

        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  #将当前桢图像转换成灰度图像
        
        

        #人脸检测，1.2和2分别为图片缩放比例和需要检测的有效点数
        faceRects = classfier.detectMultiScale(grey, scaleFactor = 1.2, minNeighbors = 3, minSize = (32, 32))
        if len(faceRects) > 0:          #大于0则检测到人脸
            for faceRect in faceRects:  #单独框出每一张人脸
                x, y, w, h = faceRect
                rgb_frame = frame[:, :, ::-1]
                image = rgb_frame[y - 10: y + h + 10, x - 10: x + w + 10]
                face_locations = face_recognition.face_locations(image )
                face_encoding = face_recognition.face_encodings(image, face_locations)
                #找到本地noknow_people文件夹下所有的人脸
                know_people_list = [i for i in os.listdir('/home/pi/face/noknow_people') if (i.endswith('.jpg'))]
                known_face_encodings = []
                for know_people in know_people_list:
                    konw_image = face_recognition.load_image_file('/home/pi/face/noknow_people/' + know_people)
                    know_face_encoding = face_recognition.face_encodings(konw_image)[0]
                    known_face_encodings.append(know_face_encoding)
                '''
                这里有一个问题,noknow_people文件夹里面的人脸也是通过下面的代码截图保存的，当下一次检测到人脸后和noknow_people
                文件夹中的人脸使用face_recognition.compare_faces对比时，会出现明明是两个不同的人脸对比的结果是True
                '''
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                if True not in matches:
                    now = datetime.datetime.now()
                    strtime = "csmd_" + now.strftime("%Y%m%d%H%M%S") + ".jpg"  # 图片名字，格式为门店编码+时间戳
                    cv2.imwrite('%s/%s' % ("/home/pi/face/noknow_people", strtime), image)  # 保存人脸

                    # 将人脸图片上传到服务器临时文件夹noknow_img
                    img_path = '/home/pi/face/noknow_people/' + strtime  # 本地图片路径
                    remote_ip = '39.108.65.xxx'
                    remote_ssh_port = 22
                    ssh_password = 'yyh'
                    ssh_username = 'root'
                    # 创建sftp连接
                    t = paramiko.Transport((remote_ip, remote_ssh_port))
                    t.connect(username=ssh_username, password=ssh_password)
                    sftp = paramiko.SFTPClient.from_transport(t)
                    # 执行上传sftp
                    sftp.put(img_path, '/home/noknow_img/' + strtime)
                    # 关闭sftp连接
                    t.close()
                    urllib.request.urlopen('http://39.108.65.xxx:8868/add?name=' + strtime) #调用服务器上的python接口
        #显示图像
        cv2.imshow('Video', frame)
        c = cv2.waitKey(10)
        if c & 0xFF == ord('q'):
            break

     #释放摄像头并销毁所有窗口
    cap.release()
    cv2.destroyAllWindows()
if __name__ == '__main__':
    CatchPICFromVideo()

