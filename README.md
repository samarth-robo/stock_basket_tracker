# Stock Basket Tracker

Simple tool that allows you to track the price of a weighted basket of stocks.

|![teaser](teaser.png)|
-

## Setup
- Get [Miniconda](https://docs.conda.io/en/latest/miniconda.html). Then:
```bash
(base) $ git clone https://github.com/samarth-robo/stock_basket_tracker.git
(base) $ cd stock_basket_tracker 
(base) $ conda env create -f environment.yml
(base) $ conda activate stock_basket_tracker
```

# Run the App

The app has a simple interface. Supply a JSON with a dict of ticker names and
weights.

```bash
(stock_basket_tracker) $ python show_history.py --help
usage: show_history.py [-h] -f TICKER_NAMES_FILE [--start_year START_YEAR]

optional arguments:
  -h, --help            show this help message and exit
  -f TICKER_NAMES_FILE, --ticker_names_file TICKER_NAMES_FILE
  --start_year START_YEAR
```

Run it with an example basket that is included:

```bash
(stock_basket_tracker) $ python show_history.py -f example_basket.json 
Normalizing basket fractions
Getting MSFT data
Getting AAPL data
Getting INDA data
Go to http://localhost:8050
Dash is running on http://127.0.0.1:8050/

 * Serving Flask app "app" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:8050/ (Press CTRL+C to quit)
```

The app will be live at [http://localhost:8050](http://localhost:8050).