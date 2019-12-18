import tornado.ioloop
import tornado.web
import cv2
import face_recognition
import urllib.request
import numpy as np
import base64
import shutil
import os

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        name = self.get_argument('name')#获取人脸照片名字
        unknown_image = face_recognition.load_image_file('/home/noknow_img/'+name)#树莓派上传上来的人脸图片
        unknown_encoding = face_recognition.face_encodings(unknown_image)[0] #获取未知人脸encod
        #获取文件夹下的所有人脸图片名字
        know_people_list = [i for i in os.listdir('/home/image') if (i.endswith('.jpg'))]
        known_face_encodings = []
        for know_people in know_people_list:
            konw_image = face_recognition.load_image_file('/home/image/' + know_people)
            know_face_encoding = face_recognition.face_encodings(konw_image)[0]
            known_face_encodings.append(know_face_encoding) #将文件夹下的人脸encod存入known_face_encodings
        matches = face_recognition.compare_faces(known_face_encodings, unknown_encoding) #对比人脸
        if True not in matches:
            # 将人脸从服务器临时文件夹noknow_img移动到image中
            shutil.move('/home/noknow_img/'+name, '/home/image')
            #将保存的人脸照片名字作为参数传给java接口
            urllib.request.urlopen('http://39.108.65.144:8090/drty/sendPhoto?imgName='+name)
        else:
            num=matches.index(True) #如果已经存在人脸，就找出此人脸照片的索引
            imgname=know_people_list[num] #找出此人脸照片，获取照片名字
            #调用java接口，将照片名字作为参数
            urllib.request.urlopen('http://39.108.65.144:8090/drty/sendPhoto?imgName='+imgname)
application = tornado.web.Application([(r"/add", MainHandler), ])

if __name__ == "__main__":
    application.listen(8868)
    tornado.ioloop.IOLoop.instance().start()