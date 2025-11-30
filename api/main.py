from fastapi import FastAPI
from pydantic import BaseModel
import pika, json

app = FastAPI(title="Notification API - Day4")

RABBIT_HOST = "rabbitmq"
QUEUE_NAME = "notifications"

class Notification(BaseModel):
    user_id: str
    channel: str   # email | sms | push
    message: str
    force_fail: bool | None = False

def publish_message(payload: dict):
    conn = pika.BlockingConnection(pika.ConnectionParameters(RABBIT_HOST))
    ch = conn.channel()
    ch.queue_declare(queue=QUEUE_NAME, durable=True)
    ch.basic_publish(exchange="", routing_key=QUEUE_NAME, body=json.dumps(payload))
    conn.close()

@app.post("/notifications")
def send_notification(notification: Notification):
    publish_message(notification.dict())
    return {"status": "queued", "notification": notification}
