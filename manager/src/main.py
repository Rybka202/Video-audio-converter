from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from boto3 import client
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from sqlalchemy import insert, select, join, update, delete
from models import file as fileTable
from models import stage
from brokerConnection import send_message, get_message, get_msg, clear_msg
from uuid import uuid1
from garbageСollector import clean_storage
from botocore.exceptions import ClientError

app = FastAPI(
    title="Managers"
)

s3 = client('s3',
            endpoint_url='http://minio:9000',
            aws_access_key_id='Simon',
            aws_secret_access_key='password')

video_format = {'avi', 'mov', 'mp4', 'mkv', 'wmv', 'flv'}
audio_format = {'mp3', 'wav', 'flac', 'aac', 'ogg', 'aiff', 'wma', 'alac', 'ac3', 'mid'}

def check_bucket_exists(bucket_name):
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchBucket":
            return False
        else:
            raise
    return True

@app.on_event("startup")
def start():
    if not check_bucket_exists('storage'):
        s3.create_bucket(Bucket='storage')
    if not check_bucket_exists('convert-storage'):
        s3.create_bucket(Bucket='convert-storage')

    return

@app.post("/upload")
async def upload(convertedFormat: str,
                 file: UploadFile = File(...),
                 session: AsyncSession = Depends(get_async_session)):

    if not (file.content_type.startswith('video/') or file.content_type.startswith('audio/')):
        raise HTTPException(status_code=400, detail="Is not a video or audio")
    if not(convertedFormat in video_format or convertedFormat in audio_format):
        raise HTTPException(status_code=400, detail="Converted format is not a video or audio")
    id = str(uuid1())
    filename_id = id + file.filename[file.filename.rindex('.'):]
    convertedFilename_id = id + '.' + convertedFormat
    s3.put_object(Bucket='storage', Key=filename_id, Body=file.file)
    msg = filename_id + '|' + convertedFilename_id
    await send_message(msg)
    stmt = insert(fileTable).values([filename_id, file.filename, convertedFilename_id, 1])
    await session.execute(stmt)
    await session.commit()
    return {"id": filename_id}

@app.get("/update")
async def updateInfo(session: AsyncSession = Depends(get_async_session)):
    await get_message()
    msg_list = get_msg()
    if msg_list != []:
        for id_name in msg_list:
            s3.delete_object(Bucket='storage', Key=id_name)
            stmt = update(fileTable).where(fileTable.c.id == id_name).values(stage=2)
            await session.execute(stmt)
        await session.commit()
        clear_msg()

    query = select(fileTable.c.converted_id).where(fileTable.c.stage == 3)
    result = await session.execute(query)
    delete_id = await clean_storage(3, result.scalars().all().copy())

    query = select(fileTable.c.converted_id).where(fileTable.c.stage == 2)
    result = await session.execute(query)
    delete_id.extend(await clean_storage(2, result.scalars().all().copy()))
    for id_name in delete_id:
        del_query = delete(fileTable).where(fileTable.c.converted_id == id_name)
        await session.execute(del_query)
        await session.commit()
    return "success"

@app.get("/check")
async def checkFile(id: str, session: AsyncSession = Depends(get_async_session)):
    j = join(fileTable, stage, fileTable.c.stage == stage.c.id)
    query = select(stage.c.stepOfDevelopment).select_from(j).where(fileTable.c.id == id)
    result = await session.execute(query)
    return result.scalars().all()

@app.get("/download")
async def download(id: str, session: AsyncSession = Depends(get_async_session)):
    query = select(fileTable).where(fileTable.c.id==id)
    result = await session.execute(query)
    res = []
    for row in result:
        res = list(row).copy()
    if res != [] and res[-1] != 1:
        url = s3.generate_presigned_url('get_object',
                                        Params={'Bucket': 'convert-storage',
                                                'Key': res[2]},
                                        ExpiresIn=60)
        stmt = update(fileTable).where(fileTable.c.id == id).values(stage=3)
        str(url)
        url = url[:7] + "localhost" + url[12:]
        await session.execute(stmt)
        await session.commit()
        return {"Download": url}

    return "File_Not_Found or File_Is_Not_Converted"