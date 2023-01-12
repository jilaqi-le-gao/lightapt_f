__version__ = "1.6.1"
__author__ = 'Shengdun Hua <webmaster0115@gmail.com>'
__modified__ = "Max Qian <astro_air@126.com>"

import sys
# Check if the system is windows , if true then change asyncio settings
if sys.platform == 'win32' and sys.version_info.major == 3 and \
        sys.version_info.minor >= 8:
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
