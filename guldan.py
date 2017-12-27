# -*- coding: utf-8 -*-
from app import app, init, load_app_config
from app.serving import GuldanRequestHandler

import os
current_dir = os.path.dirname(os.path.abspath(__file__))
extra_dirs = [
    os.path.join(current_dir, "app/templates")
]

extra_files = extra_dirs[:]
for extra_dir in extra_dirs:
    for dirname, dirs, files in os.walk(extra_dir):
        for filename in files:
            filename = os.path.join(dirname, filename)
            if os.path.isfile(filename):
                extra_files.append(filename)


if __name__ == "__main__":
    init()
    print app.url_map
    app.run(
        host='0.0.0.0',
        port=load_app_config().LISTENING_PORT,
        extra_files=extra_files,
        request_handler=GuldanRequestHandler
    )

