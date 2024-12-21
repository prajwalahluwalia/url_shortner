from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, abort
from werkzeug.utils import secure_filename
import os
from .models import URL
from . import db

bp = Blueprint("urlshort", __name__)

USER_FILES_DIR = "static/user_files"


@bp.route("/")
def home():
    """Render the home page."""
    codes = [url.code for url in URL.query.all()]
    return render_template("index.html", codes=codes)


@bp.route("/your-url", methods=["GET", "POST"])
def your_url():
    """Handle URL shortening requests."""
    if request.method == "POST":
        code = request.form.get("code")

        if not code or URL.query.filter_by(code=code).first():
            flash("Short name is already taken or invalid. Please choose a new one.")
            return redirect(url_for("urlshort.home"))

        url_entry = URL(code=code)

        if "url" in request.form:
            url_entry.url = request.form["url"]
        elif "file" in request.files:
            file = request.files["file"]
            filename = secure_filename(file.filename)
            if not filename:
                flash("Invalid file. Please upload a valid file.")
                return redirect(url_for("urlshort.home"))
            full_name = f"{code}_{filename}"
            file_path = os.path.join(USER_FILES_DIR, full_name)
            os.makedirs(USER_FILES_DIR, exist_ok=True)
            file.save(file_path)
            url_entry.file_name = full_name
        else:
            flash("No URL or file provided.")
            return redirect(url_for("urlshort.home"))

        # Save to the database
        db.session.add(url_entry)
        db.session.commit()

        session[code] = True
        return render_template("your_url.html", code=code)

    flash("Invalid request.")
    return redirect(url_for("urlshort.home"))


@bp.route("/<string:code>")
def redirect_to_url(code):
    """Redirect to the original URL or serve the uploaded file."""
    url_entry = URL.query.filter_by(code=code).first()

    if url_entry:
        if url_entry.url:
            return redirect(url_entry.url)
        if url_entry.file_name:
            return redirect(url_for("static", filename=f"user_files/{url_entry.file_name}"))

    return abort(404)


@bp.route("/api")
def session_api():
    """Return session data as JSON."""
    return jsonify(list(session.keys()))


@bp.errorhandler(404)
def page_not_found(error):
    """Render a custom 404 page."""
    return render_template("page_not_found.html"), 404
