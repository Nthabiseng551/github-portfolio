import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

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
    user_id = session["user_id"]
    stocks = db.execute(
        "SELECT symbol, price, SUM(shares) as total_shares FROM transactions WHERE user_id = ? GROUP BY symbol",
        user_id,
    )

    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]

    total_value = cash

    for stock in stocks:
        quote = lookup(stock[symbol])
        stock["price"] = quote["price"]
        stock["value"] = stock["price"] * stock["total_shares"]
        total_value += stock["value"]

    return render_template(
        "index.html", stocks=stocks, cash=cash, total_value=total_value, usd=usd
    )


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        shares = request.form.get("shares")
        if not symbol:
            return apology("Please provide the stock's symbol")
        elif not shares:
            return apology("Please provide the number of shares you'd like buy")
        elif not shares.isdigit() or int(shares) <= 0:
            return apology("A positive number of shares must be provided")

        quote = lookup(symbol)
        if quote is None:
            return apology("Invalid symbol")

        price = quote["price"]
        total_price = int(shares) * price
        user_id = session["user_id"]
        cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0][
            "cash"
        ]  # index into the dict produced by db.execute

        if total_price > cash:
            return apology("Insufficient cash")

        # Update user's table
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash - total_cost, user_id)

        # Add transaction to the transaction table
        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price, type) VALUES (?, ?, ?, ?, ?))",
            user_id,
            symbol,
            shares,
            price,
            "Buy",
        )

        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    transactions = db.execute(
        "SELECT * FROM transactions WHERE user_id = ? ORDER BY transacted DESC", user_id
    )

    return render_template("history.html", transactions=transactions, usd=usd)


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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
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
    if request.method == "POST":
        symbol = request.form.get("symbol")
        quote = lookup(symbol)
        if not quote:
            return apology("Invalid symbol")
        return render_template("quoted.html", quote=quote, usd=usd)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user id
    session.clear()

    # User reached route via POST by submitting form

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("Username required")

        elif not request.form.get("password"):
            return apology("Password required")

        elif not request.form.get("confirmation"):
            return apology("Re-enter password to confirm")

        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("Passwords do not match")

        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        if len(rows) != 0:
            return apology("Username already exist, try another one")

        db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            request.form.get("username"),
            generate_password_hash(request.form.get("password")),
        )

        # recently inserted user
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )
        session["user_id"] = rows[0]["id"]

        # Redirect to homepage
        return redirect("/")

    # User reached route via GET through URL or redirect
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = session["user_id"]
    stocks = db.execute(
        "SELECT symbol, SUM(shares) as total_shares FROM transactions WHERE user_id= ? GROUP BY symbol HAVING total_shares > 0",
        user_id,
    )

    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        shares = request.form.get("shares")
        if not symbol:
            return apology("Stock's symbol required")
        elif not shares:
            return apology("Please provide the number of shares you'd like buy")
        elif not shares.isdigit() or int(shares) <= 0:
            return apology("A positive number of shares must be provided")

        for stock in stocks:
            if stock["symbol"] == symbol:
                if stock["total_shares"] < int(shares):
                    return apology("not enough shares")
                else:
                    quote = lookup(symbol)
                    if quote is None:
                        return apology("Symbol not found")
                    price = quote["price"]
                    total_price = int(shares) * price

                    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)

                    db.execute(
                        "UPDATE users SET cash = ? WHERE id = ?",
                        cash + total_price,
                        user_id,
                    )

                    db.execute(
                        "INSERT INTO transactions (user_id, symbol, shares, price, type) VALUES (?, ?, ?, ?)",
                        user_id,
                        symbol,
                        -shares,
                        price,
                        "sell",
                    )

                    return redirect("/")
        return apology("Invalid symbol")
    else:
        return render_template("sell.html", stocks=stocks)

    valid = True

    if len(password) < 8 or len(password) > 20:
        print("The length of the password must be atleast 8 but not exceeding 20")
        valid = False

    if not any(char.isdigit() for char in password):
        print("Password must contain atleast one number")
        valid = False

    if not any(char.isupper() for char in passwd) or not any(
        char.islower() for char in passwd
    ):
        print(
            "Password must contain atleast one uppercase letter and atleast one lowercase letter"
        )
        valid = False

    if valid:
        return valid
