from fastapi import UploadFile


class FileHandler:

    @staticmethod
    async def read_text_file(file: UploadFile) -> str:

        content = await file.read()

        return content.decode("utf-8")