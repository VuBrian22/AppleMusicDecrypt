import asyncio
import os
import pathlib
import queue
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from src.cmd import InteractiveShell
import uvicorn

app = FastAPI()

class DownloadRequest(BaseModel):
    url: str

@app.post("/api/download")
async def download(request: DownloadRequest, app_request: Request):
    shell = app_request.app.state.shell
    q = queue.Queue()
    command = f"dl {request.url}"
    asyncio.run_coroutine_threadsafe(shell.execute_command(command, q), shell.loop)
    
    try:
        filename = q.get(timeout=300) # 5 minute timeout
        return {"message": "Download complete", "filename": str(filename)}
    except queue.Empty:
        return {"message": "Download timed out"}


@app.get("/")
async def read_index(request: Request):
    static_path = request.app.state.static_path
    return FileResponse(static_path / 'index.html')

@app.get("/api/download-file")
async def download_file(filename: str):
    file_path = pathlib.Path(filename).resolve()
    try:
        return FileResponse(file_path, media_type='application/octet-stream', filename=file_path.name)
    finally:
        # Delete the file after sending it
        try:
            os.remove(file_path)
        except OSError as e:
            print(f"Error deleting file {file_path}: {e}")

def start_web_server(main_loop: asyncio.AbstractEventLoop, shell_instance: InteractiveShell, static_path: pathlib.Path):
    app.state.shell = shell_instance
    app.state.static_path = static_path
    app.state.loop = main_loop
    
    app.mount("/static", StaticFiles(directory=static_path), name="static")

    uvicorn.run(app, host="0.0.0.0", port=8000)
