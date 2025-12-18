from flask import Flask, render_template, request, redirect, url_for, session
from model import match_probabilities
import todaysMatches
import psycopg2
import bcrypt
from dotenv import load_dotenv
from os import getenv
load_dotenv()
db_info = {
    "host": getenv("PGHOST"),
    "user": getenv("PGUSER"),
    "db": getenv("PGDB"),
    "password": getenv("PGPASSWORD"),
    "port": getenv("PGPORT")
}
app = Flask(__name__)
@app.route("/")
def home():
    results = []
    matches = todaysMatches.get_todays_matches() 
    team_logos = {
    "Arsenal": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.4bb79b74.png",
    "Aston Villa": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.c0365d94.png",
    "Bournemouth": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.38183e0c.png",
    "Brentford": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.6bb91d6c.png",
    "Brighton & Hove Albion": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.8e71b1d1.png",
    "Burnley": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.a4fec3c1.png",
    "Chelsea": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.5d55e66e.png",
    "Crystal Palace": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.58ce1fec.png",
    "Everton": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.227a7e0c.png",
    "Fulham": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.f1d972bb.png",
    "Leeds United": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.5544c4e5.png",
    "Liverpool": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.822bd0ba.png",
    "Manchester City": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.b8fd03ef.png",
    "Manchester United": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.7c37db0b.png",
    "Newcastle United": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.5fb9a44c.png",
    "Nottingham Forest": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.532d41e3.png",
    "Southampton": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.2397d8e6.png",
    "Tottenham Hotspur": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.8cf7983f.png",
    "West Ham United": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.22f21770.png",
    "Wolverhampton Wanderers": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.3f80296a.png",
    "Barcelona": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.206d90db.png",
    "Real Madrid": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.53a2f082.png",
    "Atlético Madrid": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.602f4854.png",
    "Sevilla": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.5bea8ae4.png",
    "Real Sociedad": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.cdd22a4f.png",
    "Villarreal": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.a0cfea7e.png",
    "Valencia": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.2d917b24.png",
    "Real Betis": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.f1f2d721.png",
    "Celta Vigo": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.b8eaa1bb.png",
    "Getafe": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.e3c5bb23.png",
    "Bayern Munich": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.054efa67.png",
    "Borussia Dortmund": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.7c8dbfeb.png",
    "RB Leipzig": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.e3b2e947.png",
    "Bayer Leverkusen": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.c7a9f859.png",
    "Eintracht Frankfurt": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.b19020bc.png",
    "VfL Wolfsburg": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.8fcd9251.png",
    "Borussia Mönchengladbach": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.f14bbace.png",
    "Bayer 04 Leverkusen": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.c7a9f859.png",
    "Juventus": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.e0652b02.png",
    "Inter": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.d609edc0.png",
    "AC Milan": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.1a9860fe.png",
    "AS Roma": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.8d9d7e6f.png",
    "SSC Napoli": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.a9b4b4b9.png",
    "Atalanta": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.3b5f8c1e.png",
    "Lazio": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.8fa02f21.png",
    "Fiorentina": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.6a2b7350.png",
    "Paris Saint-Germain": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.e2d8892c.png",
    "Olympique Lyonnais": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.fbb8d941.png",
    "Olympique de Marseille": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.750f4bdc.png",
    "AS Monaco": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.1864f2c4.png",
    "LOSC Lille": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.3c7f31a3.png",
    "FC Nantes": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.9db47745.png",
    "Stade Rennais": "https://cdn.ssref.net/req/202301181/tlogo/fb/mini.097f41de.png",
    }

    for match in matches:
        try:
            result = match_probabilities(match["Home"],match["Away"])
            result["Homeimg"] = team_logos[match["Home"]]
            result["Awayimg"] = team_logos[match["Away"]]
            results.append(result)
        except KeyError:
            results.append("ERROR")
    return render_template("home.html",matches=results)
@app.route("/match/<int:match_id>")
def match_detail(match_id):
    matches = todaysMatches.get_todays_matches()
    for match in matches:
        result = match_probabilities(match["Home"], match["Away"])
        if result["Id"] == match_id:
            return render_template("match.html", match=result)
@app.route("/signup",methods=['GET','POST'])
def signup():
    if request.method == "POST":
        print("Signup")
        username = request.form.get("username")
        email = request.form.get("email")
        salt = bcrypt.gensalt()
        password = request.form.get("password")
        if not username or not email or not password:
            return "Missing fields", 400
        password = bcrypt.hashpw(password.encode('utf-8'),salt)
        conn = psycopg2.connect(
            database=db_info["db"],
            user=db_info["user"],
            password=db_info["password"],
            host=db_info["host"],
            port=db_info["port"]
        )
        cur = conn.cursor() 
        cur.execute("""INSERT into users (username,email,password) VALUES (%s,%s,%s)""",(username,email,password))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("login"))
    return render_template("signup.html")
@app.route("/login",methods=['GET','POST'])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        conn = psycopg2.connect(
            database=db_info["db"],
            user=db_info["user"],
            password=db_info["password"],
            host=db_info["host"],
            port=db_info["port"]
        )
        cur = conn.cursor() 
        cur.execute("""SELECT password FROM users WHERE email = %s""",(email,))
        row = cur.fetchone()
        if row and bcrypt.checkpw(password.encode("utf-8"),bytes(row[0])):
            print("login succesful")
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("home"))
    return render_template("login.html")
if __name__ == "__main__":
    app.run(debug=True)