import threading
import speech_recognition as sr
import requests
from datetime import datetime
import base64
import logging
import tempfile
import json
import time


# Parameters
TOTAL_REQUESTS = 65
DURATION = 5
CHECKS = 5
SLEEP_BETWEEN_CHECKS = 8


# Constants
AUDIO_FILE = 'audio.wav'
LANGUAGE = 'en-US'
HOT_WORDS = json.dumps(['to'])
URL = 'http://192.168.182.136:3000/convert'
START = 60

# set up logging
logging.basicConfig(
     filename='info.log',
     level=logging.INFO, 
     format= '[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
     datefmt='%H:%M:%S'
 )
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
logger = logging.getLogger(__name__)


def single_request(idx):
    """
    Send a request to get the transcript.
    """    
    
    recognizer = sr.Recognizer()
    audio_file = sr.AudioFile(AUDIO_FILE)

    with audio_file as source:
        audio = recognizer.record(source, duration=DURATION, offset=START)

    data = {
        'language': LANGUAGE,
        'hot_words': HOT_WORDS,
        'frame_data_base64': base64.b64encode(audio.frame_data),
        'sample_rate': audio.sample_rate,
        'sample_width': audio.sample_width
    }

    logger.debug(f'Sending request {idx}.')
    res = requests.post(URL, data=data)
    logger.debug(f'Recieved response {idx}. Response Code: {res.status_code}. Response Text: {res.text}')
    return res.text

def main():
    times = None
    for _ in range(CHECKS):
        logger.info(f'Starting')
        threads = []

        t0 = datetime.now()
        for idx in range(TOTAL_REQUESTS):
            thread = threading.Thread(target=single_request, args=(idx,))
            thread.start()
            threads.append(thread)

        logger.info(f'Started all threads.')

        # Wait for therads to finish
        [thread.join() for thread in threads]
        t1 = datetime.now()
        if(times is None):
            times = (t1 - t0)
        else:
            times += (t1 - t0)
        logger.info(f'Finished. Time: {(t1-t0).__str__()}')
        time.sleep(SLEEP_BETWEEN_CHECKS)

    logger.info(f'Finished All checks. Total Requests: {TOTAL_REQUESTS}. Duration: {DURATION}. Avergae: {times / CHECKS}')
if __name__ == "__main__":
    main()