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
import pygrib
import tempfile
import shutil
import time

# NOAA NBM GRIB2 data URL patterns
NBM_BASE_URL = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/blend/prod"

# Create output directories
os.makedirs('public/data', exist_ok=True)
os.makedirs('data/cache', exist_ok=True)


def get_latest_nbm_cycle():
    """Get the latest available NBM model run cycle."""
    now = datetime.utcnow()
    # NBM runs every 1 hour but we'll use the main 6-hourly cycles for consistency
    # Main cycles: 00, 06, 12, 18 UTC
    cycle_hour = (now.hour // 6) * 6
    cycle_time = now.replace(hour=cycle_hour, minute=0, second=0, microsecond=0)

    # Check if we need to go back one cycle (data may not be available yet)
    # NBM data typically available 1-2 hours after cycle time
    if (now - cycle_time).total_seconds() < 7200:  # Less than 2 hours old
        cycle_time -= timedelta(hours=6)

    return cycle_time


def download_nbm_file(cycle_time, forecast_hour):
    """
    Download a specific NBM GRIB2 file.

    Args:
        cycle_time: datetime of model run
        forecast_hour: forecast hour (1-72)

    Returns:
        Path to downloaded file or None if failed
    """
    date_str = cycle_time.strftime('%Y%m%d')
    hour_str = cycle_time.strftime('%H')

    # NBM file naming: blend.tCCz.core.fFFF.co.grib2
    # where CC is cycle hour and FFF is forecast hour
    filename = f"blend.t{hour_str}z.core.f{forecast_hour:03d}.co.grib2"
    url = f"{NBM_BASE_URL}/blend.{date_str}/{hour_str}/core/{filename}"

    cache_dir = 'data/cache'
    local_file = os.path.join(cache_dir, f"{date_str}_{hour_str}_{filename}")

    # Check if already cached
    if os.path.exists(local_file):
        print(f"  Using cached: {filename}")
        return local_file

    print(f"  Downloading: {filename}", end=' ', flush=True)
    try:
        response = requests.get(url, timeout=60, stream=True)
        response.raise_for_status()

        with open(local_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print("✓")
        return local_file
    except requests.exceptions.Timeout:
        print("✗ (timeout)")
        return None
    except Exception as e:
        print(f"✗ ({str(e)[:50]})")
        return None


def find_nearest_point(grb, target_lat, target_lon):
    """Find nearest grid point to target coordinates."""
    lats, lons = grb.latlons()

    # Handle longitude wrapping (convert negative to 0-360 if needed)
    if target_lon < 0:
        target_lon += 360
    lons = np.where(lons < 0, lons + 360, lons)

    # Calculate distances
    distances = np.sqrt((lats - target_lat)**2 + (lons - target_lon)**2)
    min_idx = np.unravel_index(np.argmin(distances), distances.shape)

    return min_idx


def extract_data_at_point(grib_file, lat, lon):
    """
    Extract forecast data at a specific location from GRIB2 file.

    Returns dict with snow, precip, and snow level data.
    """
    try:
        grbs = pygrib.open(grib_file)

        data = {
            'snow': {},      # Accumulated snow at different percentiles
            'precip': {},    # Accumulated precipitation
            'snow_level': {} # Height of 0C wet bulb (freezing level)
        }

        # NBM probabilistic forecast percentiles we want
        # 10th percentile = 10% chance of exceeding
        # 50th percentile = median
        # 90th percentile = 90% chance of exceeding

        for grb in grbs:
            var_name = grb.name
            idx = find_nearest_point(grb, lat, lon)
            value = grb.values[idx]

            # Snow accumulation (ASNOW)
            if 'Total snowfall' in var_name or 'ASNOW' in str(grb):
                try:
                    percentile = grb.percentile if hasattr(grb, 'percentile') else None
                    prob_type = grb.probabilityType if hasattr(grb, 'probabilityType') else None

                    if percentile == 10 or '10th percentile' in var_name:
                        data['snow']['p10'] = value
                    elif percentile == 50 or '50th percentile' in var_name or 'median' in var_name.lower():
                        data['snow']['p50'] = value
                    elif percentile == 90 or '90th percentile' in var_name:
                        data['snow']['p90'] = value
                    elif percentile == 95 or '95th percentile' in var_name:
                        data['snow']['p95'] = value
                except:
                    pass

            # Total precipitation (APCP)
            elif 'Total precipitation' in var_name or 'APCP' in str(grb):
                try:
                    percentile = grb.percentile if hasattr(grb, 'percentile') else None

                    if percentile == 10 or '10th percentile' in var_name:
                        data['precip']['p10'] = value
                    elif percentile == 50 or '50th percentile' in var_name or 'median' in var_name.lower():
                        data['precip']['p50'] = value
                    elif percentile == 90 or '90th percentile' in var_name:
                        data['precip']['p90'] = value
                    elif percentile == 95 or '95th percentile' in var_name:
                        data['precip']['p95'] = value
                except:
                    pass

            # Freezing level / Snow level (wet bulb zero height)
            elif 'Geopotential height' in var_name and '0C' in var_name:
                try:
                    percentile = grb.percentile if hasattr(grb, 'percentile') else None

                    if percentile == 10 or '10th percentile' in var_name:
                        data['snow_level']['p10'] = value
                    elif percentile == 50 or '50th percentile' in var_name or 'median' in var_name.lower():
                        data['snow_level']['p50'] = value
                    elif percentile == 90 or '90th percentile' in var_name:
                        data['snow_level']['p90'] = value
                    elif percentile == 95 or '95th percentile' in var_name:
                        data['snow_level']['p95'] = value
                except:
                    pass

        grbs.close()
        return data

    except Exception as e:
        print(f"  ✗ Error extracting data: {e}")
        return None


def fetch_nbm_grib_data(cycle_time, lat, lon):
    """
    Fetch NBM GRIB2 data for a specific location.

    Downloads forecast files at 3-hour intervals and interpolates hourly values.
    This is much faster than downloading all 72 hourly files.
    """
    print(f"Fetching NBM data for cycle: {cycle_time.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"Location: {lat}°N, {lon}°E")

    # Fetch forecasts every 3 hours (much faster than every hour)
    # We'll interpolate to get hourly values
    forecast_hours = list(range(1, 73, 3))  # 1, 4, 7, 10, ... 70
    print(f"Downloading {len(forecast_hours)} GRIB2 files (every 3 hours)...")

    # Storage for 3-hourly data
    three_hourly_data = []
    prev_snow = {'p10': 0, 'p50': 0, 'p90': 0, 'p95': 0}
    prev_precip = {'p10': 0, 'p50': 0, 'p90': 0, 'p95': 0}
    success_count = 0
    max_failures = 5
    failure_count = 0
    start_time = time.time()
    max_runtime = 480  # 8 minutes max

    for fhr in forecast_hours:
        # Check runtime - if taking too long, stop and use what we have
        if time.time() - start_time > max_runtime:
            print(f"\n⚠ Runtime limit reached, using {success_count} data points collected so far")
            break

        if failure_count >= max_failures:
            print(f"\n✗ Too many failures ({max_failures}), stopping downloads")
            break

        # Download GRIB file
        grib_file = download_nbm_file(cycle_time, fhr)

        if grib_file is None:
            failure_count += 1
            continue

        # Extract data
        data = extract_data_at_point(grib_file, lat, lon)

        if data and data['snow']:
            success_count += 1

            point_data = {
                'hour': fhr,
                'snow': {},
                'precip': {},
                'snow_level': {}
            }

            # Calculate 3-hourly increments from accumulated values
            for key in ['p10', 'p50', 'p90', 'p95']:
                # Snow (convert from kg/m² to mm, roughly 1:10 ratio for snow)
                acc_snow = data['snow'].get(key, prev_snow[key])
                three_hourly_val = max(0, acc_snow - prev_snow[key])
                point_data['snow'][key] = three_hourly_val * 10  # Convert to mm snow
                prev_snow[key] = acc_snow

                # Precipitation (convert from kg/m² to mm, 1:1 ratio)
                acc_precip = data['precip'].get(key, prev_precip[key])
                three_hourly_val = max(0, acc_precip - prev_precip[key])
                point_data['precip'][key] = three_hourly_val
                prev_precip[key] = acc_precip

                # Snow level (already in meters)
                point_data['snow_level'][key] = data['snow_level'].get(key, 2000)

            three_hourly_data.append(point_data)
        else:
            failure_count += 1

    print(f"\n✓ Successfully processed {success_count}/{len(forecast_hours)} forecast periods")

    # If we got too few data points, fall back to sample data
    if success_count < 5:
        print("✗ Insufficient real data, using sample data")
        return generate_sample_forecast_data()

    # Interpolate 3-hourly data to hourly
    print("Interpolating to hourly values...")
    timestamps = []
    hourly_snow = {'p10': [], 'p50': [], 'p90': [], 'p95': []}
    hourly_precip = {'p10': [], 'p50': [], 'p90': [], 'p95': []}
    snow_level = {'p10': [], 'p50': [], 'p90': [], 'p95': []}

    for i in range(72):  # Generate 72 hourly values
        hour = i + 1
        valid_time = cycle_time + timedelta(hours=hour)
        timestamps.append(valid_time.isoformat() + 'Z')

        # Find surrounding 3-hourly data points
        prev_idx = None
        next_idx = None

        for idx, point in enumerate(three_hourly_data):
            if point['hour'] <= hour:
                prev_idx = idx
            if point['hour'] >= hour and next_idx is None:
                next_idx = idx

        if prev_idx is not None and next_idx is not None and prev_idx != next_idx:
            # Interpolate between two points
            prev_point = three_hourly_data[prev_idx]
            next_point = three_hourly_data[next_idx]

            # Linear interpolation factor
            hour_diff = next_point['hour'] - prev_point['hour']
            factor = (hour - prev_point['hour']) / hour_diff if hour_diff > 0 else 0

            for key in ['p10', 'p50', 'p90', 'p95']:
                # Distribute 3-hourly totals evenly across hours for precip/snow
                hourly_snow[key].append(prev_point['snow'][key] / 3.0)
                hourly_precip[key].append(prev_point['precip'][key] / 3.0)

                # Interpolate snow level
                snow_val = prev_point['snow_level'][key] + factor * (next_point['snow_level'][key] - prev_point['snow_level'][key])
                snow_level[key].append(snow_val)
        elif prev_idx is not None:
            # Use previous point
            point = three_hourly_data[prev_idx]
            for key in ['p10', 'p50', 'p90', 'p95']:
                hourly_snow[key].append(point['snow'][key] / 3.0)
                hourly_precip[key].append(point['precip'][key] / 3.0)
                snow_level[key].append(point['snow_level'][key])
        else:
            # No data, use zeros
            for key in ['p10', 'p50', 'p90', 'p95']:
                hourly_snow[key].append(0)
                hourly_precip[key].append(0)
                snow_level[key].append(2000)

    forecast_data = {
        'generated': datetime.utcnow().isoformat() + 'Z',
        'model_run': cycle_time.isoformat() + 'Z',
        'source': 'NOAA National Blend of Models (NBM)',
        'location': {'lat': lat, 'lon': lon},
        'timestamps': timestamps,
        'hourlySnow': {k: [round(x, 2) for x in v] for k, v in hourly_snow.items()},
        'hourlyPrecip': {k: [round(x, 2) for x in v] for k, v in hourly_precip.items()},
        'snowLevel': {k: [round(x, 0) for x in v] for k, v in snow_level.items()}
    }

    return forecast_data


def generate_sample_forecast_data():
    """
    Generate sample forecast data as fallback.
    """
    hours = 72  # 3-day forecast
    timestamps = []
    now = datetime.utcnow()

    for i in range(hours):
        timestamp = now + timedelta(hours=i)
        timestamps.append(timestamp.isoformat() + 'Z')

    # Generate probabilistic snow data with realistic patterns
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

    # Snow level (wet-bulb zero height)
    base_snow_level = 2000
    snow_level_p10 = [base_snow_level + np.random.uniform(-200, 200) for _ in range(hours)]
    snow_level_p50 = [base_snow_level + 300 + np.random.uniform(-200, 200) for _ in range(hours)]
    snow_level_p90 = [base_snow_level + 600 + np.random.uniform(-200, 200) for _ in range(hours)]
    snow_level_p95 = [base_snow_level + 800 + np.random.uniform(-200, 200) for _ in range(hours)]

    forecast_data = {
        'generated': datetime.utcnow().isoformat() + 'Z',
        'model_run': get_latest_nbm_cycle().isoformat() + 'Z',
        'source': 'Sample Data (NBM unavailable)',
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


def main():
    """Main execution function."""
    print("=" * 70)
    print("NBM Ski Resort Data Fetcher")
    print("=" * 70)

    # Get latest model cycle
    cycle = get_latest_nbm_cycle()
    print(f"\nLatest NBM cycle: {cycle.strftime('%Y-%m-%d %H:%M UTC')}")

    # Default location: Vail, CO
    default_lat = 39.6403
    default_lon = -106.3742

    # Fetch and process data
    try:
        forecast_data = fetch_nbm_grib_data(cycle, default_lat, default_lon)

        # Save to JSON file
        output_file = 'public/data/forecast.json'
        with open(output_file, 'w') as f:
            json.dump(forecast_data, f, indent=2)

        print(f"\n✓ Forecast data saved to: {output_file}")
        print(f"✓ Forecast hours: {len(forecast_data['timestamps'])}")
        print(f"✓ Data source: {forecast_data['source']}")
        print(f"✓ Generated: {forecast_data['generated']}")

        # Print summary statistics
        total_snow_p50 = sum(forecast_data['hourlySnow']['p50'])
        total_snow_p90 = sum(forecast_data['hourlySnow']['p90'])

        print(f"\n3-Day Snow Forecast Summary:")
        print(f"  50th percentile: {total_snow_p50:.1f} mm")
        print(f"  90th percentile: {total_snow_p90:.1f} mm")

    except Exception as e:
        print(f"\n✗ Error fetching NBM data: {e}")
        print("Using fallback sample data...")
        import traceback
        traceback.print_exc()

        # Generate fallback data
        forecast_data = generate_sample_forecast_data()
        output_file = 'public/data/forecast.json'
        with open(output_file, 'w') as f:
            json.dump(forecast_data, f, indent=2)

        print(f"✓ Sample data saved to: {output_file}")

    # Clean up old cache files (keep only last 24 hours)
    try:
        cache_dir = 'data/cache'
        cutoff_time = datetime.utcnow() - timedelta(hours=24)

        for filename in os.listdir(cache_dir):
            filepath = os.path.join(cache_dir, filename)
            if os.path.isfile(filepath):
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                if file_time < cutoff_time:
                    os.remove(filepath)
                    print(f"Cleaned up old cache file: {filename}")
    except Exception as e:
        print(f"Cache cleanup warning: {e}")

    print("\n" + "=" * 70)
    print("Data fetch complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
