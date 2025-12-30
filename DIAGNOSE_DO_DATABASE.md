# Diagnose DigitalOcean Database Issue

## Problem: App Not Pulling Data

**Root Cause:** Your local database (SQLite) has data, but DigitalOcean is using PostgreSQL which is likely:
1. Empty (no data initialized)
2. Using wrong DATABASE_URL
3. Connection/permission issues

---

## Step 1: Check DigitalOcean Database Connection (2 minutes)

### Option A: Use Console (Fastest)

1. Go to: https://cloud.digitalocean.com/apps
2. Click on your app (shark-app or immigration)
3. Click **"Console"** tab
4. Click **"Run Command"**
5. Run this command:
   ```bash
   python test_db_connection.py
   ```

**What to look for:**
- ✅ If it shows "PostgreSQL" → Good, you're using the right DB type
- ✅ If it shows users/forms → Database has data
- ❌ If it shows "0 users" → Database is empty (need to initialize)
- ❌ If it shows "SQLite" → Wrong DATABASE_URL configured

---

### Option B: Check Environment Variables

1. In your app, go to **Settings** tab
2. Scroll to **Environment Variables**
3. Find `DATABASE_URL`
4. Click **"Show/Edit"**

**What should it look like?**
```
postgresql://username:password@host:port/database?sslmode=require
```

**Common Issues:**
- ❌ Still says `sqlite:///...` → You need to update it to PostgreSQL
- ❌ Says `postgres://...` instead of `postgresql://...` → Will cause errors with SQLAlchemy 1.4+
- ❌ Not set at all → You need to add it

---

## Step 2: Get Your PostgreSQL Connection String

### If you have a DigitalOcean Managed Database:

1. Go to: https://cloud.digitalocean.com/databases
2. Click on your database (dev-db-268120 or similar)
3. Click **"Connection Details"**
4. **IMPORTANT:** Select **"Connection Pooler"** from dropdown (not "Public network")
5. Copy the **connection string**
6. It should look like:
   ```
   postgresql://doadmin:AVNS_xxx@pooler-xxx.db.ondigitalocean.com:25061/defaultdb?sslmode=require
   ```

### If you DON'T have a database yet:

You need to create one first:

1. Go to: https://cloud.digitalocean.com/databases
2. Click **"Create Database"**
3. Choose:
   - Database: **PostgreSQL**
   - Version: **15** (latest stable)
   - Datacenter: **Same as your app** (check app settings)
   - Plan: **Basic** ($15/month) or **Development** ($7/month for testing)
4. Name: `immigration-db`
5. Click **"Create Database Cluster"**
6. Wait 2-3 minutes for it to provision
7. Once ready, follow "Get Connection String" above

---

## Step 3: Update DATABASE_URL in DigitalOcean

1. In your app → Settings → Environment Variables
2. Find `DATABASE_URL` (or click "Add Variable" if not exists)
3. Update/Set value to the **Connection Pooler string** from Step 2:
   ```
   postgresql://doadmin:AVNS_xxx@pooler-xxx.db.ondigitalocean.com:25061/defaultdb?sslmode=require
   ```
4. Click **"Save"**
5. App will automatically redeploy (wait 3-5 minutes)

---

## Step 4: Initialize the Database

Once the DATABASE_URL is set correctly:

### Option A: Run init_db.py via Console

1. Wait for deployment to complete (Step 3)
2. Go to Console tab
3. Run:
   ```bash
   python init_db.py
   ```

**Expected output:**
```
Creating database tables...
Database tables created successfully!
Successfully migrated 11 forms to database!
```

### Option B: Auto-initialization (if Console doesn't work)

Your app should auto-create tables on first run. Check Runtime Logs:

1. Go to **Runtime Logs** tab
2. Look for:
   ```
   Creating database tables...
   Database tables created successfully!
   ```

If you see errors instead:
- Check the error message
- Most common: "permission denied for schema public" → See Step 5

---

## Step 5: Fix Database Permissions (if needed)

If you get "permission denied" errors:

### Quick Fix: Use Connection Pooler

Make sure you're using the **Connection Pooler** string (not Public network). The pooler has proper permissions by default.

1. Database → Connection Details
2. Dropdown: Select **"Connection pooler"**
3. Copy that connection string
4. Update DATABASE_URL in app

### Manual Fix: Grant Permissions

If pooler doesn't work, grant permissions manually:

1. In database dashboard → Click **"Console"** or **"Open Console"**
2. Run these SQL commands:

```sql
-- Connect to your database
\c defaultdb

-- Check current user
SELECT current_user;

-- Grant all permissions
GRANT ALL PRIVILEGES ON SCHEMA public TO doadmin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO doadmin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO doadmin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO doadmin;
```

3. Then retry `python init_db.py` in your app console

---

## Step 6: Verify It's Working

After initialization:

1. Go to your app URL
2. Visit: `https://your-domain.com/`
3. You should see:
   - ✅ Immigration platform homepage
   - ✅ Forms library
   - ✅ File compressor in navigation
   - ✅ No errors

4. Check Runtime Logs for:
   ```
   ✓ Database connection successful
   ✓ Forms loaded: 11
   ```

---

## Step 7: Migrate Your Local Data (Optional)

If you need to move data from local SQLite to PostgreSQL:

### Option A: Export/Import Users Manually

Since you only have 2 test users, easier to recreate them manually in production.

### Option B: Use pg_dump (for larger datasets)

1. **Export local data:**
   ```bash
   # Convert SQLite to SQL
   sqlite3 immigration.db .dump > local_data.sql
   ```

2. **Import to PostgreSQL:**
   - This requires manual SQL conversion (SQLite → PostgreSQL syntax)
   - Not recommended for small datasets
   - Better to use Option A or just start fresh

---

## Common Scenarios

### Scenario 1: "No users found" in production

**This is NORMAL if:**
- This is your first deployment
- You haven't created any users in production yet

**Solution:**
1. Go to your app URL
2. Sign up with Clerk authentication
3. Create your first production user
4. Run diagnostic again - should now show 1 user

---

### Scenario 2: "Connection refused"

**Causes:**
- Database not running
- Wrong connection string
- Firewall/network issue

**Solution:**
1. Check database status in DO dashboard
2. Make sure database is "Running" (green status)
3. Use **Connection Pooler** string (not Public network)
4. Check database and app are in same datacenter region

---

### Scenario 3: Forms not showing up

**After running init_db.py, forms should auto-populate.**

Check in Console:
```bash
python -c "from app import app, db; from models import ImmigrationForm; app.app_context().push(); print(f'Forms: {ImmigrationForm.query.count()}')"
```

If shows 0:
```bash
python init_db.py
```

---

## Quick Diagnostic Checklist

Run through this in order:

- [ ] DATABASE_URL in DO points to PostgreSQL (not SQLite)
- [ ] DATABASE_URL uses Connection Pooler string
- [ ] Database status shows "Running"
- [ ] App deployed successfully (check Activity tab)
- [ ] Run `python test_db_connection.py` in Console
- [ ] If 0 users: Run `python init_db.py`
- [ ] Check Runtime Logs for errors
- [ ] Visit app URL - should work

---

## What's Happening Right Now?

**Your situation:**
- ✅ Local development: Working perfectly (SQLite with data)
- ❌ Production (DO): Either empty database or wrong connection

**Most likely cause:**
1. DATABASE_URL in DO not set or points to empty PostgreSQL
2. Need to run `init_db.py` to populate forms

**Time to fix:** 5-10 minutes

---

## Need Help?

Run the diagnostic and tell me:

1. What does `python test_db_connection.py` show in DO Console?
   - Database type?
   - Number of users?
   - Any errors?

2. What's in Settings → Environment Variables → DATABASE_URL?
   - sqlite:// or postgresql://?
   - Is it set at all?

3. Do you have a DigitalOcean Managed Database?
   - Yes, which one?
   - No, need to create it?

I'll help you fix it!
