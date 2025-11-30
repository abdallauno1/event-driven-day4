import pika, json, logging, sys

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}',
    stream=sys.stdout
)

RABBIT_HOST = "rabbitmq"
DLQ_NAME = "notifications.dlq"

def callback(ch, method, properties, body):
    data = json.loads(body)
    logging.error(f"[DLQ] Dead letter received: {data}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    logging.info("DLQ worker started...")
    conn = pika.BlockingConnection(pika.ConnectionParameters(RABBIT_HOST))
    ch = conn.channel()
    ch.basic_consume(queue=DLQ_NAME, on_message_callback=callback)
    ch.start_consuming()

if __name__ == "__main__":
    main()
