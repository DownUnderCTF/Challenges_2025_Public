from flask import Flask, Response, render_template, request
from hashlib import sha256
import subprocess
import secrets
import os
import shutil

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

def extract(extract_cmd: list[str], create_cmd: list[str]):
    if "zipfile" not in request.files:
        return "Invalid request", 500

    file = request.files["zipfile"]
    filedata = file.stream.read()

    h = sha256(filedata).hexdigest()

    zippath = f"/tmp/{h}.zip"
    extractdir = f"/tmp/{secrets.token_hex(8)}"
    finalzippath = f"/tmp/{secrets.token_hex(8)}.zip"

    os.mkdir(extractdir)

    with open(zippath, "wb") as f:
        f.write(filedata)

    subprocess.run([*extract_cmd, zippath], cwd=extractdir)
    subprocess.run([*create_cmd, finalzippath, extractdir])

    with open(finalzippath, "rb") as f:
        finaldata = f.read()

    os.remove(zippath)
    os.remove(finalzippath)
    shutil.rmtree(extractdir)

    return Response(finaldata, mimetype="application/zip")

@app.route("/un7z", methods=["POST"])
def un7z():
    return extract(["7z", "x", "-y"], ["7z", "a"])

@app.route("/unzip", methods=["POST"])
def unzip():
    return extract(["unzip", "-:"], ["zip", "-y", "-r"])


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
