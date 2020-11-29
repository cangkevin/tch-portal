"""
This module contains the API interface of the application.
"""
import logging

from flask import request, jsonify, session
from website import client
from website.core import bp
from website.client.exceptions import InvalidCredentialsError


logger = logging.getLogger(__name__)


@bp.app_errorhandler(InvalidCredentialsError)
def invalid_credentials(error):
    logger.error("Invalid credentials detected")
    return ("", 400)


@bp.route("/schedule", methods=["POST"])
def schedules():
    if "username" in session:
        data = request.get_json()
        schedules = client.get_schedules_for_dates(data["dates"])
        return jsonify(schedules)
    return ("", 303)


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    client.set_credentials(data["username"], data["password"])
    session["username"] = data["username"]
    session.permanent = True
    logger.info("Successfully logged in")

    return ("", 200)
