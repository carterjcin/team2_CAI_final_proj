"""
Data loading and cleaning for the Airline Delay Cause dataset (US DOT / BTS).

Source: https://www.transtats.bts.gov/OT_Delay/OT_DelayCause1.asp
Raw file: data/Airline_Delay_Cause.csv (one row per year-month-carrier-airport)
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Resolve relative to this file's location, not the current working
# directory, so the app works no matter where it's launched from.
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_PATH = BASE_DIR / "data" / "Airline_Delay_Cause.csv"

NUMERIC_COLS = [
    "arr_flights", "arr_del15", "carrier_ct", "weather_ct", "nas_ct",
    "security_ct", "late_aircraft_ct", "arr_cancelled", "arr_diverted",
    "arr_delay", "carrier_delay", "weather_delay", "nas_delay",
    "security_delay", "late_aircraft_delay",
]

CAUSE_COLS = {
    "carrier_delay": "Carrier",
    "weather_delay": "Weather",
    "nas_delay": "National Air System",
    "security_delay": "Security",
    "late_aircraft_delay": "Late Aircraft",
}


def load_clean_data(path=RAW_PATH) -> pd.DataFrame:
    """Load the raw BTS extract and apply cleaning steps.

    Cleaning performed here (documented for the assignment's
    "one messy thing" requirement):
      1. Drop rows where every numeric field is blank. These are
         carrier/airport pairs BTS lists for a month with zero
         recorded operations - there is no delay to analyze, and
         leaving them in would corrupt averages with NaNs.
      2. Coerce numeric columns (some arrive as object dtype because
         of stray blanks) and fill any remaining gaps with 0.
      3. Parse the free-text `airport_name` field
         ("Moline, IL: Quad Cities International") into separate
         city / state / airport_full_name columns so the state can
         be used for the choropleth map.
      4. Build a proper datetime `date` column from year + month for
         time-series plotting.
      5. Derive a few analysis-friendly columns: delay_rate,
         cancellation_rate, and a single tidy label combining the
         airport code and city for dropdowns.
    """
    df = pd.read_csv(path)

    # 1. drop fully-blank operational rows
    df = df.dropna(subset=["arr_flights"]).copy()

    # 2. numeric coercion
    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # 3. parse "City, ST: Airport Full Name" into parts
    parts = df["airport_name"].str.extract(
        r"^(?P<city>.+),\s*(?P<state>[A-Z]{2}):\s*(?P<airport_full_name>.+)$"
    )
    df["city"] = parts["city"]
    df["state"] = parts["state"]
    df["airport_full_name"] = parts["airport_full_name"]
    # a handful of territories/codes without a 2-letter state won't match;
    # drop those since the map/state filters can't place them
    df = df.dropna(subset=["state"]).copy()

    # 4. date column
    df["date"] = pd.to_datetime(
        df["year"].astype(int).astype(str) + "-" + df["month"].astype(int).astype(str) + "-01"
    )

    # 5. derived metrics
    df["delay_rate"] = np.where(
        df["arr_flights"] > 0, df["arr_del15"] / df["arr_flights"], 0
    ).round(4)
    df["cancellation_rate"] = np.where(
        df["arr_flights"] > 0, df["arr_cancelled"] / df["arr_flights"], 0
    ).round(4)
    df["avg_arr_delay_min"] = np.where(
        df["arr_flights"] > 0, df["arr_delay"] / df["arr_flights"], 0
    ).round(2)

    df["airport_label"] = df["airport"] + " - " + df["city"] + ", " + df["state"]

    return df


def carrier_options(df: pd.DataFrame):
    lookup = df[["carrier", "carrier_name"]].drop_duplicates().sort_values("carrier_name")
    return [{"label": row.carrier_name, "value": row.carrier} for row in lookup.itertuples()]


def airport_options(df: pd.DataFrame):
    lookup = df[["airport", "airport_label"]].drop_duplicates().sort_values("airport_label")
    return [{"label": row.airport_label, "value": row.airport} for row in lookup.itertuples()]


def year_options(df: pd.DataFrame):
    years = sorted(df["year"].unique())
    return [{"label": str(y), "value": int(y)} for y in years]
