from pydantic import BaseModel
from datetime import datetime


class DownloadedFileSchema(BaseModel):
    filename: str
    timestamp: datetime

    class Config:
        orm_mode = True
