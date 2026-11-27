# Pre-Launch Debug Checklist for Vibe-Coded Apps (Cursor / Lovable / Bolt / Replit)

Use this checklist before shipping an AI-generated web application to production:

1. **Environment & Secrets**
   - Verify `.env` is listed in `.gitignore`.
   - Confirm no `NEXT_PUBLIC_*` or `VITE_*` variables contain private server API keys.
   - Run `python env_security_audit.py .`.
2. **Auth & Database (Supabase / PostgreSQL / Firebase)**
   - Confirm Row Level Security (RLS) policies are enabled on every user table.
   - Verify redirect URLs match your production domain (Vercel / Netlify).
3. **API & Webhook Reliability**
   - Add explicit error handling (`try/catch`) and HTTP status checks on external API calls.
   - Validate incoming request payloads before writing to the database.
4. **Build & Deployment**
   - Run a clean production build (`npm run build` or `pytest`) locally before deploying.
