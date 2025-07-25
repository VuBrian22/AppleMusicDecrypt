from fastapi import FastAPI
from src.rip import rip_song, rip_album, rip_artist, rip_playlist
from src.url import AppleMusicURL, URLType
from src.flags import Flags
import uvicorn

app = FastAPI()

@app.post("/api/download")
async def download(url: str):
    parsed_url = AppleMusicURL.parse_url(url)
    if not parsed_url:
        return {"error": "Invalid URL"}

    flags = Flags(force_save=True)
    codec = "alac"

    if parsed_url.type == URLType.Song:
        await rip_song(parsed_url, codec, flags)
    elif parsed_url.type == URLType.Album:
        await rip_album(parsed_url, codec, flags)
    elif parsed_url.type == URLType.Artist:
        await rip_artist(parsed_url, codec, flags)
    elif parsed_url.type == URLType.Playlist:
        await rip_playlist(parsed_url, codec, flags)
    else:
        return {"error": "Unsupported URL type"}

    return {"message": "Download started"}

def start_web_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)
