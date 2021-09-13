import subprocess
from queue import Queue
def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
file_handler = logging.FileHandler('gpio.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

GPIOOUT = [65, 68, 70, 71, 72, 73, 74, 76]
GPIOIN = [111, 112, 113, 114, 229, 117, 118, 75]
INPIN = { 111 : 1, 112 : 2, 113 : 3, 114 : 4, 229 : 5, 117 : 6, 118 : 7, 75 : 8 }
OUTPIN = { 1 : 65, 2: 68 , 3 : 70, 4 : 71, 5 : 72, 6 : 73, 7 : 74, 8 : 76 }

async def GPIOOUT_FUNC(outArray):
    pinLoc = 1
    for i in outArray:
        outCommand = f"echo {i} > /sys/class/gpio/gpio{OUTPIN[pinLoc]}/value"
        subprocess.getoutput(outCommand)
        pinLoc +=1

async def GPIOThread(exitSig, INQueue):
    while exitSig:
        for i in GPIOIN:
            inCommand = f"cat /sys/class/gpio/gpio{i}/value"
            if str2bool(subprocess.getoutput(inCommand)):
                INQueue.put(INPIN[i])