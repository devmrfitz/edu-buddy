import pymongo
import json
import requests
import os

YOUR_API_KEY = os.environ['AZURE_KEY']
client = pymongo.MongoClient(os.environ['MONGODB_URI'])
db = client['edubuddy']


def transcript(YOUR_AUDIO_FILE):
    results = get_text(audio=YOUR_AUDIO_FILE)
    return results


def get_text(audio):
    # Request that the Bing Speech API convert the audio to text
    url = 'https://eastus.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language=en-IN'
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
    data = {
        'course': course,
        'vid_id': id,
        'transcript': text,
        'start_time': time
    }
    posts.insert_one(data)


if __name__ == '__main__':
    # db.transcript.create_index([("transcript", pymongo.TEXT)])
    print(db.transcript.find_one({"$text": {"$search": "complement"}}))
    # insert_transcript(course='ip', id='1T_oAY8OP4aHcozPRYaejCp6k8UIWwH7z', text=transcript('app/audio.wav'), time='693')
