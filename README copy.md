# 📘 Facebook Page Post Performance Dashboard

An interactive Streamlit dashboard built on the **real UCI "Facebook
metrics" dataset** (Moro, Rita & Vala, 2016) — 500 posts published on a
cosmetics brand's Facebook Page, each with reach, impressions, and
engagement metrics — plus a live call to a real external API
(Open-Meteo weather, free and keyless).

**Live app:** _[paste your Streamlit Community Cloud URL here after deploying — see "Deploy it live" below]_

## Dataset

- **File:** `dataset_Facebook.csv` (bundled in this repo, semicolon-separated,
  500 rows / 19 columns).
- **Source:** Moro, S., Rita, P., & Vala, B. (2016). *Predicting social
  media performance metrics and evaluation of the impact on brand
  building: A data mining approach.* Journal of Business Research —
  publicly available via the UCI Machine Learning Repository.
- **What it contains:** one row per Facebook post — its type (Photo,
  Status, Link, Video), category, the month/weekday/hour it was
  published, whether it was a paid promotion, and lifetime reach/
  impressions/engagement figures plus the raw comment, like, share, and
  total interaction counts.
- **Loading:** `load_data()` in `app.py` reads the CSV directly with
  `pd.read_csv("dataset_Facebook.csv", sep=";")` — no dependency on any
  other part of the assignment.

## Dashboard features

- **Interactive widgets** (sidebar):
  - `st.multiselect` — filter by Post Type (Photo/Status/Link/Video)
  - `st.selectbox` — filter by Paid vs Organic vs All Posts
  - `st.slider` — filter by Post Month range
- **3 chart types**, all reacting live to the filters:
  1. `st.bar_chart` — average Total Interactions by Post Type
  2. `st.line_chart` — average Total Interactions by Post Month
  3. Matplotlib pie chart — engagement mix (comments vs likes vs shares)
- **Live table**: `st.dataframe` of the currently filtered posts, plus a
  CSV download button.
- **KPIs**: post count, average reach, average total interactions, and
  average engaged users for the current filter selection.

## External API integration

- **Endpoint called:** `GET https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true`
- **Method:** GET — the app only reads current conditions, it never
  writes anything to the server, so no POST is needed anywhere in this
  app.
- **What the API returns, in plain terms:** Open-Meteo is a free weather
  forecast service. Given a latitude/longitude, the
  `current_weather=true` flag returns a small JSON object with the
  *current* conditions at that spot right now — air temperature (°C),
  wind speed (km/h), wind direction, and a numeric "weather code" that
  maps to a condition like clear sky, fog, rain, or thunderstorm. It's a
  live snapshot, not a multi-day forecast.
- **Fields the dashboard displays:** `temperature`, `windspeed`, and
  `weathercode` (decoded to a label like "Partly cloudy" via a lookup
  table in `app.py`) for whichever reference city the user picks in the
  sidebar.
- **Where in the code:** `get_current_weather()` in `app.py` makes the
  `requests.get(...)` call and parses `response.json()["current_weather"]`;
  it's rendered in the "🌦️ Live Weather (external API demo)" panel. This
  panel is intentionally kept separate from the Facebook filters — the
  Facebook dataset has no location data, so the weather demo exists to
  show the app can reach a real external API, not to analyze the posts
  themselves.

**Attribution:** Weather data by Open-Meteo.com (CC BY 4.0).

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the URL Streamlit prints (usually http://localhost:8501).
Make sure `dataset_Facebook.csv` stays in the same folder as `app.py`.

## Deploy it live (free, ~2 minutes) — Streamlit Community Cloud

This step needs your own GitHub/Streamlit account, so it has to be done
by you. It's quick:

1. Create a new **public** GitHub repository (e.g. `facebook-post-dashboard`)
   and upload `app.py`, `requirements.txt`, `dataset_Facebook.csv`, and
   this `README.md` to its root — either via GitHub's web "Add file →
   Upload files", or:
   ```bash
   git init
   git add app.py requirements.txt dataset_Facebook.csv README.md
   git commit -m "Facebook post performance dashboard with Open-Meteo API"
   git branch -M main
   git remote add origin https://github.com/<your-username>/facebook-post-dashboard.git
   git push -u origin main
   ```
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click **New app**, choose that repo and the `main` branch, and set the
   main file path to `app.py`.
4. Click **Deploy**. Streamlit Cloud installs `requirements.txt`
   automatically (~1 minute) and gives you a public URL like
   `https://<your-app-name>.streamlit.app`.
5. Paste that URL into the **"Live app"** line at the top of this README
   and commit the change, so the grader can click straight through.

No secrets or API keys are needed — Open-Meteo's public endpoint is
keyless, so the app works out of the box on Streamlit Cloud.

## Notes

- Rows with missing `Paid`, `like`, or `share` values (a handful in the
  original dataset) are filled with 0 during loading so filters and
  aggregates don't break.
- If the weather API is briefly unreachable, the dashboard degrades
  gracefully and still shows all Facebook post data and charts.