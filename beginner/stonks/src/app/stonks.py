import os
from flask import Flask, redirect, request, render_template, session
from secrets import token_bytes

FLAG = os.environ.get("FLAG", "FAKE{REAL_FLAG_ON_INSTANCE}")

app = Flask(__name__, 
            static_url_path="/",
            static_folder = "./static",
            template_folder="./templates")
app.secret_key = token_bytes(32)

# in AUD
SUPER_RICH = 1_000_000_000_000

# gift stonks value
STONKS_GIFT = 50

# currency conversions with AUD the new dollar standard 
DOLLAR_STANDARD = "AUD"

CURRENCY_CONVERSIONS = {
    "AUD": 1,
    "NZD": 1.08,
    "EUR": 0.56,
    "USD": 0.65,
    "GBP": 0.48,
    "CAD": 0.89,
    "JPY": 94.48,
    "CNY": 4.65,
    "KRW": 888.04,
    "PLN": 2.39,
    "ZAR": 11.64,
    "INR": 55.89,
    "IDR": 10597.38
}

user_balances = {}

user_currencies = {}

user_received_stonks = []

user_passes = {}

@app.before_request
def set_boring():
    boring = request.args.get("boring", "missing")
    if boring == "missing" and "boring" in session:
        return
    session["boring"] = boring == "true"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    username = request.form.get("username", None)
    password = request.form.get("password", None)

    if username is None or password is None:
        return render_template("login.html", error="INCORRECT USERNAME OR PASSWORD LOOOOOOOL")
    
    if username not in user_passes:
        return render_template("login.html", error="INCORRECT USERNAME OR PASSWORD LOOOOOOOL")
    
    if password != user_passes[username]:
        return render_template("login.html", error="INCORRECT USERNAME OR PASSWORD LOOOOOOOL")
    
    session["username"] = username
    session["currency"] = user_currencies.get(username, DOLLAR_STANDARD)
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        return render_template("register.html")
    
    username: str = request.form.get("username", None)
    password: str = request.form.get("password", None)
    conf_password: str = request.form.get("confirm_password", None)

    if username is None or password is None:
        return render_template("register.html", error="MISSING USERNAME AND PASSWORD")
    
    if username.strip() == "" or password.strip() == "":
        return render_template("register.html", error="MISSING USERNAME AND PASSWORD")

    if username in user_passes:
        return render_template("register.html", error="USERNAME ALREADY EXISTS")
    
    if password != conf_password:
        return render_template("register.html", error="PASSWORDS DO NOT EQUAL!")
    
    user_passes[username] = password
    user_balances[username] = STONKS_GIFT
    user_currencies[username] = DOLLAR_STANDARD
    
    return redirect("/login")

@app.route("/are-you-rich", methods=['GET'])
def are_you_rich():
    if not session.get("username", False) or not session.get("currency", False):
        return redirect("/login")
    
    u = session.get("username")
    currency = session.get("currency")
    balance_aud = user_balances.get(u, 0) / CURRENCY_CONVERSIONS[currency]

    if balance_aud > SUPER_RICH:
        return render_template("are-you-rich.html", 
                               message=f"YES YOU ARE! HERE IS A FLAG {FLAG}", 
                               aud_balance=balance_aud)
    return render_template("are-you-rich.html", message="NAH YA BROKE LOOOOOOOOOOOOL", 
                           aud_balance=balance_aud)
    

@app.route("/change-currency", methods=['GET', 'POST'])
def change_currency():
    if not session.get("username", False) or not session.get("currency", False):
        return redirect("/login")
    
    if request.method == "GET":
        return render_template("change_currency.html", currencies=CURRENCY_CONVERSIONS)

    u = session["username"]
    old_currency = session["currency"]
    new_currency = request.form.get("currency", DOLLAR_STANDARD)
    if new_currency not in CURRENCY_CONVERSIONS:
        return render_template("change_currency.html", error="INVALID CURRENCY", currencies=CURRENCY_CONVERSIONS)
    
    if u not in user_balances:
        user_balances[u] = STONKS_GIFT * user_currencies[u]

    session["currency"] = new_currency
    user_balances[u] = (user_balances[u] / CURRENCY_CONVERSIONS[old_currency]) * CURRENCY_CONVERSIONS[new_currency] 
    user_currencies[u] = new_currency
    
    return redirect("/")


@app.route("/", methods=['GET'])
def index():
    if not session.get("username", False) or not session.get("currency", False):
        return redirect("/login")
    
    u = session["username"]
    return render_template("index.html", 
                           balance = user_balances.get(u, 0),
                           currency = user_currencies.get(u, DOLLAR_STANDARD))

if __name__ == '__main__':
    app.run("0.0.0.0", 1337, debug=False)