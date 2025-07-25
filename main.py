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
    <title>Apple Music Decrypt</title>
</head>
<body>
    <h1>Apple Music Decrypt</h1>
    <input type="text" id="apple-music-url" placeholder="Paste Apple Music URL here" size="100">
    <button onclick="download()">Download</button>
    <p id="status"></p>
    <a id="download-link" style="display:none">Download File</a>

    <script>
        async function download() {
            const url = document.getElementById('apple-music-url').value;
            const status = document.getElementById('status');
            const downloadLink = document.getElementById('download-link');

            status.textContent = 'Starting download...';
            downloadLink.style.display = 'none';

            const response = await fetch('/api/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url }),
            });

            const result = await response.json();

            if (response.ok && result.filename) {
                status.textContent = result.message;
                downloadLink.href = `/api/download-file?filename=${encodeURIComponent(result.filename)}`;
                downloadLink.style.display = 'block';
            } else {
                status.textContent = 'Error: ' + (result.message || 'Unknown error');
            }
        }
    </script>
</body>
</html>
"""
    (static_path / "index.html").write_text(index_html_content)

    web_server_thread = threading.Thread(target=start_web_server, args=(loop, cmd, static_path))
    web_server_thread.daemon = True
    web_server_thread.start()

    try:
        loop.run_until_complete(cmd.start())
    except KeyboardInterrupt:
        loop.stop()
