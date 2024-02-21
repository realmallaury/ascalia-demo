import logging
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from internal.ftp import download_and_process, list_and_upload_json_files
from internal.sql import SessionLocal, DownloadedFile
from internal.schemas import DownloadedFileSchema

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

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
    logger.info("Starting scheduler...")
    try:
        scheduler.add_job(list_and_upload_json_files)
        scheduler.add_job(
            download_and_process, trigger=IntervalTrigger(minutes=1), max_instances=1
        )
    except Exception as e:
        logger.error(f"Failed to start scheduler jobs: {e}")
    logger.info("Scheduler started.")


@app.get("/", response_model=list[DownloadedFileSchema])
async def root(db: Session = Depends(get_db)):
    try:
        files = db.query(DownloadedFile).all()
        return files
    except Exception as e:
        logger.error(f"Failed to fetch files: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
