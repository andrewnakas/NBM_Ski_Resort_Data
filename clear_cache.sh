#!/bin/bash
# Clear NBM data cache and state to force fresh downloads

echo "Clearing NBM data cache and state..."

# Remove cached GRIB files
if [ -d "data/cache" ]; then
    echo "Removing cached GRIB files..."
    rm -rf data/cache/*
    echo "✓ Cache cleared"
fi

# Remove download state
if [ -d "data/state" ]; then
    echo "Removing download state..."
    rm -rf data/state/*
    echo "✓ State cleared"
fi

# Remove generated forecast data
if [ -f "public/data/forecast.json" ]; then
    echo "Removing old forecast data..."
    rm -f public/data/forecast.json
    echo "✓ Old forecast removed"
fi

echo ""
echo "✓ All caches cleared!"
echo "Next run will download fresh GRIB files."
