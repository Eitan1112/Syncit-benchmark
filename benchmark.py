import threading
import speech_recognition as sr
import requests
from datetime import datetime
import base64
import logging
import tempfile
import json
from flask import Flask,request
import time
import os
from dotenv import load_dotenv

load_dotenv()


# Parameters
CHECKS = 10
SLEEP_BETWEEN_CHECKS = 15


# Constants
AUDIO_FILE = 'audio.wav'
LANGUAGE = 'en-US'
HOT_WORDS = json.dumps(['to'])
URL = 'https://syncit-speech-to-text-dev-ycu3nfdh3q-uc.a.run.app'
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

app = Flask(__name__)


def single_request(idx, duration):
    """
    Send a request to get the transcript.
    """    
    
    recognizer = sr.Recognizer()
    audio_file = sr.AudioFile(AUDIO_FILE)

    with audio_file as source:
        audio = recognizer.record(source, duration=duration, offset=START)

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

@app.route('/', methods=['POST'])
def main():
    total_requests = int(request.form['total_requests'])
    duration = float(request.form['duration'])
    times = None
    for _ in range(CHECKS):
        logger.info(f'Starting')
        threads = []

        t0 = datetime.now()
        for idx in range(total_requests):
            thread = threading.Thread(target=single_request, args=(idx,duration))
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

    logger.info(f'Finished All checks. Total Requests: {total_requests}. Duration: {duration}. Avergae: {times / CHECKS}')
    return f'Finished All checks. Total Requests: {total_requests}. Duration: {duration}. Avergae: {times / CHECKS}'
    
if(__name__ == '__main__'):
    app.run('0.0.0.0', debug=True)