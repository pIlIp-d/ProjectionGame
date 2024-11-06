import cv2

from threading import Thread
from time import sleep


class WebcamVideoStream:
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        self.grabbed, self.frame = self.stream.read()
        self.stopped = False
        self.thread = Thread(target=self.update, daemon=True, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        while True:
            if self.stopped:
                return
            grabbed, frame = self.stream.read()
            if grabbed:
                self.frame = frame

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
        self.thread.join()
        self.stream.release()


class CameraFrame:
    def __init__(self, *param, **kwargs):
        self.cap = WebcamVideoStream(*param, **kwargs)

    def get_dimensions(self):
        return [
            int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        ]

    def get_image(self):
        frame = self.cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame

    def stop(self):
        # todo properly clean it up (deconstructor maybe called to late)
        self.cap.stop()
