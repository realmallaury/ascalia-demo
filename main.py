from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from internal.ftp import ftp_download_and_delete, list_and_upload_json_files
from internal.sql import SessionLocal, DownloadedFile
from internal.schemas import DownloadedFileSchema


app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


scheduler = AsyncIOScheduler()
scheduler.start()


@app.on_event("startup")
def start_scheduler():
    scheduler.add_job(list_and_upload_json_files)
    scheduler.add_job(
        ftp_download_and_delete, trigger=IntervalTrigger(minutes=1), max_instances=1
    )


@app.get("/", response_model=list[DownloadedFileSchema])
async def root(db: Session = Depends(get_db)):
    files = db.query(DownloadedFile).all()
    return files
