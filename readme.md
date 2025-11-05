# 🏏 Cricket Stats Tracker — README

A **Flask + Tailwind CSS** web application to manage and track cricket player statistics for friendly or local matches (like *Don Bradman Cricket 17* sessions).

This app allows users to enter **match-by-match stats** for each player — including batting and bowling performance — and automatically calculates **career totals** such as **strike rate**, **economy**, **highest score**, and **number of ducks**.

Built for simplicity and fun, this project is the perfect foundation for future expansion (e.g., auction system, team creation, player profiles).

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Tech Stack](#tech-stack)
3. [Architecture](#architecture)
4. [Core Features (MVP)](#core-features-mvp)
5. [Folder Structure](#folder-structure)
6. [Setup Instructions](#setup-instructions)
7. [Database Schema (Supabase)](#database-schema-supabase)
8. [Environment Variables](#environment-variables)
9. [Key Flask Routes](#key-flask-routes)
10. [How It Works](#how-it-works)
11. [Future Enhancements](#future-enhancements)
12. [Development Notes](#development-notes)

---

## 🧠 Overview

This project helps manage **cricket player stats** for local or friendly tournaments.
You can:

* Add new players with their roles.
* Enter match stats (runs, balls, wickets, economy, etc.).
* Automatically calculate and update cumulative player performance.
* View all data in a **leaderboard** built with Tailwind CSS for a clean look.

Everything runs in Flask — no React or JS frontend complexity.

---

## ⚙️ Tech Stack

| Layer         | Technology            | Purpose                                 |
| ------------- | --------------------- | --------------------------------------- |
| Backend       | Flask (Python)        | Core web framework                      |
| Frontend      | HTML + Tailwind CSS   | Simple, responsive UI                   |
| Database      | Supabase (PostgreSQL) | Stores players and match stats          |
| ORM/DB SDK    | `supabase-py`         | For database operations                 |
| Configuration | `.env`                | Secure storage for Supabase credentials |

---

## 🧱 Architecture

```
Browser (HTML + Tailwind)
   │
   ▼
Flask (Python)
   │
   ▼
Supabase (PostgreSQL)
```

* Flask serves HTML templates rendered with **Jinja2**.
* Flask connects to Supabase (PostgreSQL) using the `supabase-py` client.
* All stat calculations happen server-side (Python).

---

## 🏏 Core Features (MVP)

### 🧍 Player Management

* Add players with name and role (`batsman`, `bowler`, or `all-rounder`).
* Display all players in a responsive table with stats.

### 📋 Match Entry

* Add a new match (by name).
* Input each player’s:

  * Runs scored
  * Balls faced
  * Balls bowled
  * Runs conceded
  * Wickets
  * Maidens
* System automatically updates:

  * Total runs, wickets, economy, strike rate, highest score, ducks, etc.

### 📊 Leaderboard

* View all players with automatically calculated statistics.
* Clean Tailwind UI for readability.

---

## 📁 Folder Structure

```
cricket_stats_app/
│
├── app.py                       # Main Flask file
├── requirements.txt              # Dependencies
├── .env                          # Supabase credentials
│
├── templates/                    # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── add_player.html
│   ├── add_match.html
│   └── leaderboard.html
│
└── static/
    └── css/
        └── tailwind.css          # Tailwind stylesheet
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/cricket-stats-app.git
cd cricket-stats-app
```

### 2️⃣ Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate    # on Windows
# OR source venv/bin/activate on Mac/Linux
```

### 3️⃣ Install dependencies

```bash
pip install flask flask-cors supabase python-dotenv
```

### 4️⃣ Set up Tailwind CSS (optional local version)

Download Tailwind CSS via CDN for simplicity:

In `templates/base.html`:

```html
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
```

No npm setup needed for this approach.

---

## 🧮 Database Schema (Supabase)

Go to your [Supabase SQL Editor](https://app.supabase.com) and run these SQL commands:

### `players` table

```sql
CREATE TABLE players (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name TEXT NOT NULL,
  role TEXT CHECK (role IN ('batsman', 'bowler', 'allrounder')),
  matches INT DEFAULT 0,
  total_runs INT DEFAULT 0,
  balls_faced INT DEFAULT 0,
  strike_rate FLOAT DEFAULT 0,
  ducks INT DEFAULT 0,
  highest_score INT DEFAULT 0,
  balls_bowled INT DEFAULT 0,
  runs_conceded INT DEFAULT 0,
  wickets INT DEFAULT 0,
  maidens INT DEFAULT 0,
  economy FLOAT DEFAULT 0
);
```

### `match_entries` table

```sql
CREATE TABLE match_entries (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  match_name TEXT NOT NULL,
  player_id BIGINT REFERENCES players (id) ON DELETE CASCADE,
  runs INT DEFAULT 0,
  balls INT DEFAULT 0,
  balls_bowled INT DEFAULT 0,
  runs_conceded INT DEFAULT 0,
  wickets INT DEFAULT 0,
  maidens INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔐 Environment Variables

Create a `.env` file in the root directory:

```env
SUPABASE_URL=https://your-project-url.supabase.co
SUPABASE_KEY=your-anon-public-key
```

Never commit `.env` to GitHub. Add it to `.gitignore`.

---

## 🔑 Key Flask Routes

| Route          | Method   | Description                         |
| -------------- | -------- | ----------------------------------- |
| `/`            | GET      | Home page                           |
| `/add-player`  | GET/POST | Add a new player                    |
| `/add-match`   | GET/POST | Add new match data for all players  |
| `/leaderboard` | GET      | Display all players and their stats |

---

## ⚙️ How It Works

1. **Add Player**

   * Form in `add_player.html` posts to `/add-player`.
   * Flask inserts player record into Supabase.

2. **Add Match**

   * Displays all existing players.
   * Input batting and bowling stats per player.
   * Flask:

     * Inserts each player's match entry into `match_entries`.
     * Updates their cumulative stats in `players`.
     * Calculates:

       * `strike_rate = (runs / balls) * 100`
       * `economy = runs_conceded / (balls_bowled / 6)`
       * Updates ducks and highest score as needed.

3. **Leaderboard**

   * Fetches all players from Supabase.
   * Displays their aggregate stats in a Tailwind table.

---

## 🖼️ UI Pages Overview

### 🏠 Home (`index.html`)

* Simple navigation to Add Player, Add Match, and Leaderboard.

### ➕ Add Player (`add_player.html`)

* Input: player name, role.
* Tailwind-styled form.

### 🏏 Add Match (`add_match.html`)

* Input: match name.
* Table with each player row to enter:

  * Runs, balls, wickets, etc.

### 🏆 Leaderboard (`leaderboard.html`)

* Table showing all players and their stats.
* Sorted, responsive layout using Tailwind classes.

---

## 🧩 Development Notes

### Run Flask server:

```bash
python app.py
```

### View in browser:

```
http://127.0.0.1:5000
```

### Debugging Tips

* Use `print()` to inspect Supabase responses.
* Restart Flask after editing templates (auto-reload may not catch template-only changes sometimes).
* If you get CORS issues, install and import `flask-cors`.

---

## 🚀 Future Enhancements

| Category    | Feature                             | Description                           |
| ----------- | ----------------------------------- | ------------------------------------- |
| ⚔️ Auction  | Add auction system for players      | Each player can be bid on by managers |
| 🧢 Teams    | Team creation and player assignment | Assign players to specific teams      |
| 📈 Charts   | Visual analytics                    | Strike rate, economy trends           |
| 🧍 Profiles | Individual player pages             | Show match history and averages       |
| 🧾 Export   | CSV / PDF download of stats         | For records or tournaments            |
| 🔐 Auth     | Supabase Auth for secure access     | Managers log in to add/edit data      |

---

## ✅ Summary

**Cricket Stats Tracker** helps record and analyze player performances with:

* Flask backend
* Supabase database
* Tailwind-based clean UI

It’s lightweight, beginner-friendly, and designed to expand — from local friendly matches to a complete cricket analytics web app.

---

## 🧭 Copilot Instructions Summary

If using **GitHub Copilot**, instruct it as follows:

1. **Setup Flask Project:**

   * Create `app.py`, add routes `/`, `/add-player`, `/add-match`, `/leaderboard`.
   * Integrate Supabase client from `.env`.

2. **Create Templates:**

   * Use `base.html` for navigation.
   * Tailwind for styling.

3. **Implement Stat Logic:**

   * On match submission, update both `match_entries` and player totals.
   * Compute `strike_rate` and `economy` in Python.

4. **Link Everything:**

   * Use Jinja templating to render player data on leaderboard.

5. **Test and Debug:**

   * Add a few players and matches.
   * Verify calculations and UI flow.

