import asyncio
import pathlib
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from src.cmd import InteractiveShell
import uvicorn

app = FastAPI()
shell = None
static_path_global = None

class DownloadRequest(BaseModel):
    url: str

@app.post("/api/download")
async def download(request: DownloadRequest):
    command = f"dl {request.url}"
    asyncio.run_coroutine_threadsafe(shell.execute_command(command), shell.loop)
    return {"message": "Download started"}

def start_web_server(main_loop: asyncio.AbstractEventLoop, shell_instance: InteractiveShell, static_path: pathlib.Path):
    global shell, static_path_global
    shell = shell_instance
    static_path_global = static_path
    
    app.mount("/static", StaticFiles(directory=static_path_global), name="static")

    @app.get("/")
    async def read_index():
        return FileResponse(static_path_global / 'index.html')

    uvicorn.run(app, host="0.0.0.0", port=8000)
