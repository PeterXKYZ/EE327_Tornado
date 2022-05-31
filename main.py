from errno import EALREADY
from multiprocessing.dummy import Array
from sys import flags
from cv2 import log
import tornado.web
import tornado.ioloop
import tornado.websocket
import cv2 as cv
import numpy as np
import sms
import time
import glob, os

cl_web = []
cl_cam = []
cl_esp = []
cam_on = False


def client_write_msg(cl, msg, binary=False):
    for c in cl:
        c.write_message(msg, binary=binary)


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("video.html")  


class WebPageHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("webpage WebSocket opened") 
        cl_web.clear() 
        
        # append the active client to global variable <cl_web>
        # so it could be accessed by other handlers
        cl_web.append(self)

    def on_message(self, message):
        global cam_on
        if message == "on":
            cam_on = True
        elif message == "off":
            cam_on = False
        elif message == "show":
            log_list = os.listdir("img/")
            for img in log_list:
                client_write_msg(cl_web, img)
        elif message == "delete":
            # https://stackoverflow.com/questions/1548704/delete-multiple-files-matching-a-pattern
            for f in glob.glob("img/*.jpg"):
                os.remove(f)

        # everytime a message arrives at the web client, it
        # passes the message along to the cam client
        client_write_msg(cl_cam, message)
            
    def on_close(self):
        print("webpage WebSocket closed")
        cl_web.remove(self) 

    def check_origin(self, origin):
        return True 
    

class CamHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("cam WebSocket opened")
        self.write_message("channel opened") 
        cl_cam.clear()
        cl_cam.append(self)

    def on_message(self, message):
        if message == "button":
            client_write_msg(cl_web, "button")
        
            # when the doorbell button is pressed, send a SMS message
            # to the phone number provided in sms.py
            print("send text?")
            # sms.button_send_text() 

        elif message == "pir":
            client_write_msg(cl_cam, "photo")

            # when the pir sensor is triggered, send a SMS message
            # to the phone number provided in sms.py        
            sms.pir_send_text()    

        else:
            client_write_msg(cl_web, message, True) # True means to send message as binary
            
            global cam_on
            if not cam_on:        
                # https://stackoverflow.com/questions/62348356/decode-image-bytes-data-stream-to-jpeg
                msg = np.frombuffer(message, dtype=np.uint8)
                img = cv.imdecode(msg, cv.IMREAD_UNCHANGED)
                time_epoch = time.time()
                localtime_struct = time.localtime(time_epoch)
                localdate = time.strftime("%Y-%m-%d %H.%M.%S", localtime_struct)
                cv.imwrite(f"img/{localdate}.jpg", img)

        
    def on_close(self):
        print("cam WebSocket closed")
        cl_cam.remove(self)

    def check_origin(self, origin):  
        return True  
 
 
urls = [
    (r"/", IndexHandler),
    (r"/web", WebPageHandler), 
    (r"/cam", CamHandler),
    # https://stackoverflow.com/questions/32288515/how-to-load-html-image-files-on-the-python-tornado
    (r"/resources/(test.jpg)", tornado.web.StaticFileHandler, {"path": "./"}), # used by html page to load a photo
    (r"/resources/(logo.jpg)", tornado.web.StaticFileHandler, {"path": "./"}) # used by html page to load a photo
]

def main():
    app = tornado.web.Application(urls, autoreload=True)
    app.listen(420)
    print("I'm listening on port 420")
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()