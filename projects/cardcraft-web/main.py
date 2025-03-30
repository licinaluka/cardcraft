import uvicorn
from dotenv import load_dotenv

from cardcraft.app.core import asgi_app as flaskapp
from cardcraft.apparatus.apparatus.asgi import application as djangoapp

load_dotenv()


async def dispatch(scope, receive, send):
    default_app = djangoapp
    patterns: dict = {"/game/": flaskapp, "/control": djangoapp}

    app = None

    for _path, _app in patterns.items():
        if not scope["path"].startswith(_path):
            continue

        app = _app
        break

    if app is None:
        app = default_app

    await app(scope, receive, send)


if __name__ == "__main__":
    uvicorn.run(
        app=dispatch,
        # "cardcraft.app.core:asgi_app",
        # debug=True,
        host="0.0.0.0",
        port=3134,
        reload=False,  # never
        reload_dirs="../../bases/cardcraft/app",
    )
