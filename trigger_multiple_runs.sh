#!/bin/bash
# Script to trigger 24 workflow runs to quickly build complete NBM dataset
# Each run downloads 1 GRIB file, so 24 runs = complete 72-hour forecast

BRANCH="claude/make-github-016QS7Krep1mLSPp2tDqoFM6"
RUNS=24

echo "========================================="
echo "Triggering $RUNS workflow runs on branch: $BRANCH"
echo "========================================="

for i in $(seq 1 $RUNS); do
    echo "Triggering run $i/$RUNS..."
    gh workflow run deploy.yml --ref "$BRANCH"

    # Small delay to avoid rate limiting
    sleep 0.5
done

echo ""
echo "========================================="
echo "✓ All $RUNS workflow runs queued!"
echo "========================================="
echo ""
echo "Monitor progress at:"
echo "https://github.com/andrewnakas/NBM_Ski_Resort_Data/actions"
echo ""
echo "Expected completion time: ~90 minutes"
echo "(24 runs × ~3.5 min per run, running sequentially)"
echo ""
echo "Your site will update with each completed run:"
echo "https://andrewnakas.github.io/NBM_Ski_Resort_Data/"
