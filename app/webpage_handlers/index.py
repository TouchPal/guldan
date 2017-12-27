# -*- coding: utf-8 -*-
from flask import render_template, send_from_directory
from app import app


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/<path:path>")
def static_path(path):
    return send_from_directory("static", path)

