# ⚡ Quick Reference: Environment Variables

## For Vercel (Settings → Environment Variables)

Add these 4 variables to your Vercel project:

```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@YOUR_PROJECT.supabase.co:5432/postgres
ADMIN_PASSWORD=0000
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_KEY=YOUR_ANON_KEY_HERE
FLASK_ENV=production
```

Then **REDEPLOY** your project!

---

## For Local Development (.env file)

Create `.env` in your project root:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@YOUR_PROJECT.supabase.co:5432/postgres
ADMIN_PASSWORD=0000
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_KEY=YOUR_ANON_KEY_HERE
FLASK_ENV=development
PORT=5000
```

**IMPORTANT**: Add `.env` to `.gitignore` so passwords don't get committed!

```
# .gitignore
.env
*.env
.env.local
```

---

## Getting Your Values

### DATABASE_URL
1. Go to Supabase Dashboard
2. Click **Settings** → **Database**
3. Scroll to **Connection Strings**
4. Select **psycopg2**
5. Copy the full URL

### SUPABASE_URL
1. Go to Supabase **Settings** → **API**
2. Copy the **Project URL** value

### SUPABASE_KEY
1. Go to Supabase **Settings** → **API**
2. Under **Project API keys**, copy the **anon** key (public key)

### ADMIN_PASSWORD
- Default: `0000`
- Change to something secure if deploying to production!

---

## Verification Checklist

- [ ] Supabase project created
- [ ] SQL table created in Supabase
- [ ] DATABASE_URL copied from connection string
- [ ] All 4 variables added to Vercel
- [ ] Vercel project redeployed
- [ ] Local .env file created (optional but recommended)
- [ ] Tested adding question via admin panel
- [ ] Verified question appears in Supabase Table Editor

✅ If all checked, you're ready to go!

---

## Troubleshooting

### Connection Refused
- Check DATABASE_URL is copied exactly (no extra spaces)
- Verify Supabase project is active

### Table Not Found
- Run SQL query again in Supabase SQL Editor
- Click **Run** button

### Changes Don't Save
- Check Vercel logs for errors
- Verify DATABASE_URL in Vercel settings
- Redeploy project

### Admin Password Not Working
- Add ADMIN_PASSWORD to Vercel environment variables
- Redeploy project

---

## What Each Variable Does

| Variable | Purpose | Example |
|----------|---------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:pass@host:5432/postgres` |
| `ADMIN_PASSWORD` | Password to access /admin panel | `0000` |
| `SUPABASE_URL` | Your Supabase project URL | `https://abc123.supabase.co` |
| `SUPABASE_KEY` | Public API key | `eyJhbGciOiJIUzI1NiI...` |
| `FLASK_ENV` | Environment (development/production) | `production` |

---

## Common Mistakes to Avoid

❌ Don't forget to **REDEPLOY** after adding env vars to Vercel
❌ Don't commit `.env` file to GitHub
❌ Don't share DATABASE_URL publicly
❌ Don't use weak passwords (min 12 characters)
❌ Don't forget to create the SQL table

---

## Next: Configure Vercel

1. Go to https://vercel.com/dashboard
2. Click your project
3. **Settings** → **Environment Variables**
4. Add the 4 variables above
5. **Deployments** → Click **⋯** on latest → **Redeploy**

Done! ✅

