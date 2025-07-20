from flask import Flask, render_template, make_response, request
import requests
import os
import urllib.parse

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/bot-login")
def bot_login():
    if request.args.get("token") != os.getenv("BOT_TOKEN"):
        return "Invalid token! This url is so the bot can login, it's not part of the challenge"

    resp = make_response("bot logged in")
    resp.set_cookie('flag', 'DUCTF{if_y0u_d1dnt_us3_mutation_x5S_th3n_it_w45_un1nt3nded_435743723}')
    return resp

@app.route("/report", methods=["POST"])
def report():
    requests.post(f"{os.getenv("INTERNAL_XSS_BOT_URL")}/visit", json={
        "url": os.getenv("BOT_VISIT_URL") + "/?input=" + urllib.parse.quote_plus(request.get_data(as_text=True))
    }, headers={
        "X-SSRF-Protection": "1"
    })

    return "Reported"

if __name__ == '__main__':
    app.run( host="0.0.0.0", port=1337, debug=False)
