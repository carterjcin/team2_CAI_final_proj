# Flight Delay Explorer

A multi-page Dash app for exploring US domestic flight delays by
airport, carrier, and cause of delay.

## The question

**Which airline is the most reliable at your airport - and is it improving?**

## Who it's for

A frequent traveler deciding which carrier to
pick out of a specific airport.
## The data

- **Source**: US Department of Transportation / Bureau of
  Transportation Statistics, "Airline Delay Cause" extract
  (https://www.transtats.bts.gov/OT_Delay/OT_DelayCause1.asp)
- **Size**: 69,600 raw rows &rarr; ~69,500 after cleaning; one row per
  (year, month, carrier, airport); 370 airports, 21 carriers,
  June 2023 - June 2026 (36 months).
- **What was messy about it**: 51 rows were carrier/airport pairs
  BTS lists for a month with *zero* recorded flights - every numeric
  column was blank, which would have silently corrupted averages if
  left in, so they're dropped. The airport's city/state also only
  existed buried inside one free-text field, which had to be
  parsed apart with a regex before it could drive the state map.

## App structure

| Page | Route | What it shows |
|---|---|---|
| Home | `/` | Landing page with a short intro and a link into Overview. There is also a moving banner with different airline logos |
| Overview | `/overview` | US choropleth map of delay rate by state, filterable by year range and carrier |
| Comparison | `/comparison` | Ranked bar chart of carriers at one airport |
| Delay Causes | `/causes` | Pie + stacked bar breakdown of delay minutes by cause (carrier, weather, NAs, security, late aircraft) |


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

## How to view using Render

https://team2-cai-final-proj.onrender.com/

## AI usage

See the disclosure comment block at the top of `app.py`. Claude was
used to outline the multi-page structure, the data-cleaning steps,
and callback skeletons; all logic was reviewed prior to submission.