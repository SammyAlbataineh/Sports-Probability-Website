FootyOdds — Presentation Setup
Requirements

Docker Desktop (https://www.docker.com/products/docker-desktop/)
Your CSV data files (see below)


Setup (do this once)

Copy your .env file (or rename .env.example to .env and fill in values):

   SECRET_KEY=anything_random
   PGDB=footyodds
   PGUSER=footyodds
   PGPASSWORD=anything_random

Put your CSV files in the project root (same folder as app.py):

   E0.csv          E0 (1).csv      E0 (2).csv
   season-2425.csv season-2324.csv season-2223.csv
   season-2425 (1).csv  season-2324 (1).csv  season-2223 (1).csv
   season-2425 (2).csv  season-2324 (2).csv  season-2223 (2).csv
   season-2425 (3).csv  season-2324 (3).csv  season-2223 (3).csv

Build and start:

bash   docker compose up --build

Open http://localhost:5000 in your browser.


Stopping
bashdocker compose down
To also wipe the database (fresh start):
bashdocker compose down -v

Notes

The first docker compose up --build takes ~2 minutes to download and install everything.
After that, subsequent starts are instant.
The database persists between restarts unless you run down -v.