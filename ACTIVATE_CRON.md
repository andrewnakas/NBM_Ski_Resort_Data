# Activate Automatic Cron Downloads

## Current Status

Your NBM snow data viewer is ready! But the automatic cron schedule won't activate until the code is on the `main` branch.

**Current situation:**
- ✅ Code is on branch: `claude/make-github-016QS7Krep1mLSPp2tDqoFM6`
- ✅ Cron configured: Runs every 2 minutes
- ❌ Cron inactive: Only runs from `main` branch (GitHub Actions requirement)

## Quick Setup (2 methods)

### Method 1: Create Main Branch via GitHub UI (Recommended - 30 seconds)

1. **Go to your repository:**
   https://github.com/andrewnakas/NBM_Ski_Resort_Data

2. **Click "Branch: claude/make-github..." dropdown** (top left)

3. **Click "View all branches"**

4. **Find your branch and click the 3-dot menu** next to it

5. **Click "Set as default branch"** OR create a pull request and merge it

**OR even easier:**

1. Go to: https://github.com/andrewnakas/NBM_Ski_Resort_Data/tree/claude/make-github-016QS7Krep1mLSPp2tDqoFM6

2. Click **"Contribute"** button (top right, near the green "Code" button)

3. Click **"Open pull request"**

4. Title: "Add NBM Snow Data Viewer"

5. Click **"Create pull request"**

6. Click **"Merge pull request"**

7. Click **"Confirm merge"**

Done! Main branch created and cron activated.

### Method 2: Manual Branch Creation

```bash
# In your local terminal
git checkout claude/make-github-016QS7Krep1mLSPp2tDqoFM6
git pull origin claude/make-github-016QS7Krep1mLSPp2tDqoFM6

# Push to main (you may need repo admin access)
git push origin claude/make-github-016QS7Krep1mLSPp2tDqoFM6:main
```

## What Happens After Activation

Once on `main`, the cron schedule activates automatically:

### Automatic Download Schedule

- **Frequency:** Every hour at :15 past the hour
- **Downloads:** All 24 GRIB files per run
- **Duration:** ~30-45 minutes per run
- **Updates:** Site updates with complete dataset after each run

### Expected Behavior

```
00:15 UTC - Cron triggers
00:15 UTC - Downloads all 24 GRIB files
00:45 UTC - Processing complete, site deployed ✓
01:15 UTC - Next run starts (fresh data)
02:15 UTC - Next run starts
...
```

## Monitor Progress

**GitHub Actions:**
https://github.com/andrewnakas/NBM_Ski_Resort_Data/actions

**Live Site:**
https://andrewnakas.github.io/NBM_Ski_Resort_Data/

## Current Configuration

- ⏰ **Cron:** `15 * * * *` (hourly at :15)
- 📦 **Files per run:** 24 GRIB files (complete dataset)
- ⏱️ **Run timeout:** 60 minutes
- 💾 **State persistence:** GitHub Actions cache
- 🔄 **Auto-cleanup:** Old cache files removed after 24 hours

## Note on Download Strategy

This system downloads all 24 GRIB files in a single run:
- ✅ **Pros:** Complete dataset every hour, simple and reliable
- ⏱️ **Cons:** Each run takes 30-45 minutes
- 🎯 **Best for:** Hourly updates with complete fresh data

---

**Ready to activate?** Just merge to main using Method 1 above! 🚀
