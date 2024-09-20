import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "cardcraft.app.core:asgi_app",
        # debug=True,
        host="0.0.0.0",
        port=3134,
        reload=True,
        reload_dirs="../../bases/cardcraft/app",
    )
