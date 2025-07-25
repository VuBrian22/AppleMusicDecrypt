import asyncio
import pathlib
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
    command = f"dl {request.url}"
    asyncio.run_coroutine_threadsafe(shell.execute_command(command), shell.loop)
    return {"message": "Download started"}

@app.get("/")
async def read_index(request: Request):
    static_path = request.app.state.static_path
    return FileResponse(static_path / 'index.html')

def start_web_server(main_loop: asyncio.AbstractEventLoop, shell_instance: InteractiveShell, static_path: pathlib.Path):
    app.state.shell = shell_instance
    app.state.static_path = static_path
    app.state.loop = main_loop
    
    app.mount("/static", StaticFiles(directory=static_path), name="static")

    uvicorn.run(app, host="0.0.0.0", port=8000)
