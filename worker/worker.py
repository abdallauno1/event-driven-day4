import pika, json, time, logging, sys

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}',
    stream=sys.stdout
)

RABBIT_HOST = "rabbitmq"
QUEUE_NAME = "notifications"

def handle_email(msg):
    logging.info(f"[EMAIL] to user={msg['user_id']} message={msg['message']}")

def handle_sms(msg):
    logging.info(f"[SMS] to user={msg['user_id']} message={msg['message']}")

def handle_push(msg):
    logging.info(f"[PUSH] to user={msg['user_id']} message={msg['message']}")

CHANNEL_HANDLERS = {
    "email": handle_email,
    "sms": handle_sms,
    "push": handle_push,
}

def callback(ch, method, properties, body):
    data = json.loads(body)
    try:
        if data.get("force_fail"):
            raise ValueError("Simulated processing error")

        handler = CHANNEL_HANDLERS.get(data["channel"], handle_email)
        handler(data)
        time.sleep(0.5)

        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logging.error(f"Processing error: {e} — requeue")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def main():
    logging.info("Multi-channel worker started...")
    conn = pika.BlockingConnection(pika.ConnectionParameters(RABBIT_HOST))
    ch = conn.channel()
    ch.basic_qos(prefetch_count=1)
    ch.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
    ch.start_consuming()

if __name__ == "__main__":
    main()
