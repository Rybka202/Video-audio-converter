from fastapi import FastAPI
from boto3 import client
import brokerConnection
from converter import converter
import os
import time

app = FastAPI(
    title="Executors"
)

s3 = client('s3',
            endpoint_url='http://minio:9000',
            aws_access_key_id='Simon',
            aws_secret_access_key='password')

@app.get("/startup")
def startup():
    while True:
        brokerConnection.get_message()
        msg = brokerConnection.get_msg()
        if msg != "":
            filename = msg[:msg.index('|')]
            convertedFilename = msg[msg.index('|') + 1:]
            s3.download_file(Bucket='storage', Key=filename, Filename=filename)
            converter(filename, convertedFilename)
            s3.put_object(Bucket='convert-storage', Key=convertedFilename, Body=open(convertedFilename, 'rb'))
            brokerConnection.send_message(filename)
            os.remove(filename)
            os.remove(convertedFilename)
            brokerConnection.clear_msg()
        else:
            time.sleep(5)
