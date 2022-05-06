from sys import flags
import tornado.web
import tornado.ioloop
import tornado.websocket
import cv2 as cv
import numpy as np

cl_web = []
cl_cam = []

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
        print(message)

        # everytime a message arrives at the web client, it
        # passes the message along to the cam client
        for c in cl_cam:
            c.write_message(message)

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
        for c in cl_web:
            c.write_message(message, True)  # True means to send message as binary

        # https://stackoverflow.com/questions/62348356/decode-image-bytes-data-stream-to-jpeg
        # msg = np.frombuffer(message, dtype=np.uint8)
        # img = cv.imdecode(msg, cv.IMREAD_UNCHANGED)
        # cv.imwrite("test.jpg", img)
        
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
    (r"/(test.jpg)", tornado.web.StaticFileHandler, {"path": "./"}) # used by html page to load a photo
]

def main():
    app = tornado.web.Application(urls, autoreload=True)
    app.listen(420)
    print("I'm listening on port 420")
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()