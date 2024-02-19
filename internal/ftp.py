import ftplib
import os
import re
import json
import yaml

from io import BytesIO
from datetime import datetime
from internal.sql import SessionLocal, DownloadedFile
from internal.order import parse_json_to_order
from internal.ascalia import create_order


async def ftp_download_and_delete():
    try:
        ftp = ftplib.FTP("ftp.dlptest.com")
        ftp.login("dlpuser", "rNrKYTX9g7z3RgJRmxWuGHbeu")

        filenames = ftp.nlst("*.json")
        filenames = filter_filenames(filenames, r"GSRNL_\d{5}\.json")
        files = []

        db = SessionLocal()
        try:
            for filename in filenames:
                with BytesIO() as file:
                    ftp.retrbinary(f"RETR {filename}", file.write)
                    file.seek(0)

                    data = yaml.load(file.read().decode("utf-8"), yaml.SafeLoader)
                    order = parse_json_to_order(data)
                    res = create_order(order)
                    print(res)

                    db_file = DownloadedFile(
                        filename=filename, timestamp=datetime.utcnow()
                    )
                    db.add(db_file)

                    print(f"Downloaded: {filename}")
                    ftp.delete(filename)
                    print(f"Deleted: {filename}")

            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Database error occurred: {e}")
        finally:
            db.close()

        ftp.quit()
    except Exception as e:
        print(f"An error occurred: {e}")


async def list_and_upload_json_files():
    local_folder = "data"
    remote_folder = "/ftp-test/"

    # List local .json files
    local_files = [f for f in os.listdir(local_folder) if f.endswith(".json")]

    try:
        ftp = ftplib.FTP("ftp.dlptest.com")
        ftp.login("dlpuser", "rNrKYTX9g7z3RgJRmxWuGHbeu")

        remote_files = ftp.nlst("*.json")
        remote_files = filter_filenames(remote_files, r"GSRNL_\d{5}\.json")

        # Upload files that are missing on the remote server
        for file in local_files:
            if file not in remote_files:
                file_path = os.path.join(local_folder, file)
                with open(file_path, "rb") as file_obj:
                    ftp.storbinary(f"STOR {file}", file_obj)
                print(f"Uploaded: {file}")

        ftp.quit()
    except Exception as e:
        print(f"An error occurred: {e}")


def filter_filenames(filenames, pattern):
    regex = re.compile(pattern)
    return [filename for filename in filenames if regex.match(filename)]
