import cv2


class CameraFrame:
    def __init__(self, *param, **kwargs):
        self.cap = cv2.VideoCapture(*param, **kwargs)

    def get_dimensions(self):
        return [
            int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        ]

    def get_image(self):
        if not self.cap.isOpened():
            raise IOError("video finished or camera disconnected")
        success, frame = self.cap.read()
        if not success:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            success, frame = self.cap.read()
            #raise IOError("empty frame")
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame

    def __del__(self):
        # todo properly clean it up (deconstructor maybe called to late)
        self.cap.release()
