from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Profile(db.Model):
    """The single editable DevOps profile (row id = 1)."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(160), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    about = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(120))
    email = db.Column(db.String(120))
    github = db.Column(db.String(200))
    linkedin = db.Column(db.String(200))
    years_experience = db.Column(db.String(20))
    pipelines = db.Column(db.String(20))
    uptime = db.Column(db.String(20))
    clusters = db.Column(db.String(20))

    # Fields the edit form is allowed to update
    EDITABLE = (
        "name", "title", "summary", "about", "location", "email",
        "github", "linkedin", "years_experience", "pipelines",
        "uptime", "clusters",
    )

    def update_from_form(self, form):
        for field in self.EDITABLE:
            if field in form:
                setattr(self, field, form.get(field, "").strip())


def seed_profile():
    """Insert a default profile the first time the app starts."""
    if db.session.get(Profile, 1) is not None:
        return
    db.session.add(
        Profile(
            id=1,
            name="Bharath C Y",
            title="Senior DevOps Engineer · Cloud & Automation",
            summary=(
                "I build reliable, automated infrastructure and CI/CD pipelines "
                "that help teams ship faster and sleep better at night."
            ),
            about=(
                "I'm a DevOps Engineer with a passion for automation, "
                "observability, and infrastructure as code. I specialize in "
                "scalable cloud architectures on AWS and Azure, containerizing "
                "workloads with Docker and Kubernetes, and building self-healing "
                "CI/CD pipelines."
            ),
            location="Bengaluru, India",
            email="bharath@example.com",
            github="https://github.com/bharathcy",
            linkedin="#",
            years_experience="8+",
            pipelines="120+",
            uptime="99.9%",
            clusters="40+",
        )
    )
    db.session.commit()
