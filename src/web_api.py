import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
from src.rip import rip_song, rip_album, rip_artist, rip_playlist
from src.url import AppleMusicURL, URLType
from src.flags import Flags
import uvicorn

app = FastAPI()
loop = None

class DownloadRequest(BaseModel):
    url: str

@app.post("/api/download")
async def download(request: DownloadRequest):
    parsed_url = AppleMusicURL.parse_url(request.url)
    if not parsed_url:
        return {"error": "Invalid URL"}

    flags = Flags(force_save=True)
    codec = "alac"

    if parsed_url.type == URLType.Song:
        asyncio.run_coroutine_threadsafe(rip_song(parsed_url, codec, flags), loop)
    elif parsed_url.type == URLType.Album:
        asyncio.run_coroutine_threadsafe(rip_album(parsed_url, codec, flags), loop)
    elif parsed_url.type == URLType.Artist:
        asyncio.run_coroutine_threadsafe(rip_artist(parsed_url, codec, flags), loop)
    elif parsed_url.type == URLType.Playlist:
        asyncio.run_coroutine_threadsafe(rip_playlist(parsed_url, codec, flags), loop)
    else:
        return {"error": "Unsupported URL type"}

    return {"message": "Download started"}

def start_web_server(main_loop: asyncio.AbstractEventLoop):
    global loop
    loop = main_loop
    uvicorn.run(app, host="0.0.0.0", port=8000)
