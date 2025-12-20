#!/usr/bin/env python

import pika, sys, os, yaml, time, random, json
from dotenv import load_dotenv

load_dotenv()

def main():
    profile = None
    if len(sys.argv) > 1:
        profile = sys.argv[1]
    if profile is None and os.getenv('processing_profile') is not None:
        profile = os.getenv('processing_profile')
    if profile is None:
        print("Please set either processing_profile environment variable or provide the profile name as the second argument", flush=True)
        exit(1)
    
    rabbitmq_username = os.getenv('rabbitmq_username')
    rabbitmq_password = os.getenv('rabbitmq_password')
    if not rabbitmq_password or not rabbitmq_username:
        print("Please set rabbitmq_username and rabbitmq_password env vars", flush=True)
        exit(1)

    print("profile: " + profile, flush=True)
    print("rabbitmq host: " + os.getenv('rabbitmq_host'), flush=True)
    print("rabbitmq port: " + os.getenv('rabbitmq_port'), flush=True)
    print("rabbitmq user: " + os.getenv('rabbitmq_username'), flush=True)

    with open('config.yaml') as f:
        config = yaml.safe_load(f)

    do_read  = str(config[profile]['read_queue']) != -1
    do_write = profile != "delivery"

    print("[x] Creating rabbitmq connections using given credentials...", flush=True)

    pikaConnection = pika.BlockingConnection(pika.ConnectionParameters(
        host=os.getenv('rabbitmq_host'),
        port=os.getenv('rabbitmq_port'),
        credentials=pika.PlainCredentials(username=rabbitmq_username, password=rabbitmq_password)
    ))
    channel = pikaConnection.channel()  

    def consumer_callback(ch: pika.channel.Channel, method: pika.spec.Basic.Deliver, properties: pika.spec.BasicProperties, consumedObjectBody: bytes):
        jsonStr = consumedObjectBody.decode().replace("'", '"')
        print("Received string: " + jsonStr, flush=True)
        jsonObj = json.loads(jsonStr)

        time.sleep(random.randrange(config[profile]['start_delay_min'], config[profile]['start_delay_max']))

        statusStr = json.dumps({ "id" : jsonObj["id"], "status": config[profile]['started_status'] })
        print("Writing string: " + statusStr, flush=True)
        channel.basic_publish(exchange=config['common']['status_exchange'], routing_key=config['common']['status_routing_key'], body=statusStr)

        time.sleep(random.randrange(config[profile]['delay_min'], config[profile]['delay_max']))

        if do_write:
            channel.basic_publish(exchange=config[profile]['write_exchange'], routing_key=config[profile]['write_routing_key'], body=consumedObjectBody)

        statusStr = json.dumps({ "id" : jsonObj["id"], "status": config[profile]['finished_status'] })
        print("Writing string: " + statusStr, flush=True)
        channel.basic_publish(exchange=config['common']['status_exchange'], routing_key=config['common']['status_routing_key'], body=statusStr)

    channel.basic_consume(queue=config[profile]['read_queue'], on_message_callback=consumer_callback, auto_ack=True)
    print(f"[x] Processor {profile} consuming {config[profile]['read_queue']} and writing to {config[profile]['write_exchange']} and {config['common']['status_exchange']}", flush=True)
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
