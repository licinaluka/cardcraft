import time

from flask import Flask, url_for
from pyhiccup.core import html

app = Flask(__name__, static_url_path="/resources", static_folder="./resources")


@app.route("/")
def landing():
    jsfile = url_for("static", filename="app/bundle.js") + "?t=" + str(int(time.time()))

    return f"""<!DOCTYPE html>
    <head>
    </head>
    <body>
    <div class="container">
    asdasdfasdf
    </div>
    <script src={jsfile} type="module"></script>
    </body>
    </html>
    """