from flask import Blueprint, redirect, render_template, request, url_for

from .models import Profile, db

bp = Blueprint("main", __name__)


def get_profile():
    return db.session.get(Profile, 1)


@bp.route("/")
def index():
    """View the profile page."""
    return render_template("index.html", p=get_profile())


@bp.route("/edit", methods=["GET", "POST"])
def edit():
    """Edit form (GET) and update handler (POST)."""
    profile = get_profile()
    if request.method == "POST":
        profile.update_from_form(request.form)
        db.session.commit()
        return redirect(url_for("main.index"))
    return render_template("edit.html", p=profile)


@bp.route("/health")
def health():
    """Liveness/readiness probe for Docker, K8s, and load balancers."""
    return {"status": "ok"}, 200
