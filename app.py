import os
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

try:
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
except Exception:
    supabase = None

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret")


def compute_strike_rate(runs: int, balls: int) -> float:
    try:
        runs = int(runs)
        balls = int(balls)
    except Exception:
        return 0.0
    if balls <= 0:
        return 0.0
    return round((runs / balls) * 100, 2)


def compute_economy(runs_conceded: int, balls_bowled: int) -> float:
    try:
        runs_conceded = int(runs_conceded)
        balls_bowled = int(balls_bowled)
    except Exception:
        return 0.0
    if balls_bowled <= 0:
        return 0.0
    overs = balls_bowled / 6.0
    if overs == 0:
        return 0.0
    return round(runs_conceded / overs, 2)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/add-player", methods=["GET", "POST"])
def add_player():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        role = request.form.get("role", "batsman").strip()
        if not name:
            flash("Player name is required.")
            return redirect(url_for("add_player"))
        # Insert into Supabase
        if supabase is None:
            flash("Database client not configured. Check SUPABASE_URL and SUPABASE_KEY in .env.")
            return redirect(url_for("add_player"))

        payload = {
            "name": name,
            "role": role,
        }
        try:
            supabase.table("players").insert(payload).execute()
            flash(f"Player '{name}' added.")
        except Exception as e:
            flash(f"Error adding player: {e}")
        return redirect(url_for("index"))

    return render_template("add_player.html")


@app.route("/add-match", methods=["GET", "POST"])
def add_match():
    if supabase is None:
        flash("Database client not configured. Check SUPABASE_URL and SUPABASE_KEY in .env.")
        return redirect(url_for("index"))

    # Fetch players for the form
    resp = supabase.table("players").select("*").order("id").execute()
    players = getattr(resp, "data", resp) or []

    if request.method == "POST":
        match_name = request.form.get("match_name", "").strip()
        if not match_name:
            flash("Match name is required.")
            return redirect(url_for("add_match"))

        # For each player, read the inputs named using the convention: runs_<id>, balls_<id>, balls_bowled_<id>, runs_conceded_<id>, wickets_<id>, maidens_<id>
        for p in players:
            pid = p.get("id")
            prefix = f"{pid}"
            runs = int(request.form.get(f"runs_{prefix}", 0) or 0)
            balls = int(request.form.get(f"balls_{prefix}", 0) or 0)
            balls_bowled = int(request.form.get(f"balls_bowled_{prefix}", 0) or 0)
            runs_conceded = int(request.form.get(f"runs_conceded_{prefix}", 0) or 0)
            wickets = int(request.form.get(f"wickets_{prefix}", 0) or 0)
            maidens = int(request.form.get(f"maidens_{prefix}", 0) or 0)

            # Insert a match entry row
            entry = {
                "match_name": match_name,
                "player_id": pid,
                "runs": runs,
                "balls": balls,
                "balls_bowled": balls_bowled,
                "runs_conceded": runs_conceded,
                "wickets": wickets,
                "maidens": maidens,
            }
            try:
                supabase.table("match_entries").insert(entry).execute()
            except Exception as e:
                # continue but inform user
                flash(f"Failed to save entry for player {p.get('name')}: {e}")

            # Update aggregated player stats
            try:
                # Re-fetch player row to get current aggregates
                r = supabase.table("players").select("*").eq("id", pid).single().execute()
                player = getattr(r, "data", r) or p

                matches = (player.get("matches") or 0) + 1
                total_runs = (player.get("total_runs") or 0) + runs
                balls_faced = (player.get("balls_faced") or 0) + balls
                highest_score = max(player.get("highest_score") or 0, runs)
                ducks = (player.get("ducks") or 0) + (1 if runs == 0 else 0)

                balls_bowled_total = (player.get("balls_bowled") or 0) + balls_bowled
                runs_conceded_total = (player.get("runs_conceded") or 0) + runs_conceded
                wickets_total = (player.get("wickets") or 0) + wickets
                maidens_total = (player.get("maidens") or 0) + maidens

                strike_rate = compute_strike_rate(total_runs, balls_faced)
                economy = compute_economy(runs_conceded_total, balls_bowled_total)

                update_payload = {
                    "matches": matches,
                    "total_runs": total_runs,
                    "balls_faced": balls_faced,
                    "highest_score": highest_score,
                    "ducks": ducks,
                    "balls_bowled": balls_bowled_total,
                    "runs_conceded": runs_conceded_total,
                    "wickets": wickets_total,
                    "maidens": maidens_total,
                    "strike_rate": strike_rate,
                    "economy": economy,
                }
                supabase.table("players").update(update_payload).eq("id", pid).execute()
            except Exception as e:
                flash(f"Failed to update aggregates for {p.get('name')}: {e}")

        flash("Match entries saved and aggregates updated.")
        return redirect(url_for("leaderboard"))

    return render_template("add_match.html", players=players)


@app.route("/leaderboard")
def leaderboard():
    if supabase is None:
        flash("Database client not configured. Check SUPABASE_URL and SUPABASE_KEY in .env.")
        return redirect(url_for("index"))
    resp = supabase.table("players").select("*").order("total_runs", desc=True).execute()
    players = getattr(resp, "data", resp) or []
    return render_template("leaderboard.html", players=players)


if __name__ == "__main__":
    app.run(debug=True)
