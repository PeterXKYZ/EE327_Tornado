from sys import flags
import tornado.web
import tornado.ioloop
import tornado.websocket
import cv2 as cv
import numpy as np

cl_video = []
cl_photo = []

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("video.html")

class videoHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("video WebSocket opened") 
        cl_video.clear()
        
        # append the active client to global variable <cl_video>
        # so it could be accessed by other handlers
        cl_video.append(self)

    def on_message(self, message):
        print(message)
        print(len(cl_photo))

        # everytime a message arrives at this current, it sends
        # passes the message along to another WS client
        for c in cl_photo:
            c.write_message(message)

    def on_close(self):
        print("video WebSocket closed")
        cl_video.remove(self)

    def check_origin(self, origin):
        return True 
    
class photoHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("photo WebSocket opened")
        self.write_message("channel opened") 
        cl_photo.clear()
        cl_photo.append(self)

    def on_message(self, message):
        print(type(message)) 
        for c in cl_video:
            c.write_message(message, True)  # True means to send message as binary

        # https://stackoverflow.com/questions/62348356/decode-image-bytes-data-stream-to-jpeg
        # msg = np.frombuffer(message, dtype=np.uint8)
        # img = cv.imdecode(msg, cv.IMREAD_UNCHANGED)
        # cv.imwrite("test.jpg", img)
        
    def on_close(self):
        print("photo WebSocket closed")
        cl_photo.remove(self)

    def check_origin(self, origin):
        return True  

urls = [
    (r"/", IndexHandler),
    (r"/video", videoHandler),
    (r"/photo", photoHandler),
    # https://stackoverflow.com/questions/32288515/how-to-load-html-image-files-on-the-python-tornado
    (r"/(test.jpg)", tornado.web.StaticFileHandler, {"path": "./"})
]

def main():
    app = tornado.web.Application(urls, autoreload=True)
    app.listen(420)
    print("I'm listening on port 420")
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()