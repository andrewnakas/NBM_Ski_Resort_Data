# NBM Ski Resort Snow Data Viewer

A real-time snow and precipitation forecast viewer for ski resorts using National Blend of Models (NBM) data.

## Features

- **Hourly Snow Accumulation** - Probabilistic hourly snowfall predictions (10%, 50%, 90%, 95%)
- **Running Total Snow** - Cumulative snowfall forecasts
- **Hourly Precipitation** - Combined rain and snow precipitation
- **Snow Level Forecast** - Wet-bulb zero elevation predictions
- **Cumulative Precipitation** - Total precipitation running totals

## Data Source

This application uses NBM GRIB2 data from NOAA's National Weather Service, providing probabilistic forecasts for ski resort locations across North America.

## Deployment

The site automatically builds and deploys to GitHub Pages when changes are pushed to the repository.

## Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Fetch NBM data:
   ```bash
   python scripts/fetch_nbm_data.py
   ```

3. Open `public/index.html` in a web browser

## License

MIT
