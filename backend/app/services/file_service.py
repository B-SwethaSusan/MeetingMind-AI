from pathlib import Path
import uuid

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


class FileService:

    async def save(self, file):

        filename = f"{uuid.uuid4().hex}_{file.filename}"

        path = UPLOAD_DIR / filename

        with open(path, "wb") as f:
            f.write(await file.read())

        return path