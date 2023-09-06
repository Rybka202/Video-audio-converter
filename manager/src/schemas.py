from pydantic import BaseModel

class FileCreate(BaseModel):
    fileName: str
    convertedFileName: str