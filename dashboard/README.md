# Airtel Network Intelligence Dashboard

## Run

From the project root, run:

```powershell
python -m streamlit run dashboard/app.py
```

The dashboard reads `data/raw/airtel.db` locally. In Streamlit Cloud, keep the database in private storage and add its HTTPS URL and optional bearer token to the app's **Settings → Secrets**; the app downloads and decompresses the archive into temporary storage on startup. Never commit the database or its access token. Use this Secrets configuration:

```toml
[database]
url = "https://your-private-storage.example/airtel.db.gz"
bearer_token = "YOUR_PRIVATE_BEARER_TOKEN"
version = "1"
```

The URL must return the gzip-compressed `airtel.db.gz` file. Leave `bearer_token` empty if the URL itself is a private signed URL. Increment `version` when replacing the database so the app fetches the new copy. The masthead uses a white Airtel wordmark. A full-height dark-red panel sits on the left and applies region, connection type, and device selections across both tabs; each chart also retains its own local **Filters** popover and lowercase chart-type label. White chart cards with red highlights keep the Airtel theme clear and consistent. Install `dashboard/requirements.txt` only if the active Python environment does not already provide Streamlit, Pandas, and Plotly:

```powershell
python -m pip install -r dashboard/requirements.txt
```

1. **Usage & demand** — every chart has its own independent region, connection, or device filters; includes monthly traffic, weekday rhythm, data-use distribution, and regional traffic mix.
2. **Service quality** — every chart has its own independent region, connection, or device filters; includes ticket resolution matrix, resolution-time accumulation, and region comparison.

Every chart has a descriptive title. Figures use interactive hover labels and compact heights intended to keep each tab on one screen at 100% browser zoom on a standard laptop display. Usage is observed from 1 January through 30 June 2025. Measures are descriptive; they do not establish causal effects.

## Chart choices

Polar line, violin, treemap, annotated heatmap, empirical CDF, and faceted bubble scatter provide distinct views beyond the existing project report figures (including a churn box plot and tenure figure).
