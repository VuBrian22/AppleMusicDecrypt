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

if __name__ == '__main__':
    web_server_thread = threading.Thread(target=start_web_server, args=(loop,))
    web_server_thread.daemon = True
    web_server_thread.start()

    cmd = InteractiveShell(loop)
    try:
        loop.run_until_complete(cmd.start())
    except KeyboardInterrupt:
        loop.stop()
