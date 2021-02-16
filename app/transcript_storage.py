import pymongo
import json
import requests
import os
from pydub import AudioSegment

YOUR_API_KEY = os.environ['AZURE_KEY']
client = pymongo.MongoClient(os.environ['MONGODB_URI'])
db = client['edubuddy']


def transcript(YOUR_AUDIO_FILE):
    results = get_text(audio=YOUR_AUDIO_FILE)
    return results


def get_text(audio):
    # Request that the Bing Speech API convert the audio to text
    url = 'https://eastus.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language=en-US'
    headers = {
        'Ocp-Apim-Subscription-Key': YOUR_API_KEY,
        'Content-type': 'audio/wav',
    }
    r = requests.post(url, headers=headers, data=stream_audio_file(audio))
    results = json.loads(r.content)
    return results["DisplayText"]


def stream_audio_file(speech_file, chunk_size=1024):
    # Chunk audio file
    with open(speech_file, 'rb') as f:
        while 1:
            data = f.read(1024)
            if not data:
                break
            yield data


def insert_transcript(course, id, text, time):
    posts = db.transcript
    print(text)
    data = {
        'course': course,
        'vid_id': id,
        'transcript': text,
        'start_time': time
    }
    posts.insert_one(data)


def create_file(filename, start_time):
    t1 = start_time * 1000
    t2 = (start_time + 18) * 1000
    newAudio = AudioSegment.from_wav(filename)
    newAudio = newAudio[t1:t2]
    newAudio.export('app/audio.wav', format="wav")


if __name__ == '__main__':
    time = 693 #860
    # create_file(filename="app/orig.wav", start_time=time)
    insert_transcript(course='ip', id='1T_oAY8OP4aHcozPRYaejCp6k8UIWwH7z', text=transcript('app/audio.wav'), time=time)
