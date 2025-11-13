#!/usr/bin/env python3
"""
Fetch and process NBM GRIB2 data for ski resort forecasts.

This script downloads National Blend of Models (NBM) GRIB2 data from NOAA,
extracts probabilistic forecasts for snow, precipitation, and snow level,
and generates JSON data for the web visualization.
"""

import os
import json
import requests
from datetime import datetime, timedelta
import numpy as np

# NOAA NBM GRIB2 data URL patterns
NBM_BASE_URL = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/blend/prod"

# Create output directories
os.makedirs('public/data', exist_ok=True)
os.makedirs('data/cache', exist_ok=True)


def get_latest_nbm_cycle():
    """Get the latest available NBM model run cycle."""
    now = datetime.utcnow()
    # NBM runs every 6 hours: 00, 06, 12, 18 UTC
    cycle_hour = (now.hour // 6) * 6
    cycle_time = now.replace(hour=cycle_hour, minute=0, second=0, microsecond=0)

    # Check if we need to go back one cycle (data may not be available yet)
    if (now - cycle_time).seconds < 3600:  # Less than 1 hour old
        cycle_time -= timedelta(hours=6)

    return cycle_time


def generate_sample_forecast_data():
    """
    Generate sample forecast data for demonstration.
    In production, this would parse actual GRIB2 files.
    """
    hours = 72  # 3-day forecast
    timestamps = []
    now = datetime.utcnow()

    for i in range(hours):
        timestamp = now + timedelta(hours=i)
        timestamps.append(timestamp.isoformat() + 'Z')

    # Generate probabilistic snow data with realistic patterns
    # Simulate a storm system passing through
    storm_peak = 24  # Hour of peak snowfall

    def snow_pattern(hour, percentile_factor):
        """Generate realistic snow pattern with storm peak."""
        distance_from_peak = abs(hour - storm_peak)
        base_intensity = max(0, 15 - distance_from_peak) * percentile_factor
        variation = np.random.normal(0, 1) * percentile_factor
        return max(0, base_intensity + variation)

    hourly_snow_p10 = [snow_pattern(h, 0.2) for h in range(hours)]
    hourly_snow_p50 = [snow_pattern(h, 0.6) for h in range(hours)]
    hourly_snow_p90 = [snow_pattern(h, 1.2) for h in range(hours)]
    hourly_snow_p95 = [snow_pattern(h, 1.5) for h in range(hours)]

    # Precipitation includes both snow and rain
    hourly_precip_p10 = [max(s * 1.1, s + np.random.uniform(0, 1)) for s in hourly_snow_p10]
    hourly_precip_p50 = [max(s * 1.2, s + np.random.uniform(0, 2)) for s in hourly_snow_p50]
    hourly_precip_p90 = [max(s * 1.3, s + np.random.uniform(0, 3)) for s in hourly_snow_p90]
    hourly_precip_p95 = [max(s * 1.4, s + np.random.uniform(0, 4)) for s in hourly_snow_p95]

    # Snow level (wet-bulb zero height) - varies with temperature
    base_snow_level = 2000
    snow_level_p10 = [base_snow_level + np.random.uniform(-200, 200) for _ in range(hours)]
    snow_level_p50 = [base_snow_level + 300 + np.random.uniform(-200, 200) for _ in range(hours)]
    snow_level_p90 = [base_snow_level + 600 + np.random.uniform(-200, 200) for _ in range(hours)]
    snow_level_p95 = [base_snow_level + 800 + np.random.uniform(-200, 200) for _ in range(hours)]

    forecast_data = {
        'generated': datetime.utcnow().isoformat() + 'Z',
        'model_run': get_latest_nbm_cycle().isoformat() + 'Z',
        'source': 'NBM (Sample Data)',
        'timestamps': timestamps,
        'hourlySnow': {
            'p10': [round(x, 2) for x in hourly_snow_p10],
            'p50': [round(x, 2) for x in hourly_snow_p50],
            'p90': [round(x, 2) for x in hourly_snow_p90],
            'p95': [round(x, 2) for x in hourly_snow_p95]
        },
        'hourlyPrecip': {
            'p10': [round(x, 2) for x in hourly_precip_p10],
            'p50': [round(x, 2) for x in hourly_precip_p50],
            'p90': [round(x, 2) for x in hourly_precip_p90],
            'p95': [round(x, 2) for x in hourly_precip_p95]
        },
        'snowLevel': {
            'p10': [round(x, 0) for x in snow_level_p10],
            'p50': [round(x, 0) for x in snow_level_p50],
            'p90': [round(x, 0) for x in snow_level_p90],
            'p95': [round(x, 0) for x in snow_level_p95]
        }
    }

    return forecast_data


def fetch_nbm_grib_data(cycle_time, lat, lon):
    """
    Fetch NBM GRIB2 data for a specific location.

    This is a placeholder for actual GRIB2 data fetching.
    Real implementation would use pygrib or cfgrib to parse GRIB2 files.
    """
    # In production, this would:
    # 1. Download GRIB2 files from NOAA
    # 2. Extract data for specific lat/lon
    # 3. Parse probabilistic forecasts
    # 4. Return structured data

    print(f"Fetching NBM data for cycle: {cycle_time}")
    print(f"Location: {lat}, {lon}")

    # For now, use sample data
    return generate_sample_forecast_data()


def main():
    """Main execution function."""
    print("=" * 60)
    print("NBM Ski Resort Data Fetcher")
    print("=" * 60)

    # Get latest model cycle
    cycle = get_latest_nbm_cycle()
    print(f"\nLatest NBM cycle: {cycle.strftime('%Y-%m-%d %H:%M UTC')}")

    # For this demo, we'll use a representative location
    # In production, you could fetch data for multiple resorts
    default_lat = 39.6403  # Vail, CO
    default_lon = -106.3742

    print(f"Fetching data for location: {default_lat}, {default_lon}")

    # Fetch and process data
    try:
        forecast_data = fetch_nbm_grib_data(cycle, default_lat, default_lon)

        # Save to JSON file
        output_file = 'public/data/forecast.json'
        with open(output_file, 'w') as f:
            json.dump(forecast_data, f, indent=2)

        print(f"\n✓ Forecast data saved to: {output_file}")
        print(f"✓ Forecast hours: {len(forecast_data['timestamps'])}")
        print(f"✓ Generated: {forecast_data['generated']}")

        # Print summary statistics
        total_snow_p50 = sum(forecast_data['hourlySnow']['p50'])
        total_snow_p90 = sum(forecast_data['hourlySnow']['p90'])

        print(f"\n3-Day Snow Forecast Summary:")
        print(f"  50th percentile: {total_snow_p50:.1f} mm")
        print(f"  90th percentile: {total_snow_p90:.1f} mm")

    except Exception as e:
        print(f"\n✗ Error fetching data: {e}")
        print("Using fallback sample data...")

        # Generate fallback data
        forecast_data = generate_sample_forecast_data()
        output_file = 'public/data/forecast.json'
        with open(output_file, 'w') as f:
            json.dump(forecast_data, f, indent=2)

        print(f"✓ Sample data saved to: {output_file}")

    print("\n" + "=" * 60)
    print("Data fetch complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
