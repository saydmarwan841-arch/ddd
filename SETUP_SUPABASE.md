# 🚀 Complete Setup Guide: Romantic Love Quiz with Supabase + Vercel

## 📋 Quick Start Summary

Your app now uses **Supabase PostgreSQL** instead of JSON files. This means:
- ✅ Works 100% on Vercel (no filesystem limitations)
- ✅ Manage questions from any device
- ✅ Real database with automatic backups
- ✅ Scalable to thousands of users

**Setup time: ~15 minutes**

---

## **Step 1: Create Supabase Account**

### Option A: Using GitHub (Recommended)
1. Go to https://supabase.com
2. Click **Sign Up** button
3. Click **Continue with GitHub**
4. Authorize access

### Option B: Using Google or Email
1. Go to https://supabase.com
2. Click **Sign Up** 
3. Choose Google or Email option
4. Complete verification

---

## **Step 2: Create Project & Database**

### 2.1: Create Organization & Project

1. After signup, click **Create a new organization**
2. Name: `romantic-quiz` (or any name)
3. Click **Create organization**
4. Click **Create a new project**
5. Fill form:
   - **Project Name**: `romantic-quiz`
   - **Database Password**: Create strong password (SAVE THIS!)
   - **Region**: Choose closest:
     - 🇪🇺 Europe: `eu-west-1`
     - 🇺🇸 US: `us-west-1`
     - 🌏 Asia: `ap-southeast-1`
6. Click **Create new project**

⏳ Wait 2-3 minutes...

### 2.2: Create Database Table

1. Click **SQL Editor** (left sidebar)
2. Click **+ New Query**
3. Copy & paste:

```sql

CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    type VARCHAR(10) NOT NULL CHECK (type IN ('mcq', 'tf')),
    question TEXT NOT NULL,
    options JSONB NOT NULL,
    correct_answer TEXT NOT NULL,
    category VARCHAR(50) DEFAULT 'رومانسي',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_questions_id ON questions(id);

```

4. Click **Run** button
5. ✅ Should see: "Success. No rows returned"

---

## **Step 3: Get Connection String**

1. Click **Settings** → **Database**
2. Scroll to **Connection Strings**
3. Select **psycopg2** from dropdown
4. Click **Copy**

You'll get something like:
```
postgresql://postgres:your_password@abc123.supabase.co:5432/postgres
```

Keep this safe! This is your `DATABASE_URL`

---

## **Step 4: Set Up Vercel Environment Variables**

1. Go to https://vercel.com/dashboard
2. Click your project
3. **Settings** → **Environment Variables**
4. Add these variables (click **Add** for each):

| Name | Value |
|------|-------|
| `DATABASE_URL` | Your connection string from Step 3 |
| `ADMIN_PASSWORD` | `0000` |
| `FLASK_ENV` | `production` |

**Example DATABASE_URL**:
```
postgresql://postgres:MyPassword123!@abc123.supabase.co:5432/postgres
```

5. Click **Save**
6. Go to **Deployments** tab
7. Click **⋯** menu on latest deployment
8. Click **Redeploy**

---

## **Step 5: Local Testing (Optional)**

### Create .env file:

In your project folder, create `.env`:

```env
DATABASE_URL=postgresql://postgres:your_password@your_project.supabase.co:5432/postgres
ADMIN_PASSWORD=0000
FLASK_ENV=development
```

### Install dependencies:

```bash
pip install -r requirements.txt
```

### Run locally:

```bash
python app.py
```

Visit: http://localhost:5000

---

## **Step 6: Test on Production**

1. After Vercel redeploy completes
2. Visit your Vercel domain
3. Go to `/admin/login` with password `0000`
4. Add a test question
5. Check if it appears in the quiz

✅ **If it works, you're done!**

---

## **Verify Data in Supabase**

1. Supabase Dashboard
2. Click **Table Editor**
3. Click `questions` table
4. You should see your questions with:
   - ID (auto)
   - Type (mcq/tf)
   - Question text
   - Options (JSON array)
   - Correct answer
   - Category
   - Timestamps

---

## **Quick Troubleshooting**

### ❌ "Connection refused"
- Copy DATABASE_URL exactly (no extra spaces)
- Verify password is correct
- Check Supabase project is active

### ❌ "Table does not exist"
- Re-run SQL query in Supabase → SQL Editor
- Click **Run** button

### ❌ "DATABASE_URL not set"
- **Local**: Create `.env` file
- **Vercel**: Add to Environment Variables + Redeploy

### ❌ "Admin changes don't save"
- Check Vercel logs (Dashboard → Deployments → Logs)
- Verify DATABASE_URL in Vercel settings

### ❌ "Module psycopg2 not found"
```bash
pip install psycopg2-binary
pip install -r requirements.txt
```

---

## **Summary**

| Step | Task | Time |
|------|------|------|
| 1 | Create Supabase account | 2 min |
| 2 | Create database & table | 5 min |
| 3 | Get connection string | 1 min |
| 4 | Add to Vercel & redeploy | 5 min |
| 5 | Test | 2 min |

**Total: ~15 minutes**

---

## **What Changed in Your Code?**

### Before (JSON file):
- ❌ Stored data in `questions_ar.json`
- ❌ Couldn't write files on Vercel
- ❌ No backup/recovery

### After (PostgreSQL):
- ✅ Stores data in Supabase database
- ✅ Works perfectly on Vercel
- ✅ Auto-backups every day
- ✅ Can manage from any device

---

## **Key Files Updated**

- `app.py` - Now uses Supabase database
- `requirements.txt` - Added psycopg2 and python-dotenv
- `.env.example` - Shows what variables you need
- `SETUP_SUPABASE.md` - This detailed guide

---

## **Next Steps**

1. ✅ Add more questions
2. ✅ Customize admin panel
3. ✅ Add categories filter
4. ✅ Share quiz link
5. ✅ Monitor analytics

---

## **Support**

- Supabase Docs: https://supabase.com/docs
- Flask Docs: https://flask.palletsprojects.com/
- Vercel Docs: https://vercel.com/docs

**Your app is now production-ready! 🚀**
