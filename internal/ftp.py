import ftplib
import os
import re
import yaml
import logging
from io import BytesIO
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from internal.sql import SessionLocal, DownloadedFile
from internal.order import parse_json_to_order
from internal.ascalia import create_order

logger = logging.getLogger(__name__)

FTP_HOST = os.getenv("FTP_HOST", "ftp.dlptest.com")
FTP_USER = os.getenv("FTP_USER", "dlpuser")
FTP_PASS = os.getenv("FTP_PASS", "rNrKYTX9g7z3RgJRmxWuGHbeu")


async def download_and_process():
    try:
        with ftplib.FTP(FTP_HOST) as ftp:
            ftp.login(FTP_USER, FTP_PASS)

            filenames = ftp.nlst("*.json")
            filtered_filenames = filter_filenames(filenames, r"GSRNL_\d{5}\.json")

            db = SessionLocal()
            try:
                for filename in filtered_filenames:
                    with BytesIO() as file:
                        ftp.retrbinary(f"RETR {filename}", file.write)
                        file.seek(0)

                        data = yaml.safe_load(file.read().decode("utf-8"))
                        order = parse_json_to_order(data)
                        create_order(order)

                        db_file = DownloadedFile(
                            filename=filename, timestamp=datetime.utcnow()
                        )
                        db.add(db_file)
                        ftp.delete(filename)
                db.commit()
            except SQLAlchemyError as e:
                db.rollback()
                logger.error(f"Database error occurred: {e}")
            finally:
                db.close()
    except ftplib.all_errors as e:
        logger.error(f"FTP error occurred: {e}")


async def list_and_upload_json_files():
    local_folder = "data"
    try:
        local_files = [f for f in os.listdir(local_folder) if f.endswith(".json")]
    except Exception as e:
        logger.error(f"Error reading local files: {e}")
        return

    try:
        with ftplib.FTP(FTP_HOST) as ftp:
            ftp.login(FTP_USER, FTP_PASS)
            remote_files = ftp.nlst("*.json")
            remote_files = filter_filenames(remote_files, r"GSRNL_\d{5}\.json")

            for file in local_files:
                if file not in remote_files:
                    file_path = os.path.join(local_folder, file)
                    with open(file_path, "rb") as file_obj:
                        ftp.storbinary(f"STOR {file}", file_obj)
                    logger.info(f"Uploaded: {file}")
    except ftplib.all_errors as e:
        logger.error(f"FTP error occurred during upload: {e}")


def filter_filenames(filenames, pattern):
    regex = re.compile(pattern)
    return [filename for filename in filenames if regex.match(filename)]
