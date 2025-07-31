"""Flask-based admin dashboard for the AI news video autopilot.

This simple web application provides an administrator login, allows
configuration of the topics to monitor, and exposes a control to run
the autopilot script on demand.  The configuration is stored in a
JSON file (`config.json`) in the project root.  The autopilot
functionality itself is implemented in `autopilot.py`.

To run the development server:

    python app.py

"""

from __future__ import annotations

import json
import os
from typing import Dict, Any, List

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)

import autopilot


app = Flask(__name__)
# In a real application you would set the secret key via an environment
# variable or a configuration file.  For demonstration purposes this
# constant is acceptable.
app.secret_key = "replace_this_with_a_random_secret"

# The location of the configuration file.  If you modify this
# application structure, update the path accordingly.
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_config() -> Dict[str, Any]:
    """Load the JSON configuration from disk.

    Returns
    -------
    dict
        The configuration as a Python dictionary.
    """
    with open(CONFIG_FILE, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save_config(cfg: Dict[str, Any]) -> None:
    """Persist the JSON configuration to disk.

    Parameters
    ----------
    cfg : dict
        The configuration to save.
    """
    with open(CONFIG_FILE, "w", encoding="utf-8") as fh:
        json.dump(cfg, fh, indent=2)


def is_logged_in() -> bool:
    """Check if the current session represents a logged in admin."""
    return session.get("logged_in", False)


@app.route("/")
def index():
    """Redirect visitors to the login page or dashboard depending on session."""
    if is_logged_in():
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Render and process the login form.

    On GET requests, the login page is displayed.  On POST, the
    submitted credentials are validated against the configuration
    file.  Successful authentication sets the session's `logged_in`
    flag.
    """
    cfg = load_config()
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if username == cfg.get("admin_username") and password == cfg.get("admin_password"):
            session["logged_in"] = True
            flash("Logged in successfully.", "success")
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid username or password."
            flash(error, "danger")
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    """Log out the current user and redirect to the login page."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    """Render the dashboard and handle topic updates and autopilot runs.

    The dashboard allows the administrator to add or remove topics and
    trigger the autopilot to produce a new video.  All changes to the
    configuration are persisted back to `config.json`.
    """
    if not is_logged_in():
        return redirect(url_for("login"))
    cfg = load_config()
    topics: List[str] = cfg.get("topics", [])
    # Handle adding a new topic
    if request.method == "POST":
        # Determine which action was triggered
        if request.form.get("action") == "add_topic":
            new_topic = request.form.get("new_topic", "").strip()
            if new_topic:
                topics.append(new_topic)
                cfg["topics"] = topics
                save_config(cfg)
                flash(f"Added topic '{new_topic}'.", "success")
            else:
                flash("Topic cannot be empty.", "danger")
        elif request.form.get("action") == "remove_topic":
            remove_idx_str = request.form.get("remove_index")
            if remove_idx_str and remove_idx_str.isdigit():
                idx = int(remove_idx_str)
                if 0 <= idx < len(topics):
                    removed = topics.pop(idx)
                    cfg["topics"] = topics
                    save_config(cfg)
                    flash(f"Removed topic '{removed}'.", "info")
                else:
                    flash("Invalid topic index.", "danger")
            else:
                flash("No topic selected for removal.", "danger")
        elif request.form.get("action") == "run_autopilot":
            try:
                video_path = autopilot.run_autopilot(topics)
                flash(f"Autopilot completed successfully. Video saved to {video_path}.", "success")
            except Exception as exc:
                flash(f"Autopilot failed: {exc}", "danger")
    # Reload configuration to reflect any changes
    cfg = load_config()
    return render_template("dashboard.html", topics=cfg.get("topics", []))


if __name__ == "__main__":
    # Run the development server.  In production, use a WSGI server like
    # Gunicorn or uWSGI.
    app.run(debug=True)
