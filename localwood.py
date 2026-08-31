import logging
import os
import secrets
import time

from flask import Flask, render_template, request
import RPi.GPIO as GPIO

import socket_setup

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

auth_token = os.environ.get("AUTH_TOKEN")

if not auth_token:
    logging.warning("Proceeding without authentication")

if not any(
    os.environ.get(key)
    for key in [
        "SOCKET_1_LABEL",
        "SOCKET_2_LABEL",
        "SOCKET_3_LABEL",
        "SOCKET_4_LABEL",
    ]
):
    raise ValueError("No power sockets enabled, missing envs e.g. SOCKET_1_LABEL")

app = Flask(__name__)

# (D0, D1, D2, D3) on pins 13, 16, 15, 11 — ENER314 encoder codes
DATA_PINS = (13, 16, 15, 11)
MODULATOR_PIN = 22
SOCKET_CODES = {
    ("all", "on"): ((True, False, True, True), "1011 all sockets on"),
    ("all", "off"): ((False, False, True, True), "0011 all sockets off"),
    ("1", "on"): ((True, True, True, True), "1111 socket 1 on"),
    ("1", "off"): ((False, True, True, True), "0111 socket 1 off"),
    ("2", "on"): ((True, True, True, False), "1110 socket 2 on"),
    ("2", "off"): ((False, True, True, False), "0110 socket 2 off"),
    ("3", "on"): ((True, True, False, True), "1101 socket 3 on"),
    ("3", "off"): ((False, True, False, True), "0101 socket 3 off"),
    ("4", "on"): ((True, True, False, False), "1100 socket 4 on"),
    ("4", "off"): ((False, True, False, False), "0100 socket 4 off"),
}


def authenticate_user():
    if not auth_token:
        return None

    provided = request.values.get("token")
    if provided is None:
        return 'Missing URL param "token"', 400

    if len(provided) != len(auth_token) or not secrets.compare_digest(
        provided, auth_token
    ):
        return "Invalid auth token", 400

    return None


@app.route("/")
def homepage():
    auth_error = authenticate_user()
    if auth_error:
        return auth_error

    return render_template(
        "homepage.html",
        page_title=os.environ.get("PAGE_TITLE", "Localwood Socket Control"),
        page_heading=os.environ.get("PAGE_HEADING", "Socket Control"),
        socket_1_label=os.environ.get("SOCKET_1_LABEL"),
        socket_2_label=os.environ.get("SOCKET_2_LABEL"),
        socket_3_label=os.environ.get("SOCKET_3_LABEL"),
        socket_4_label=os.environ.get("SOCKET_4_LABEL"),
    )


@app.route("/sockets", methods=["POST"])
def sockets():
    auth_error = authenticate_user()
    if auth_error:
        return auth_error

    if "socket" not in request.values:
        return 'Missing URL param "socket"', 400

    if "state" not in request.values:
        return 'Missing URL param "state"', 400

    socket = request.values["socket"]
    state = request.values["state"]
    code = SOCKET_CODES.get((socket, state))
    if code is None:
        logging.info("Unknown combo socket=%s state=%s", socket, state)
        return "Socket or state invalid (expects socket: 1-4 state: on/off)", 400

    bits, description = code
    logging.info("Sending code %s", description)
    for pin, value in zip(DATA_PINS, bits):
        GPIO.output(pin, value)

    # let it settle, encoder requires this
    time.sleep(0.1)
    # Enable the modulator
    GPIO.output(MODULATOR_PIN, True)
    # keep enabled for a period
    time.sleep(1)
    # Disable the modulator
    GPIO.output(MODULATOR_PIN, False)

    return "Done"


if __name__ == "__main__":
    socket_setup.setup()
    app.run(host="0.0.0.0", port=8080)
