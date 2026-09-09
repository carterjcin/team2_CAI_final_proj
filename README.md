# Flight Delay Explorer

A multi-page Dash app for exploring US domestic flight delays by
airport, carrier, and cause of delay.

## The question

**Which airline should you actually book out of your airport, and is
it getting more or less reliable over time?**

## Who it's for

A frequent traveler deciding which carrier to pick out of a specific airport, plus anyone curious whether delays at
their airport are typically the airline's fault, the weather's, or general air-traffic congestion.

## The data

- **Source**: US Department of Transportation / Bureau of
  Transportation Statistics, "Airline Delay Cause" extract
  (https://www.transtats.bts.gov/OT_Delay/OT_DelayCause1.asp)
- **Size**: 69,600 raw rows; ~69,500 after cleaning; one row per
  (year, month, carrier, airport); 370 airports, 21 carriers,
  July 2023 &ndash; June 2026 (36 months).
- **What was messy about it**: ~51 rows were carrier/airport pairs
  BTS lists for a month with *zero* recorded flights - every numeric column was blank, which would have silently corrupted averages if left in, they're dropped. The airport's city/state also only existed buried inside one free-text field which had to be parsed apart with a regex before it could drive the state map.

## App structure

| Overview | `/` | US choropleth map of delay rate by state, filterable by year range and carrier |
| Comparison | `/comparison` | Ranked bar chart of carriers at one airport plus a sortable/filterable data table |
| Delay Causes | `/causes` | Pie + stacked bar breakdown of delay minutes by cause (carrier, weather, NAS, security, late aircraft) |

## Data dictionary (raw columns)

| Column | Definition |
|---|---|
| year | YYYY |
| month | MM (1-12) |
| carrier | DOT-assigned carrier code |
| carrier_name | Airline name |
| airport | 3-letter airport code |
| airport_name | "City, State: Full airport name" |
| arr_flights | Arrival flights |
| arr_del15 | Flights arriving 15+ minutes late |
| carrier_ct / weather_ct / nas_ct / security_ct / late_aircraft_ct | Prorated flight-count attributed to each delay cause (fractional, BTS formula) |
| arr_cancelled | Flights cancelled |
| arr_diverted | Flights diverted |
| arr_delay | Total arrival delay, minutes |
| carrier_delay / weather_delay / nas_delay / security_delay / late_aircraft_delay | Delay minutes attributed to each cause |

Derived columns added during cleaning (`utils/data_loader.py`):
`city`, `state`, `airport_full_name`, `date`, `delay_rate`,
`cancellation_rate`, `avg_arr_delay_min`, `airport_label`.

## How to run locally

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open the URL printed in the terminal (default
`http://127.0.0.1:8050`).

## How to deploy (Render)

1. Push this folder to a GitHub repo.
2. In Render, create a **Web Service** pointing at the repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:server`
5. No environment variables are required; the CSV ships inside
   `data/` so no external API keys are needed.

## AI usage

See the disclosure comment block at the top of `app.py`. Claude was
used to scaffold the multi-page structure, the data-cleaning steps,
and callback skeletons; all logic was reviewed andconfirmed against the
real data before submission.
