import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from src.cmd import InteractiveShell
import uvicorn

app = FastAPI()
shell = None

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

class DownloadRequest(BaseModel):
    url: str

@app.post("/api/download")
async def download(request: DownloadRequest):
    command = f"dl {request.url}"
    asyncio.run_coroutine_threadsafe(shell.execute_command(command), shell.loop)
    return {"message": "Download started"}

def start_web_server(main_loop: asyncio.AbstractEventLoop, shell_instance: InteractiveShell):
    global shell
    shell = shell_instance
    uvicorn.run(app, host="0.0.0.0", port=8000)
