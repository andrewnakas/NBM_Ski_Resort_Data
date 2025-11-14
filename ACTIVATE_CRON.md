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

- **Frequency:** Every 2 minutes
- **Downloads:** 1 GRIB file per run
- **Timeline:** All 24 files downloaded in ~50-60 minutes
- **Updates:** Site updates after each successful download

### Expected Behavior

```
00:00 UTC - Cron triggers
00:02 UTC - Run 1 completes (file 1/24)
00:04 UTC - Run 2 completes (file 2/24)
00:06 UTC - Run 3 completes (file 3/24)
...
00:48 UTC - Run 24 completes (file 24/24) ✓
00:50 UTC - Continues downloading from new cycle...
```

## Monitor Progress

**GitHub Actions:**
https://github.com/andrewnakas/NBM_Ski_Resort_Data/actions

**Live Site:**
https://andrewnakas.github.io/NBM_Ski_Resort_Data/

## Current Configuration

- ⏰ **Cron:** `*/2 * * * *` (every 2 minutes)
- 📦 **Files per run:** 1 GRIB file
- ⏱️ **Run timeout:** 3 minutes
- 💾 **State persistence:** GitHub Actions cache
- 🔄 **Auto-cleanup:** Old cache files removed after 24 hours

## Future Adjustments (Optional)

If you want to change the download frequency later:

**Slower (hourly updates):**
```yaml
cron: '15 * * * *'  # Once per hour at :15
```

**Faster (every minute - max speed):**
```yaml
cron: '* * * * *'  # Every minute
```

Edit `.github/workflows/deploy.yml` line 11 and push to main.

---

**Ready to activate?** Just merge to main using Method 1 above! 🚀
