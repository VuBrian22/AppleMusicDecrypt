import asyncio
import os
import pathlib
import shutil
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from src.download_manager import DownloadManager
import uvicorn

app = FastAPI()
download_manager = DownloadManager()

class DownloadRequest(BaseModel):
    url: str

@app.post("/api/download")
async def download(request: DownloadRequest):
    session_id = download_manager.create_session()
    asyncio.create_task(download_manager.start_download(session_id, request.url))
    return {"session_id": session_id}

@app.get("/api/status/{session_id}")
async def get_status(session_id: str):
    session = download_manager.get_session(session_id)
    if not session:
        return {"status": "not_found"}
    return session

@app.get("/")
async def read_index(request: Request):
    static_path = request.app.state.static_path
    return FileResponse(static_path / 'index.html')

@app.get("/api/download-file")
async def download_file(filename: str, background_tasks: BackgroundTasks):
    file_path = pathlib.Path(filename).resolve()
    
    def cleanup():
        import time
        time.sleep(15) # 15 second delay
        try:
            shutil.rmtree(file_path.parent)
        except OSError as e:
            print(f"Error deleting directory {file_path.parent}: {e}")

    background_tasks.add_task(cleanup)
    return FileResponse(file_path, media_type='application/zip', filename=file_path.name)

def start_web_server(main_loop: asyncio.AbstractEventLoop, static_path: pathlib.Path):
    app.state.static_path = static_path
    app.state.loop = main_loop
    
    app.mount("/static", StaticFiles(directory=static_path), name="static")

    uvicorn.run(app, host="0.0.0.0", port=8000)
