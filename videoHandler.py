from video import VlcPlayer
import queue
from vlc import EventType
import logging
from gpioHandler import GPIOOUT_FUNC
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
file_handler = logging.FileHandler('video.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class Media:
    def __init__(self, orderNumber, mediaData, gpio=[0,0,0,0,0,0,0,0]):
        self.order = orderNumber
        self.data = mediaData
        self.gpio = gpio

    def __lt__(self,other): 
        return self.order < other.order #객체의 name을 비교한다!


def videoEndHandler(event):
    global videoEnd
    videoEnd = True

def videoThread(exitSig, videoQ):
    player = VlcPlayer('--mouse-hide-timeout=0')
    player.add_callback(EventType.MediaPlayerEndReached,videoEndHandler)
    videoEnd = False
    media = "blackscreen.mp4"
    while exitSig:
        if videoEnd:
            try :
                media = videoQ.get_nowait()
            except queue.Empty:
                media = Media(3, "blackscreen.mp4")
            player.play(media.data)
            GPIOOUT_FUNC(media.gpio)
            videoEnd = False
        else:
            pass