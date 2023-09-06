import boto3
from datetime import datetime, timedelta

async def clean_storage(stage: int, id_list: list[str]):
    s3 = boto3.client('s3',
                endpoint_url='http://minio:9000',
                aws_access_key_id='Simon',
                aws_secret_access_key='password')
    delete_id = []
    for id in id_list:
        response = s3.head_object(Bucket='convert-storage', Key=id)
        last_modified = response['LastModified']
        current_time = datetime.now(last_modified.tzinfo)
        time_difference = current_time - last_modified
        if stage == 3 and time_difference > timedelta(minutes=15):
            s3.delete_object(Bucket='convert-storage', Key=id)
            delete_id.append(id)
        if stage == 2 and time_difference > timedelta(minutes=30):
            s3.delete_object(Bucket='convert-storage', Key=id)
            delete_id.append(id)
    s3.close()
    return delete_id