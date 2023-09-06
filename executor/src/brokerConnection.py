import pika
import traceback, sys


msg: str = ""
def get_msg():
    global msg
    return msg

def clear_msg():
    global msg
    msg = ""

def get_message():
    conn_param = pika.ConnectionParameters('rabbitmq', 5672, virtual_host='/', credentials=pika.credentials.PlainCredentials('guest', 'guest'))
    connection = pika.BlockingConnection(conn_param)
    channel = connection.channel()

    queue_info = channel.queue_declare(queue='unprocessed_queue')

    def callback(ch, method, properties, body):
        global msg
        msg = body.decode()
        ch.basic_ack(delivery_tag=method.delivery_tag)
        connection.close()

    channel.basic_consume(on_message_callback=callback, queue='unprocessed_queue')

    try:
        if queue_info.method.message_count != 0:
            channel.start_consuming()
        else:
            connection.close()
    except KeyboardInterrupt:
        channel.stop_consuming()
    except Exception:
        channel.stop_consuming()
        traceback.print_exc(file=sys.stdout)

def send_message(fileName: str):
    conn_param = pika.ConnectionParameters('rabbitmq', 5672, virtual_host='/', credentials=pika.credentials.PlainCredentials('guest', 'guest'))
    connection = pika.BlockingConnection(conn_param)
    channel = connection.channel()
    channel.exchange_declare(exchange='exchange',
                             exchange_type='direct')

    channel.queue_declare(queue='processed_queue')

    channel.queue_bind(exchange='exchange',
                       queue='processed_queue',
                       routing_key='processed')

    channel.basic_publish(exchange='exchange',
                          routing_key='processed',
                          body=fileName)
    connection.close()