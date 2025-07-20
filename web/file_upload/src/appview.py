from flask import Flask, Response
import os
import subprocess
import re

app = Flask(__name__)

@app.route("/<filename>")
def serve(filename):
    if not re.match(r"[a-z0-9-]", filename):
        return "403", 403

    safe_path = "/app/uploads/" + filename

    if not os.path.isfile(safe_path):
        return "404", 404

    mime_type = subprocess.run(["file", "-b", "-i", safe_path], stdout=subprocess.PIPE).stdout.decode().strip()

    try:
        with open(safe_path, 'rb') as f:
            file_data = f.read()
            resp = Response(file_data, mimetype=mime_type)
            resp.headers["X-Frame-Options"] = "DENY"
            resp.headers["Cross-Origin-Opener-Policy"] = "noopener-allow-popups"
            return resp
    except Exception as e:
        print(e)
        return "500", 500

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=False)
