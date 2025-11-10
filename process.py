#!/usr/bin/env python
import pika, sys, os, yaml, logging, time, random
from pathlib import Path

def main():
    profile = sys.argv[1]

    with open('config.yaml') as f:
        config = yaml.safe_load(f)

    consumeConnection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost', credentials=pika.PlainCredentials(
            username=config[profile]['read_username'],
            password=config[profile]['read_password'])
        )
    )
    consumeChannel = consumeConnection.channel()  

    produceConnection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost', credentials=pika.PlainCredentials(
            username=config[profile]['write_username'],
            password=config[profile]['write_password'])
        )
    )
    produceChannel = produceConnection.channel()  

    logger = logging.getLogger(profile)
    logdir = os.path.dirname(config[profile]['logfile'])
    if not os.path.exists(logdir):
        os.makedirs(logdir)
    logging.basicConfig(filename=config[profile]['logfile'], level=logging.INFO)

    def callback(ch, method, properties, body):
        logger.info(body)
        time.sleep(random.randrange(config[profile]['delay_min'], config[profile]['delay_max']))
        produceChannel.basic_publish(exchange='', routing_key=config[profile]['write_queue'], body=body)

    consumeChannel.basic_consume(queue=config[profile]['read_queue'], on_message_callback=callback, auto_ack=True)

    print(f"Processor {profile} consuming {config[profile]['read_queue']} and writing to {config[profile]['write_queue']}")
    consumeChannel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
