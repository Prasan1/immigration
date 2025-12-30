# Quick Fix: App Not Pulling Data from Database

## TL;DR - 3 Minute Fix

Your **local database has data**, but **DigitalOcean PostgreSQL is empty or misconfigured**.

---

## Do This Right Now:

### 1. Check What Database DO is Using (30 seconds)

In DigitalOcean App:
1. Settings → Environment Variables
2. Look for `DATABASE_URL`

**Is it:**
- `sqlite:///...` → ❌ Wrong! Need PostgreSQL
- `postgresql://...` → ✅ Right type, but might be empty
- Not set? → ❌ Need to add it

---

### 2. Run Diagnostic in DO Console (1 minute)

1. Go to your DO app → **Console** tab
2. Run:
   ```bash
   python test_db_connection.py
   ```

**What does it say?**

#### If it shows "0 users, 0 forms":
Your database is **empty**. Fix:
```bash
python init_db.py
```
This creates tables and adds all 11 immigration forms.

#### If it shows error "No such file":
The diagnostic file isn't deployed yet. Push it:
```bash
git add test_db_connection.py
git commit -m "Add database diagnostic tool"
git push
```
Wait for deployment, then run diagnostic.

#### If it shows "SQLite":
You're using the wrong database! You need PostgreSQL in production.

#### If it shows connection errors:
DATABASE_URL is wrong or database isn't running.

---

### 3. Most Common Fix: Initialize Database

After verifying DATABASE_URL points to PostgreSQL:

```bash
# In DO Console:
python init_db.py
```

**Expected output:**
```
Creating database tables...
Database tables created successfully!
Successfully migrated 11 forms to database!
```

Then visit your app - should work!

---

## Still Not Working?

### Check DATABASE_URL Format

Should look like:
```
postgresql://user:password@host:25061/database?sslmode=require
```

**NOT:**
- `sqlite:///immigration.db` ❌
- `postgres://...` ❌ (should be postgresql://)

---

### Make Sure You Have a PostgreSQL Database

1. Go to: https://cloud.digitalocean.com/databases
2. Do you see a database?
   - **Yes:** Click it → Connection Details → Copy **Connection Pooler** string
   - **No:** Create one (see DIAGNOSE_DO_DATABASE.md)

---

### Update DATABASE_URL

1. App → Settings → Environment Variables
2. Set `DATABASE_URL` to your PostgreSQL connection string
3. Save (app will redeploy)
4. Wait 3 minutes
5. Run `python init_db.py` in Console

---

## Test If Fixed

Visit your app:
- Go to: `https://your-app-url.ondigitalocean.app/`
- Should see immigration platform (not errors)
- Forms library should load
- File compressor should work

---

## What You Need to Tell Me

To help you faster, run this and send me output:

**In DO Console:**
```bash
python test_db_connection.py
```

**OR tell me:**
1. What's your DATABASE_URL? (Settings → Environment Variables)
   - sqlite or postgresql?
2. Do you have a DO Managed Database?
   - Which one?
3. What error message do you see when visiting the app?

I'll tell you exactly what commands to run!

---

## Expected Timeline

- ✅ Database already exists: **2-3 minutes**
  - Update DATABASE_URL
  - Run init_db.py
  - Done

- ⚠️ Need to create database: **10-15 minutes**
  - Create DB in DO (5 min)
  - Update DATABASE_URL
  - Deploy (3-5 min)
  - Run init_db.py
  - Done

---

## Why This Happened

**Development:**
- You're using SQLite (file-based database)
- Works great for local testing
- Data stored in `immigration.db` file

**Production (DO):**
- Should use PostgreSQL (server-based database)
- SQLite doesn't work well on DO App Platform
- Need to configure DATABASE_URL to point to PostgreSQL
- Need to initialize it with `init_db.py`

This is **normal** for first deployment! Once fixed, works forever.
