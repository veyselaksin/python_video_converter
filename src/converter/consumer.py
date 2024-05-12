import pika, sys, os, time
from pymongo import MongoClient
from gridfs import GridFS
from convert import to_mp3

def main():
    client = MongoClient(os.environ['MONGO_URI'], 27017)
    db_videos = client.videos
    db_mp3s = client.mp3s

    fs_videos = GridFS(db_videos)
    fs_mp3s = GridFS(db_mp3s)

    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()

    def callback(ch, method, properties, body):
        err = to_mp3.start(body, fs_videos, fs_mp3s, ch)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=os.environ["VIDEO_QUEUE"], on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')

    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)