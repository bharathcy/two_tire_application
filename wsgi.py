import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    # Dev server only — production uses gunicorn (see Dockerfile).
    # Loopback bind + debug off unless explicitly enabled via FLASK_DEBUG=1.
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
