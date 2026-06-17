import os

from flask import Flask

from .models import db, seed_profile


def create_app(config=None):
    """Application factory — builds and configures the Flask app."""
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    # Data tier: Postgres in production, SQLite fallback for local/dev.
    db_url = os.environ.get("DATABASE_URL", "sqlite:///profile.db")
    # SQLAlchemy needs the postgresql:// scheme, not the legacy postgres://
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url.replace(
        "postgres://", "postgresql://", 1
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if config:
        app.config.update(config)

    db.init_app(app)

    from .routes import bp

    app.register_blueprint(bp)

    with app.app_context():
        db.create_all()
        seed_profile()

    return app
