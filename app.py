from flask import Flask,render_template
from premierLeague import predict_match,ratings
import todaysMatches
app = Flask(__name__)
@app.route("/")
def home():
    matches = todaysMatches.get_todays_matches() 
    results = [] 
    for match in matches:
        try:
            results.append(predict_match(match["home"],match["away"],ratings=ratings))
        except KeyError:
            results.append("ERROR")
    return render_template("home.html",matches=results)
if __name__ == "__main__":
    app.run(debug=True)