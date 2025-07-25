import asyncio
import logging
import sys

from creart import add_creator

if sys.platform in ('win32', 'cygwin', 'cli'):
    import winloop

    winloop.install()
else:
    import uvloop

    uvloop.install()
loop = asyncio.new_event_loop()

from src.logger import LoggerCreator
add_creator(LoggerCreator)
from src.config import ConfigCreator
add_creator(ConfigCreator)
from src.api import APICreator
add_creator(APICreator)
from src.grpc.manager import WMCreator
add_creator(WMCreator)
from src.measurer import MeasurerCreator
add_creator(MeasurerCreator)

from src.cmd import InteractiveShell
from src.web_api import start_web_server
import threading
import pathlib

if __name__ == '__main__':
    cmd = InteractiveShell(loop)
    
    # Ensure the static directory and index.html exist before starting the server
    static_path = pathlib.Path(__file__).parent.resolve() / "static"
    static_path.mkdir(exist_ok=True)
    
    index_html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Apple Music Downloader</title>
    <link rel="stylesheet" href="/static/styles.css">
</head>
<body>
    <div class="downloader-container">
        <h1>Apple Music Downloader</h1>
        <p>Download songs, albums, and playlists from Apple Music.</p>
        <div class="input-container">
            <input type="text" id="apple-music-url" placeholder="Paste your link here">
            <button onclick="download()">Download</button>
        </div>
        <p id="status"></p>
        <div id="download-links"></div>
    </div>

    <script>
        async function download() {
            const url = document.getElementById('apple-music-url').value;
            const status = document.getElementById('status');
            const downloadLinks = document.getElementById('download-links');

            status.textContent = 'Starting download...';
            downloadLinks.innerHTML = '';

            const response = await fetch('/api/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url }),
            });

            const result = await response.json();

            if (response.ok && result.filenames) {
                status.textContent = result.message;
                for (const filename of result.filenames) {
                    const link = document.createElement('a');
                    link.href = `/api/download-file?filename=${encodeURIComponent(filename)}`;
                    link.textContent = filename.split(/[\\/]/).pop();
                    link.style.display = 'block';
                    downloadLinks.appendChild(link);
                }
            } else {
                status.textContent = 'Error: ' + (result.message || 'Unknown error');
            }
        }
    </script>
</body>
</html>
"""
    (static_path / "index.html").write_text(index_html_content)

    styles_css_content = """
body {
    background: linear-gradient(to right, #8e2de2, #4a00e0);
    color: white;
    font-family: sans-serif;
    text-align: center;
    padding-top: 50px;
}

h1 {
    font-size: 3em;
    margin-bottom: 0;
}

p {
    font-size: 1.2em;
    margin-top: 0;
}

.downloader-container {
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    padding: 40px;
    width: 60%;
    margin: 50px auto;
}

.input-container {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 30px;
}

#apple-music-url {
    width: 70%;
    padding: 15px;
    border: none;
    border-radius: 10px 0 0 10px;
    font-size: 1em;
}

button {
    padding: 15px 30px;
    border: none;
    background-color: #00c853;
    color: white;
    font-size: 1em;
    border-radius: 0 10px 10px 0;
    cursor: pointer;
}

#download-link {
    display: block;
    margin-top: 20px;
    color: #00c853;
    font-size: 1.2em;
    text-decoration: none;
}
"""
    (static_path / "styles.css").write_text(styles_css_content)

    web_server_thread = threading.Thread(target=start_web_server, args=(loop, cmd, static_path))
    web_server_thread.daemon = True
    web_server_thread.start()

    try:
        loop.run_until_complete(cmd.start())
    except KeyboardInterrupt:
        loop.stop()
