from flask import Flask, render_template, request, redirect, url_for, session
from model import match_probabilities
import todaysMatches
import psycopg2
import bcrypt
from dotenv import load_dotenv
from os import getenv
from flask_session import Session
from datetime import timedelta
load_dotenv()
db_info = {
    "host": getenv("PGHOST"),
    "user": getenv("PGUSER"),
    "db": getenv("PGDB"),
    "password": getenv("PGPASSWORD"),
    "port": getenv("PGPORT")
}
app = Flask(__name__)
app.config["SECRET_KEY"] = getenv("SECRET_KEY")
app.config["SESSION_TYPE"] = "filesystem"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=1)
Session(app)
@app.route("/")
def home():
    results = []
    matches = todaysMatches.get_todays_matches() 
    team_logos = {
        "Arsenal": "https://upload.wikimedia.org/wikipedia/en/thumb/5/53/Arsenal_FC.svg/250px-Arsenal_FC.svg.png",
        "Aston Villa": "https://upload.wikimedia.org/wikipedia/en/thumb/9/9a/Aston_Villa_FC_new_crest.svg/250px-Aston_Villa_FC_new_crest.svg.png",
        "AFC Bournemouth": "https://upload.wikimedia.org/wikipedia/en/thumb/e/e5/AFC_Bournemouth_%282013%29.svg/250px-AFC_Bournemouth_%282013%29.svg.png",
        "Brentford": "https://upload.wikimedia.org/wikipedia/en/thumb/2/2a/Brentford_FC_crest.svg/250px-Brentford_FC_crest.svg.png",
        "Brighton & Hove Albion": "https://upload.wikimedia.org/wikipedia/en/thumb/d/d0/Brighton_and_Hove_Albion_FC_crest.svg/250px-Brighton_and_Hove_Albion_FC_crest.svg.png",
        "Burnley": "https://upload.wikimedia.org/wikipedia/en/thumb/6/6d/Burnley_FC_Logo.svg/250px-Burnley_FC_Logo.svg.png",
        "Chelsea": "https://upload.wikimedia.org/wikipedia/en/thumb/c/cc/Chelsea_FC.svg/250px-Chelsea_FC.svg.png",
        "Crystal Palace": "https://upload.wikimedia.org/wikipedia/en/thumb/a/a2/Crystal_Palace_FC_logo_%282022%29.svg/250px-Crystal_Palace_FC_logo_%282022%29.svg.png",
        "Everton": "https://upload.wikimedia.org/wikipedia/en/thumb/7/7c/Everton_FC_logo.svg/250px-Everton_FC_logo.svg.png",
        "Fulham": "https://upload.wikimedia.org/wikipedia/en/thumb/e/eb/Fulham_FC_%28shield%29.svg/250px-Fulham_FC_%28shield%29.svg.png",
        "Leeds United": "https://upload.wikimedia.org/wikipedia/en/thumb/5/54/Leeds_United_F.C._logo.svg/250px-Leeds_United_F.C._logo.svg.png",
        "Liverpool": "https://upload.wikimedia.org/wikipedia/en/thumb/0/0c/Liverpool_FC.svg/250px-Liverpool_FC.svg.png",
        "Man City": "https://upload.wikimedia.org/wikipedia/en/thumb/e/eb/Manchester_City_FC_badge.svg/250px-Manchester_City_FC_badge.svg.png",
        "Man United": "https://upload.wikimedia.org/wikipedia/en/thumb/7/7a/Manchester_United_FC_crest.svg/250px-Manchester_United_FC_crest.svg.png",
        "Newcastle United": "https://upload.wikimedia.org/wikipedia/en/thumb/5/56/Newcastle_United_Logo.svg/250px-Newcastle_United_Logo.svg.png",
        "Nott'm Forest": "https://upload.wikimedia.org/wikipedia/en/thumb/e/e5/Nottingham_Forest_F.C._logo.svg/120px-Nottingham_Forest_F.C._logo.svg.png",
        "Sunderland": "https://upload.wikimedia.org/wikipedia/en/thumb/7/77/Logo_Sunderland.svg/330px-Logo_Sunderland.svg.png",
        "Tottenham Hotspur": "https://upload.wikimedia.org/wikipedia/en/thumb/b/b4/Tottenham_Hotspur.svg/250px-Tottenham_Hotspur.svg.png",
        "West Ham United": "https://upload.wikimedia.org/wikipedia/en/thumb/c/c2/West_Ham_United_FC_logo.svg/250px-West_Ham_United_FC_logo.svg.png",
        "Wolves": "https://upload.wikimedia.org/wikipedia/en/thumb/c/c9/Wolverhampton_Wanderers_FC_crest.svg/250px-Wolverhampton_Wanderers_FC_crest.svg.png",

        # 🇪🇸 La Liga
        "Alavés": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f8/Deportivo_Alaves_logo_%282020%29.svg/250px-Deportivo_Alaves_logo_%282020%29.svg.png",
        "Athletic Bilbao": "https://upload.wikimedia.org/wikipedia/en/thumb/9/98/Club_Athletic_Bilbao_logo.svg/250px-Club_Athletic_Bilbao_logo.svg.png",
        "Atlético Madrid": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f9/Atletico_Madrid_Logo_2024.svg/250px-Atletico_Madrid_Logo_2024.svg.png",
        "Barcelona": "https://upload.wikimedia.org/wikipedia/en/thumb/4/47/FC_Barcelona_%28crest%29.svg/250px-FC_Barcelona_%28crest%29.svg.png",
        "Celta Vigo": "https://upload.wikimedia.org/wikipedia/en/thumb/1/12/RC_Celta_de_Vigo_logo.svg/250px-RC_Celta_de_Vigo_logo.svg.png",
        "Elche": "https://upload.wikimedia.org/wikipedia/en/thumb/a/a7/Elche_CF_logo.svg/250px-Elche_CF_logo.svg.png",
        "Espanyol": "https://upload.wikimedia.org/wikipedia/en/thumb/9/92/RCD_Espanyol_crest.svg/250px-RCD_Espanyol_crest.svg.png",
        "Getafe": "https://upload.wikimedia.org/wikipedia/en/thumb/4/46/Getafe_logo.svg/250px-Getafe_logo.svg.png",
        "Girona": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f7/Girona_FC_Logo.svg/250px-Girona_FC_Logo.svg.png",
        "Levante": "https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/250px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png",
        "Mallorca": "https://upload.wikimedia.org/wikipedia/en/thumb/e/e0/Rcd_mallorca.svg/250px-Rcd_mallorca.svg.png",
        "Osasuna": "https://upload.wikimedia.org/wikipedia/en/thumb/3/38/CA_Osasuna_2024_crest.svg/250px-CA_Osasuna_2024_crest.svg.png",
        "Rayo Vallecano": "https://upload.wikimedia.org/wikipedia/en/thumb/d/d8/Rayo_Vallecano_logo.svg/250px-Rayo_Vallecano_logo.svg.png",
        "Real Betis": "https://upload.wikimedia.org/wikipedia/en/thumb/1/13/Real_betis_logo.svg/250px-Real_betis_logo.svg.png",
        "Real Madrid": "https://upload.wikimedia.org/wikipedia/en/thumb/5/56/Real_Madrid_CF.svg/250px-Real_Madrid_CF.svg.png",
        "Real Oviedo": "https://upload.wikimedia.org/wikipedia/en/thumb/6/6e/Real_Oviedo_logo.svg/250px-Real_Oviedo_logo.svg.png",
        "Real Sociedad": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f1/Real_Sociedad_logo.svg/250px-Real_Sociedad_logo.svg.png",
        "Sevilla": "https://upload.wikimedia.org/wikipedia/en/thumb/3/3b/Sevilla_FC_logo.svg/250px-Sevilla_FC_logo.svg.png",
        "Valencia": "https://upload.wikimedia.org/wikipedia/en/thumb/c/ce/Valenciacf.svg/250px-Valenciacf.svg.png",
        "Villarreal": "https://upload.wikimedia.org/wikipedia/en/thumb/b/b9/Villarreal_CF_logo-en.svg/250px-Villarreal_CF_logo-en.svg.png",
        # 🇮🇹 Serie A
        "Atalanta": "https://upload.wikimedia.org/wikipedia/en/thumb/6/66/AtalantaBC.svg/250px-AtalantaBC.svg.png",
        "Bologna": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Bologna_F.C._1909_logo.svg/250px-Bologna_F.C._1909_logo.svg.png",
        "Cagliari": "https://upload.wikimedia.org/wikipedia/en/thumb/6/61/Cagliari_Calcio_1920.svg/250px-Cagliari_Calcio_1920.svg.png",
        "Como": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Calcio_Como_-_logo_%28Italy%2C_2019-%29.svg/250px-Calcio_Como_-_logo_%28Italy%2C_2019-%29.svg.png",
        "Cremonese": "https://upload.wikimedia.org/wikipedia/en/thumb/e/e1/US_Cremonese_logo.svg/250px-US_Cremonese_logo.svg.png",
        "Fiorentina": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/ACF_Fiorentina_-_logo_%28Italy%2C_2022%29.svg/250px-ACF_Fiorentina_-_logo_%28Italy%2C_2022%29.svg.png",
        "Genoa": "https://upload.wikimedia.org/wikipedia/en/thumb/2/2c/Genoa_CFC_crest.svg/250px-Genoa_CFC_crest.svg.png",
        "Hellas Verona": "https://upload.wikimedia.org/wikipedia/en/thumb/9/92/Hellas_Verona_FC_logo_%282020%29.svg/250px-Hellas_Verona_FC_logo_%282020%29.svg.png",
        "Inter Milan": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/FC_Internazionale_Milano_2021.svg/250px-FC_Internazionale_Milano_2021.svg.png",
        "Juventus": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Juventus_FC_-_logo_black_%28Italy%2C_2020%29.svg/250px-Juventus_FC_-_logo_black_%28Italy%2C_2020%29.svg.png",
        "Lazio": "https://upload.wikimedia.org/wikipedia/en/thumb/c/ce/S.S._Lazio_badge.svg/250px-S.S._Lazio_badge.svg.png",
        "Lecce": "https://upload.wikimedia.org/wikipedia/en/thumb/2/23/US_Lecce_crest.svg/250px-US_Lecce_crest.svg.png",
        "AC Milan": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Logo_of_AC_Milan.svg/330px-Logo_of_AC_Milan.svg.png",
        "Napoli": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/SSC_Napoli_2025_%28white_and_azure%29.svg/250px-SSC_Napoli_2025_%28white_and_azure%29.svg.png",
        "Parma": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Logo_Parma_Calcio_1913_%28adozione_2016%29.svg/250px-Logo_Parma_Calcio_1913_%28adozione_2016%29.svg.png",
        "Pisa": "https://upload.wikimedia.org/wikipedia/en/thumb/6/6b/Pisa_SC_crest.svg/250px-Pisa_SC_crest.svg.png",
        "Roma": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f7/AS_Roma_logo_%282017%29.svg/250px-AS_Roma_logo_%282017%29.svg.png",
        "Sassuolo": "https://upload.wikimedia.org/wikipedia/en/thumb/1/1c/US_Sassuolo_Calcio_logo.svg/250px-US_Sassuolo_Calcio_logo.svg.png",
        "Torino": "https://upload.wikimedia.org/wikipedia/en/thumb/2/2e/Torino_FC_Logo.svg/250px-Torino_FC_Logo.svg.png",
        "Udinese": "https://upload.wikimedia.org/wikipedia/en/thumb/c/ce/Udinese_Calcio_logo.svg/250px-Udinese_Calcio_logo.svg.png",

        # 🇩🇪 Bundesliga
        "Augsburg": "https://upload.wikimedia.org/wikipedia/en/thumb/c/c5/FC_Augsburg_logo.svg/250px-FC_Augsburg_logo.svg.png",
        "Union Berlin": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/1._FC_Union_Berlin_Logo.svg/250px-1._FC_Union_Berlin_Logo.svg.png",
        "Werder Bremen": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/SV-Werder-Bremen-Logo.svg/250px-SV-Werder-Bremen-Logo.svg.png",
        "Borussia Dortmund": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Borussia_Dortmund_logo.svg/250px-Borussia_Dortmund_logo.svg.png",
        "Eintracht Frankfurt": "https://upload.wikimedia.org/wikipedia/en/thumb/7/7e/Eintracht_Frankfurt_crest.svg/250px-Eintracht_Frankfurt_crest.svg.png",
        "Freiburg": "https://upload.wikimedia.org/wikipedia/en/thumb/6/6d/SC_Freiburg_logo.svg/250px-SC_Freiburg_logo.svg.png",
        "Hamburger SV": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Hamburger_SV_logo.svg/250px-Hamburger_SV_logo.svg.png",
        "Heidenheim": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/1._FC_Heidenheim_1846.svg/250px-1._FC_Heidenheim_1846.svg.png",
        "Hoffenheim": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Logo_TSG_Hoffenheim.svg/250px-Logo_TSG_Hoffenheim.svg.png",
        "Köln": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/1._FC_Koeln_Logo_2014%E2%80%93.svg/250px-1._FC_Koeln_Logo_2014%E2%80%93.svg.png",
        "RB Leipzig": "https://upload.wikimedia.org/wikipedia/en/thumb/0/04/RB_Leipzig_2014_logo.svg/330px-RB_Leipzig_2014_logo.svg.png",
        "Bayer Leverkusen": "https://upload.wikimedia.org/wikipedia/en/thumb/5/59/Bayer_04_Leverkusen_logo.svg/250px-Bayer_04_Leverkusen_logo.svg.png",
        "Mainz 05": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/1._FSV_Mainz_05_logo.svg/250px-1._FSV_Mainz_05_logo.svg.png",
        "Borussia Mönchengladbach": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Borussia_M%C3%B6nchengladbach_logo.svg/250px-Borussia_M%C3%B6nchengladbach_logo.svg.png",
        "Bayern Munich": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/FC_Bayern_M%C3%BCnchen_logo_%282024%29.svg/250px-FC_Bayern_M%C3%BCnchen_logo_%282024%29.svg.png",
        "St. Pauli": "https://upload.wikimedia.org/wikipedia/en/thumb/8/8f/FC_St._Pauli_logo_%282018%29.svg/250px-FC_St._Pauli_logo_%282018%29.svg.png",
        "Stuttgart": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/VfB_Stuttgart_1893_Logo.svg/250px-VfB_Stuttgart_1893_Logo.svg.png",
        "Wolfsburg": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/VfL_Wolfsburg_Logo.svg/250px-VfL_Wolfsburg_Logo.svg.png",

        # 🇫🇷 Ligue 1
        "Angers": "https://upload.wikimedia.org/wikipedia/en/thumb/d/d4/Angers_SCO_logo.svg/250px-Angers_SCO_logo.svg.png",
        "Auxerre": "https://upload.wikimedia.org/wikipedia/en/thumb/5/51/AJAuxerreLogo.svg/250px-AJAuxerreLogo.svg.png",
        "Brest": "https://upload.wikimedia.org/wikipedia/en/thumb/0/05/Stade_Brestois_29_logo.svg/250px-Stade_Brestois_29_logo.svg.png",
        "Le Havre": "https://upload.wikimedia.org/wikipedia/en/thumb/f/fc/Le_Havre_AC_logo.svg/250px-Le_Havre_AC_logo.svg.png",
        "Lens": "https://upload.wikimedia.org/wikipedia/en/thumb/c/cc/RC_Lens_logo.svg/250px-RC_Lens_logo.svg.png",
        "Lille": "https://upload.wikimedia.org/wikipedia/en/thumb/3/3f/Lille_OSC_2018_logo.svg/250px-Lille_OSC_2018_logo.svg.png",
        "Lorient": "https://upload.wikimedia.org/wikipedia/en/thumb/4/4c/FC_Lorient_logo.svg/250px-FC_Lorient_logo.svg.png",
        "Lyon": "https://upload.wikimedia.org/wikipedia/en/thumb/1/1c/Olympique_Lyonnais_logo.svg/250px-Olympique_Lyonnais_logo.svg.png",
        "Marseille": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Olympique_Marseille_logo.svg/250px-Olympique_Marseille_logo.svg.png",
        "Metz": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/FC_Metz_2021_Logo.svg/250px-FC_Metz_2021_Logo.svg.png",
        "Monaco": "https://upload.wikimedia.org/wikipedia/en/thumb/c/cf/LogoASMonacoFC2021.svg/250px-LogoASMonacoFC2021.svg.png",
        "Nantes": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/Logo_FC_Nantes_%28avec_fond%29_-_2019.svg/250px-Logo_FC_Nantes_%28avec_fond%29_-_2019.svg.png",
        "Nice": "https://upload.wikimedia.org/wikipedia/en/thumb/2/2e/OGC_Nice_logo.svg/250px-OGC_Nice_logo.svg.png",
        "Paris FC": "https://upload.wikimedia.org/wikipedia/en/thumb/9/9f/Paris_FC_logo.svg/250px-Paris_FC_logo.svg.png",
        "Paris Saint-Germain": "https://upload.wikimedia.org/wikipedia/en/thumb/a/a7/Paris_Saint-Germain_F.C..svg/250px-Paris_Saint-Germain_F.C..svg.png",
        "Rennes": "https://upload.wikimedia.org/wikipedia/en/thumb/9/9e/Stade_Rennais_FC.svg/250px-Stade_Rennais_FC.svg.png",
        "Strasbourg": "https://upload.wikimedia.org/wikipedia/en/thumb/8/80/Racing_Club_de_Strasbourg_logo.svg/250px-Racing_Club_de_Strasbourg_logo.svg.png",
        "Toulouse": "https://upload.wikimedia.org/wikipedia/en/thumb/6/63/Toulouse_FC_2018_logo.svg/250px-Toulouse_FC_2018_logo.svg.png" 
    }
    for match in matches:
        try:
            result = match_probabilities(match["Home"],match["Away"])
            result["Homeimg"] = team_logos[match["Home"]]
            result["Awayimg"] = team_logos[match["Away"]]
            results.append(result)
        except KeyError:
            results.append("ERROR")
    if session.get("name"): 
        return render_template("loggedIn.html",matches=results)
    return render_template("loggedOut.html",matches=results)
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
        cur.execute("""SELECT * FROM users WHERE email = %s""",(email,))
        row = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if row and bcrypt.checkpw(password.encode("utf-8"),bytes(row[3])):
            print("login succesful")
            session["name"] = row[1]
            session.permanent = True 
            session["email"] = row[2]
            session.permanent = True 
            return redirect(url_for("home"))
    return render_template("login.html")
if __name__ == "__main__":
    app.run(debug=True)