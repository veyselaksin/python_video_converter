import pika, json

def upload(fs, file, channel, access):
    try:
        if not file.filename:
            return {"message": "File is missing"}, 400
        
        file_id = fs.put(file)
        
        channel.basic_publish(
            exchange="",
            routing_key="upload",
            body=json.dumps({
                "file_id": str(file_id),
                "user_id": access["user_id"]
            }),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )
        
        return None
    except Exception as e:
        fs.delete(file_id)
        return {"message": str(e)}, 500