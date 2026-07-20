# MoodCast — Weather & Mood Intelligence Dashboard

An interactive Streamlit dashboard that investigates whether live weather conditions correlate with a predicted mood category, using a trained machine learning classifier, live weather data, and geospatial visualization.

## What this project actually is

This project is best understood as **an end-to-end ML pipeline built to test a weak-signal hypothesis**, not as a validated mood-prediction tool. The honest finding — and the interesting part — is that weather alone is a poor predictor of mood. The value here is in the pipeline: live data ingestion, feature encoding, ML inference, geospatial context, and interactive visualization, all wired together and evaluated critically.

## What it does

- Fetches live weather (temperature, humidity, condition) for any city via the OpenWeatherMap API
- Feeds those features into a trained classifier to estimate a likely mood category, along with a confidence score
- Plots the city on an interactive map
- Shows a 5-day forecast trend with a predicted mood label per day
- Lets you compare two cities side by side
- Includes a dedicated analysis tab exploring correlation patterns and mood distribution across the training dataset

## Tech stack

- **UI**: Streamlit, custom CSS
- **ML**: scikit-learn (pre-trained classifier + label encoders)
- **Visualization**: Plotly (interactive charts), Folium (maps)
- **Data**: pandas
- **APIs**: OpenWeatherMap (current weather + 5-day forecast), Nominatim (geocoding)
- **Config**: python-dotenv for secure credential management

