# FinSight — Quick Start Guide

## Phase 1: Prerequisites (Cost: $0, Time: ~15 minutes)

### 1.1 Create Supabase Account & Project

1. Go to **https://supabase.com** → Click "Start your project"
2. Sign up with GitHub or email
3. Create a new project:
   - **Project name:** finsight (or any name)
   - **Database password:** Save securely (won't show again)
   - **Region:** South America (São Paulo) ← **IMPORTANT**
4. Wait for provisioning (~2 minutes)
5. When ready, you'll see the dashboard

### 1.2 Get Supabase Credentials

**Connection String (for DATABASE):**
- Go to **Settings** (⚙️ icon, bottom left)
- Click **Database**
- Under "Connection String", select **"Session mode"** (important, not Transaction)
- Copy the URI that looks like: `postgresql://postgres.XXXXX:PASSWORD@aws-0-sa-east-1.pooler.supabase.com:5432/postgres`
- Save as `SUPABASE_DB_URL`

**API Credentials:**
- Go to **Settings** → **API**
- Copy:
  - **Project URL** (e.g., `https://XXXXX.supabase.co`) → `SUPABASE_URL`
  - **anon public key** (long string starting with `eyJ...`) → `SUPABASE_KEY`

### 1.3 Get Claude API Key

1. Go to **https://console.anthropic.com**
2. Sign up / Log in
3. Navigate to **Account** → **API Keys**
4. Click **"Create New Key"**
5. Copy the key (starts with `sk-ant-...`) → `ANTHROPIC_API_KEY`
6. **Optional but recommended:** Set a usage budget cap to $5/month to avoid surprises

### 1.4 Install Git (if needed)

- Windows: Download from **https://git-scm.com** → Run installer
- Verify: Open PowerShell, run `git --version`

---

## Phase 2: Local Setup (Time: ~10 minutes)

### 2.1 Configure Secrets

1. Open folder: `finsight/.streamlit/`
2. Create new file: `secrets.toml` (start from `secrets.example.toml`)
3. Fill in the 4 values you copied above:

```toml
ANTHROPIC_API_KEY = "sk-ant-YOUR_KEY_HERE"
SUPABASE_DB_URL = "postgresql://postgres.XXX:YYY@aws-0-sa-east-1.pooler.supabase.com:5432/postgres"
SUPABASE_URL = "https://XXX.supabase.co"
SUPABASE_KEY = "eyJ..."
```

4. Save and **never commit this file** (already in .gitignore)

### 2.2 Install Python Dependencies

Open PowerShell in `finsight/` folder:

```powershell
pip install -r requirements.txt
```

Expected output: 9 packages installed (streamlit, anthropic, supabase, etc.)

---

## Phase 3: Database Setup (Time: ~5 minutes)

### 3.1 Create Database Schema

1. In Supabase Dashboard → **SQL Editor** (icon on left)
2. Click **"New Query"**
3. Open file `finsight/sql/schema.sql` in editor
4. Copy entire content → Paste into Supabase query box
5. Click **"Run"** (or Ctrl+Enter)
6. Should see: ✅ Success

**What was created:**
- 8 tables: empresas, metas, uploads, demonstrativos, kpis, alertas (+ 2 internal)
- 5 indexes for performance

### 3.2 Populate Sample Data

Run from PowerShell in `finsight/` folder:

```powershell
python sql/seed.py
```

Expected output:
```
Configurando banco de dados...
📝 Criando empresa ESG Now...
   ✅ Empresa criada: [UUID]
📊 Criando 12 meses de dados...
   ✅ 2025-03: R$ 410k faturamento, 54.9% margem
   ✅ 2025-04: R$ 440k faturamento, 55.7% margem
   ... (10 more months)
   ✅ 2026-02: R$ 558k faturamento, 61.7% margem

✅ Seed concluído com sucesso!
Agora execute: streamlit run app.py
```

---

## Phase 4: Test Locally (Time: ~5 minutes)

### 4.1 Start the Streamlit App

```powershell
cd finsight
streamlit run app.py
```

Browser should automatically open to `http://localhost:8501`

### 4.2 Verify All Pages Load

**Page 1: Dashboard (📈 Visão Geral)**
- Should show 12-month table with actual vs. meta
- KPI cards: Faturamento R$ 558.7k, Lucro R$ 344.7k, Margem 61.7%
- Chart showing trend
- 3-5 alerts at top

**Page 2: Importar (📄)**
- File uploader ready
- Dropdown for year, month, document type
- "Processar com IA" button

**Page 3: Metas (🎯)**
- Input fields for faturamento, despesas, resultado
- Save button

**Page 4: Histórico (🗂️)**
- Table showing 12 uploaded documents

✅ If all pages load → Local setup is complete!

---

## Phase 5: Deploy to Streamlit Cloud (Time: ~20 minutes)

### 5.1 Initialize Git Repository

```powershell
cd finsight
git init
git add .
git commit -m "feat: FinSight initial release"
```

**Verify secrets.toml NOT committed:**
```powershell
git ls-files | findstr "secrets"
```
Should return nothing or only `secrets.example.toml`

### 5.2 Create GitHub Repository

1. Go to **https://github.com/new**
2. Create repository:
   - **Name:** finsight
   - **Description:** Financial intelligence dashboard
   - **Visibility:** Public (required for free Streamlit tier)
   - Leave other options default
   - Click **"Create repository"**

3. In PowerShell:
```powershell
git remote add origin https://github.com/YOUR_USERNAME/finsight.git
git push -u origin main
```

### 5.3 Deploy to Streamlit Cloud

1. Go to **https://share.streamlit.io**
2. Sign in with GitHub account
3. Click **"New app"**
4. Configure:
   - **Repository:** YOUR_USERNAME/finsight
   - **Branch:** main
   - **App file:** app.py
5. Click **"Deploy"**

### 5.4 Set Environment Secrets in Cloud

While deployment is running:
1. Click **"Advanced settings"** (if not visible, wait for app to deploy first)
2. Click **"Secrets"** tab
3. Paste the same 4 secrets (copy-paste from `.streamlit/secrets.toml`):

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
SUPABASE_DB_URL = "postgresql://..."
SUPABASE_URL = "https://..."
SUPABASE_KEY = "eyJ..."
```

4. Click **"Save"** → App will restart automatically

### 5.5 Verify Cloud Deployment

When deployment finishes (~3 minutes):
- App URL will be shown: `https://YOUR_APP.streamlit.app`
- Open URL in browser
- Should see exact same dashboard as local version
- Try uploading a PDF/XLSX to verify Claude extraction works in cloud

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'streamlit'` | Run `pip install -r requirements.txt` |
| `"Nenhuma empresa cadastrada"` | Run `python sql/seed.py` |
| `ConnectionRefusedError` | Check SUPABASE_DB_URL in secrets.toml; use Session mode (5432), not Transaction (6543) |
| `Unauthorized` Claude extraction | Verify ANTHROPIC_API_KEY is correct; check budget in Anthropic console |
| `secrets.toml` committed to GitHub | Add to .gitignore; run `git rm --cached .streamlit/secrets.toml` then `git commit --amend` |
| App stuck on "Please wait..." | Streamlit recompiling; wait 30sec; if not fixed, restart with Ctrl+C then `streamlit run app.py` |

---

## What's Next?

Once cloud deployment works:

1. **Upload real financial documents** (PDF/XLSX) → Claude extracts data
2. **Set monthly targets** in Metas page
3. **Monitor alerts** on Dashboard (cash flow, margins, etc.)

### Optional Customizations

- Edit `lib/utils.py` to change currency formatting
- Modify alert rules in `lib/alertas.py`
- Add more KPIs in `lib/kpis.py`
- Change theme colors in `.streamlit/config.toml`

---

## Support

For issues:
1. Check `.streamlit/secrets.toml` exists locally (not on GitHub)
2. Verify Supabase schema was executed (8 tables in SQL Editor)
3. Test locally first before troubleshooting cloud deployment
4. Check terminal output for detailed error messages

**Estimated total time: 45 minutes from start to cloud deployment**
