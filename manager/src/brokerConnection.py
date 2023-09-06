import pika
import sys, traceback

async def send_message(fileName: str):
    conn_param = pika.ConnectionParameters('rabbitmq', 5672, virtual_host='/', credentials=pika.credentials.PlainCredentials('guest', 'guest'))
    connection = pika.BlockingConnection(conn_param)
    channel = connection.channel()
    channel.exchange_declare(exchange='exchange',
                             exchange_type='direct')

    channel.queue_declare(queue='unprocessed_queue')

    channel.queue_bind(exchange='exchange',
                       queue='unprocessed_queue',
                       routing_key='unprocessed')

    channel.basic_publish(exchange='exchange',
                          routing_key='unprocessed',
                          body=fileName)
    connection.close()


msg: list[str] = []

def get_msg():
    global msg
    return msg

def clear_msg():
    global msg
    msg.clear()

async def get_message():
    conn_param = pika.ConnectionParameters('rabbitmq', 5672, virtual_host='/', credentials=pika.credentials.PlainCredentials('guest', 'guest'))
    connection = pika.BlockingConnection(conn_param)
    channel = connection.channel()

    queue_info = channel.queue_declare(queue='processed_queue')

    def callback(ch, method, properties, body):
        msg.append(body.decode())
        ch.basic_ack(delivery_tag=method.delivery_tag)
        queue_info.method.message_count -= 1
        if queue_info.method.message_count == 0:
            connection.close()

    channel.basic_consume(on_message_callback=callback, queue='processed_queue')

    try:
        if queue_info.method.message_count != 0:
            channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    except Exception:
        channel.stop_consuming()
        traceback.print_exc(file=sys.stdout)