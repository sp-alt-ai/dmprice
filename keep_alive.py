from __future__ import annotations

import os
from threading import Thread

from flask import Flask

app = Flask(__name__)

@app.route('/')
def main():
    return '<meta http-equiv="refresh" content="0; URL=https://phantom.is-a.dev/support"/>'

def run():
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))

    # Flask's built-in server is for development only; use a WSGI server.
    from waitress import serve

    serve(app, host=host, port=port)

def keep_alive():
    server = Thread(target=run)
    server.daemon = True
    server.start()