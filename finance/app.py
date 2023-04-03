import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # Get user cash
    user_id = session["user_id"]
    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
    total = cash[0]["cash"]

    # Get user stock symbols and their quantitys
    portfolio = db.execute(
        "SELECT * FROM (SELECT symbol, SUM(shares) AS shares from history WHERE person_id=? GROUP BY symbol ORDER BY symbol) WHERE shares > 0", user_id)

    for stock in portfolio:
        # Get other data
        quote = lookup(stock["symbol"])
        stock["name"] = quote["name"]
        stock["price"] = quote["price"]
        stock["total"] = float(stock["shares"]) * float(stock["price"])
        total += stock["total"]

        # Convert to usd and upper
        stock["price"] = usd(stock["price"])
        stock["total"] = usd(stock["total"])
        stock["symbol"] = stock["symbol"].upper()

    return render_template("index.html", portfolio=portfolio, cash=usd(cash[0]["cash"]), total=usd(total))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":

        # Gather symbol and price
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Ensure symbol and shares is not blank
        if symbol == "" or shares == "":
            return apology("input missing", 400)

        buffer = shares

        # Ensure symbol is not blank
        if shares == "" or shares.isalpha():
            return apology("MISSING SHARES", 400)
        try:
            temp = float(shares)
        except ValueError:
            return apology("fractional not supported", 400)
        if round(float(shares)) != float(shares):
            return apology("fractional not supported", 400)
        if float(shares) <= 0:
            return apology("share number can't be negative number or zero!", 400)

        shares = buffer

        quote = lookup(symbol)
        # Ensure symbol is valid

        if not quote:
            return apology("INVALID SYMBOL", 400)

        else:
            # Gathering more information
            person_id = session["user_id"]
            price = lookup(symbol)["price"]
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cash = db.execute("SELECT cash FROM users WHERE id = ?", person_id)[0]["cash"]

            # Check if buy is possible
            if cash < float(shares) * price:
                return apology("Not enough money", 400)

            else:
                # Subtract price
                cash = cash - (float(shares) * price)
                db.execute("UPDATE users SET cash = ?  WHERE id = ?", cash, person_id)

                # Storing information
                db.execute("INSERT INTO history (person_id, symbol, shares, price, time) VALUES (?, ?, ?, ?, ?)",
                           person_id, symbol, shares, price, time)

                # Send notification
                flash('Bought!')
                # Return to index
                return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    person_id = session["user_id"]

    # Get all transactions of the user
    history = db.execute("SELECT * FROM history WHERE person_id = ?", person_id)

    for transaction in history:
        transaction["price"] = usd(transaction["price"])

    return render_template("history.html", history=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        symbol = request.form.get("symbol")
        # Ensure symbol is not blank
        if symbol == "":
            return apology("input is blank", 400)

        quote = lookup(symbol)

        if not quote:
            return apology("INVALID SYMBOL", 400)
        else:
            return render_template("quoted.html", name=quote["name"], symbol=quote["symbol"], price=usd(quote["price"]))

     # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get inputs
        username = request.form.get("username")
        password = request.form.get("password")
        password_again = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)

         # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username is avalible
        if len(rows) != 0:
            return apology("username not avalible", 400)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 400)

         # Ensure password was again submitted
        elif not password_again:
            return apology("must provide password again", 400)

        # Ensure passwords are matching
        elif password != password_again:
            return apology("passwords must be matching", 400)

        # Add login to database
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(password))

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        # Get user_id and portfolio
        user_id = session["user_id"]
        portfolio = db.execute(
            "SELECT * FROM (SELECT symbol, SUM(shares) AS shares from history WHERE person_id = ? GROUP BY symbol ORDER BY symbol) WHERE shares > 0", user_id)

        # Get user input
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Ensure symbol is selected
        symbol_missing = True
        for stock in portfolio:
            if stock["symbol"] == symbol:
                symbol_missing = False
                held = int(stock["shares"])

        if symbol_missing:
            return apology("input missing", 400)

        # shares is not blank
        elif shares == "":
            return apology("input missing", 400)

        # Check if amount of shares are owned
        elif held < int(shares):
            return apology("too many shares", 400)

        # Sell the stock
        else:
            price = lookup(symbol)["price"]
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]

            # Add cash
            cash = cash + (float(shares) * price)
            db.execute("UPDATE users SET cash = ?  WHERE id = ?", cash, user_id)

            # Storing information
            db.execute("INSERT INTO history (person_id, symbol, shares, price, time) VALUES (?, ?, ?, ?, ?)",
                       user_id, symbol, 0-int(shares), price, time)

            # Send notification
            flash('Sold!')
            # Return to index
            return redirect("/")

    else:
        # Get user_id and portfolio
        user_id = session["user_id"]
        portfolio = db.execute(
            "SELECT symbol FROM (SELECT symbol, SUM(shares) AS shares from history WHERE person_id = ? GROUP BY symbol ORDER BY symbol) WHERE shares > 0", user_id)

        return render_template("sell.html", portfolio=portfolio)


@app.route("/settings")
@login_required
def settings():
    """Show settings"""
    # Query database
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
    return render_template("settings.html", username=username[0]['username'])


@app.route("/passwordupdate", methods=["GET", "POST"])
@login_required
def passwordupdate():
    """Show settings"""

    if request.method == "POST":

        # Validate submission
        currentpassword = request.form.get("currentpassword")
        newpassword = request.form.get("newpassword")
        confirmation = request.form.get("confirmation")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        # Ensure password == confirmation
        if not (newpassword == confirmation):
            return apology("the passwords do not match", 400)

        # Ensure password not blank
        if currentpassword == "" or newpassword == "" or confirmation == "":
            return apology("input is blank", 400)

       # Ensure password is correct
        if not check_password_hash(rows[0]["hash"], currentpassword):
            return apology("invalid password", 403)
        else:
            hashcode = generate_password_hash(newpassword, method='pbkdf2:sha256', salt_length=8)
            db.execute("UPDATE users SET hash = ? WHERE id = ?", hashcode, session["user_id"])

        # Redirect user to settings
        return redirect("/settings")

    else:
        return render_template("passwordupdate.html")