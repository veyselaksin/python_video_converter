import pika, json, tempfile, os
from bson.objectid import ObjectId
import moviepy.editor as mp

def start(body, fs_videos, fs_mp3s, ch):
    try:
        data = json.loads(body)
        video_id = data['video_id']
        video = fs_videos.get(ObjectId(video_id))
        video_path = f'/tmp/{video_id}.mp4'
        with open(video_path, 'wb') as f:
            f.write(video.read())
        video.close()

        mp3_path = f'/tmp/{video_id}.mp3'
        clip = mp.VideoFileClip(video_path)
        clip.audio.write_audiofile(mp3_path)
        clip.close()

        with open(mp3_path, 'rb') as f:
            fs_mp3s.put(f, filename=f'{video_id}.mp3')
        os.remove(video_path)
        os.remove(mp3_path)
        return None
    except Exception as e:
        print(e)
        return e