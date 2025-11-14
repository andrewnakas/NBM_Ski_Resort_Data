# Revert Cron Schedule to Hourly

Once all 24 GRIB files are downloaded, revert the cron schedule back to hourly updates.

## Check Progress

Monitor at: https://github.com/andrewnakas/NBM_Ski_Resort_Data/actions

Look for the workflow run that shows:
```
Progress: 24/24 files downloaded
✓ All files already downloaded for this cycle!
```

## Revert Instructions

Once you see 24/24 files downloaded, change the cron schedule back:

### Option 1: Via GitHub Web UI

1. Go to: `.github/workflows/deploy.yml`
2. Click "Edit" (pencil icon)
3. Find line ~11 with: `- cron: '*/5 * * * *'`
4. Change to: `- cron: '15 * * * *'`
5. Update comment to: `# Run every hour at minute 15`
6. Commit directly to the branch

### Option 2: Via Git Command Line

```bash
# Edit the file
nano .github/workflows/deploy.yml

# Change this line:
    - cron: '*/5 * * * *'

# To this:
    - cron: '15 * * * *'

# Commit and push
git add .github/workflows/deploy.yml
git commit -m "Revert cron to hourly updates after dataset complete"
git push
```

## Result

After reverting:
- Workflow runs once per hour at :15 past the hour
- Downloads latest NBM data
- Keeps your forecast up to date
- No manual intervention needed
