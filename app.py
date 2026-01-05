from flask import Flask, render_template, request, session, redirect
import random

app = Flask(__name__)
app.secret_key = "guess_logo_secret"

BRAND_NAMES = [
    "Reliance","RevlonLipStick","Philips","Apple","CocaCola","Nike",
    "Ola","Byjus","CRED","Amul","Surfexcel","Mcdonald's","AsianPaints","Disney",
    "Ghadi","ICICI","AxisBank","snickers","kurkure","Manyavar","KalyanBabu","Pepsi",
    "Patanjali","Britannia","Kingfisher","DairyMilk","TataSky","RedBull","SubWay","LouisVuitton"
]

LOGOS = [
    {
        "name": name,
        "image": f"{name.lower()}.png"
    }
    for name in BRAND_NAMES
]

LEADERBOARD = []

def generate_question():
    used = session.get("used", [])

    if len(used) == len(LOGOS):
        return None, None  # GAME OVER

    remaining = [l for l in LOGOS if l["name"] not in used]
    correct = random.choice(remaining)

    used.append(correct["name"])
    session["used"] = used

    options = random.sample(
        [l["name"] for l in LOGOS if l["name"] != correct["name"]],
        3
    )
    options.append(correct["name"])
    random.shuffle(options)

    return correct, options


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session.clear()
        session["username"] = request.form["username"]
        session["score"] = 0
        session["question"], session["options"] = generate_question()
        return redirect("/game")
    return render_template("login.html")

@app.route("/game", methods=["GET", "POST"])
def game():
    if "username" not in session:
        return redirect("/")

    if request.method == "POST":
        selected = request.form.get("option")
        correct = session["question"]["name"]

        if selected == correct:
            session["score"] += 1

        session["question"], session["options"] = generate_question()

        if session["question"] is None:
            LEADERBOARD.append({
                "name": session["username"],
                "score": session["score"]
            })
            return redirect("/game-over")

    return render_template(
        "game.html",
        username=session["username"],
        score=session["score"],
        question=session["question"],
        options=session["options"]
    )


@app.route("/reset")
def reset():
    if "username" in session:
        LEADERBOARD.append({
            "name": session["username"],
            "score": session["score"]
        })
    session.clear()
    return redirect("/")

@app.route("/game-over")
def game_over():
    return render_template(
        "game_over.html",
        username=session["username"],
        score=session["score"],
        total=len(LOGOS)
    )

from flask import jsonify

@app.route("/answer", methods=["POST"])
def answer():
    if "username" not in session:
        return jsonify({"game_over": True})

    data = request.json
    selected = data.get("option")
    correct = session["question"]["name"]

    result = selected == correct
    if result:
        session["score"] += 1

    session["question"], session["options"] = generate_question()

    if session["question"] is None:
        LEADERBOARD.append({
            "name": session["username"],
            "score": session["score"]
        })
        return jsonify({
            "game_over": True,
            "score": session["score"],
            "total": len(LOGOS)
        })

    return jsonify({
        "correct": result,
        "score": session["score"],
        "image": session["question"]["image"],
        "options": session["options"],
        "name": session["question"]["name"]
    })
    

@app.route("/end-game", methods=["POST"])
def end_game():
    if "username" in session:
        LEADERBOARD.append({
            "name": session["username"],
            "score": session["score"]
        })
    return jsonify({"end": True})



if __name__ == "__main__":
    app.run()
