# FinSight — Financial Intelligence Dashboard

Streamlit + Supabase + Claude AI financial extraction and analytics dashboard.

## Quick Start

### Prerequisites

- Python 3.11+
- Supabase account (free tier)
- Anthropic API key (Claude Sonnet 4.5)
- GitHub account

### Local Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create `.streamlit/secrets.toml`** (Never commit this):
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   SUPABASE_DB_URL = "postgresql://postgres.REF:SENHA@aws-0-sa-east-1.pooler.supabase.com:5432/postgres"
   SUPABASE_URL = "https://REF.supabase.co"
   SUPABASE_KEY = "eyJ..."
   ```

3. **Set up Supabase database:**
   - Create account at supabase.com → New Project (South America region)
   - In SQL Editor, execute `sql/schema.sql`

4. **Populate with sample data:**
   ```bash
   python sql/seed.py
   ```

5. **Run locally:**
   ```bash
   streamlit run app.py
   ```

### Deploy to Streamlit Cloud

1. Push to GitHub:
   ```bash
   git add .
   git commit -m "feat: FinSight initial release"
   git push -u origin main
   ```

2. At share.streamlit.io:
   - "New app" → select repo, branch, and `app.py`
   - Advanced settings → Secrets → paste same 4 variables
   - Deploy

## File Structure

```
finsight/
├── app.py                    # Main entry
├── requirements.txt
├── .streamlit/
│   ├── config.toml          # UI theme
│   └── secrets.toml         # (Git ignored)
├── .gitignore
├── pages/
│   ├── 1_Dashboard.py       # Monthly financials
│   ├── 2_Importar.py        # PDF/XLSX upload
│   ├── 3_Metas.py           # Set targets
│   └── 4_Historico.py       # Upload history
├── lib/
│   ├── db.py                # Supabase + PostgreSQL
│   ├── extrator.py          # Claude extraction
│   ├── kpis.py              # KPI calculations
│   ├── alertas.py           # Alert rules
│   └── utils.py             # Format helpers
├── components/
│   ├── kpi_cards.py
│   ├── tabela_resumo.py
│   ├── grafico_evolucao.py
│   └── alertas_feed.py
└── sql/
    ├── schema.sql           # DB schema
    └── seed.py              # Sample data
```

## Cost Estimate

- Streamlit Cloud: **Free** (with limitations)
- Supabase: **Free tier** covers ~1K rows (12 months sample data)
- Claude API: ~$0.10 per PDF extraction (~$1–3/month)

**Total cost:** $0–5 USD for low-volume usage (< 20 uploads/month)

## Key Features

- 📊 Dashboard with 12-month KPI tracking
- 🤖 Automatic financial data extraction via Claude API
- 📈 Margin trends, expense analysis, cash flow alerts
- 🎯 Monthly targets vs actuals
- 🔔 Automatic alert generation
- 🗂️ Upload history + re-extraction capability

## Database

Single-tenant design (one empresa per deployment). Data model:
- **empresas:** Company metadata
- **metas:** Monthly targets
- **uploads:** PDF/XLSX document records
- **demonstrativos:** Extracted financial data (JSON)
- **kpis:** Calculated metrics
- **alertas:** Generated alerts

## Support

For issues or feature requests, open an issue on GitHub.
