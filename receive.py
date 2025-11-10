#!/usr/bin/env python
import pika, sys, os

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=pika.PlainCredentials(username='consumer', password='consumer')))
    channel = connection.channel()

    inputQueue = sys.argv[1]
    
    def callback(ch, method, properties, body):
        print(f" [x] Received {body}")

    channel.basic_consume(queue=inputQueue, on_message_callback=callback, auto_ack=True)

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
