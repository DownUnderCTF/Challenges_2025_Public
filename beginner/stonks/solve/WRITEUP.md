stonks
============

The main issue with the web application is that user's currency is fetched from the session cookie when converting their balance and checking if they are rich, as it shows below.

```py
@app.route("/are-you-rich", methods=['GET'])
def are_you_rich():
    if not session.get("username", False) or not session.get("currency", False):
        return redirect("/login")
    
    u = session.get("username")
    currency = session.get("currency") <2>
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
    old_currency = session["currency"] <1>
    new_currency = request.form.get("currency", DOLLAR_STANDARD)
    if new_currency not in CURRENCY_CONVERSIONS:
        return render_template("change_currency.html", error="INVALID CURRENCY", currencies=CURRENCY_CONVERSIONS)
    
    if u not in user_balances:
        user_balances[u] = STONKS_GIFT * user_currencies[u]

    session["currency"] = new_currency 
    user_balances[u] = (user_balances[u] / CURRENCY_CONVERSIONS[old_currency]) * CURRENCY_CONVERSIONS[new_currency] <1>
    user_currencies[u] = new_currency
    
    return redirect("/")
```
<1> Uses the `currency` value in the user's session cookie to convert between different currencies.

<2> Uses the `currency` session variable for converting the user's currency back to AUD to validate if they are rich.

The problem with using the `currency` value from a user's session cookie for currency conversions is that Flask session cookies are **stateless**.
So you could reuse previous session cookies with a different currency to break the currency conversion.

The following are steps to break the conversion and get a balance over 1,000,000,000,000 AUD.

1. Register and log into an account and then convert your currency to GBP. Save the returned `session` cookie for future requests.
2. Using the GBP session cookie, repeat the request to `POST /change-currency` and convert the currency to `IDR` several times. This results in $B_{new} = \frac{B_{old}}{0.48} \times 10597.38$ being used to calculate the new balance for each request and results in the balance size blowing up quickly.