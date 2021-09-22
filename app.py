import binascii
import os

import requests
from dotenv import load_dotenv
from flask import Flask, redirect, request, session

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY")
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")


@app.route("/")
def root():
    if "username" in session:
        return ("You are {}! <a href='/repos'>Repos</a> <a href='/logout'>Logout</a>" +
                "<img src={} alt='avatar'>").format(session['username'],
                                                    session["avatar"])
    if "oauth_state" not in session:
        session['oauth_state'] = binascii.hexlify(os.urandom(24))

    return ("<a href='https://github.com/login/oauth/authorize" +
            "?client_id={}&client_secret={}'>OAuth</a>").format(
                CLIENT_ID, CLIENT_SECRET)


@app.route("/authorized")
def authorized():
    code = request.args["code"]
    token_url = ("https://github.com/login/oauth/access_token" +
                 "?client_id={}&client_secret={}&code={}").format(
                     CLIENT_ID, CLIENT_SECRET, code)
    header = {"accept": "application/json"}

    res = requests.post(token_url, headers=header)
    if res.status_code == 200:
        r = res.json()
        print(f"{r=}")
        access_token = r["access_token"]

        user_url = "https://api.github.com/user"
        access_token = f"token {access_token}"

        headers = {"accept": "application/json", "Authorization": access_token}

        res = requests.get(user_url, headers=headers)
        if res.status_code == 200:
            user_info = res.json()
            print(f"{user_info=}")
            session["is_login"] = True
            session["username"] = user_info["login"]
            session["avatar"] = user_info["avatar_url"]
    return redirect("/")


@app.route("/logout")
def logout():
    for key in {"is_login", "username"}:
        if key in session:
            session.pop(key)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
