# 🔮 Utility Crystal Ball

**Advanced utility consumption forecasting platform**

Developed by **Engr. Ahmed Raslan**
✉ Engr_Raslan@outlook.com | 📞 +971 52 289 9595

---

## What it does

Forecasts consumption for:
- ⚡ Electricity (MW)
- 💧 Water (m³)
- 🔥 Gas (m³)
- ❄️ District Cooling (TonHr)
- ♻️ TSE (m³)

Using an **ensemble of Prophet + SARIMA** models with:
- Multi-zone support (unlimited zones)
- 3 forecast scenarios (base / optimistic / conservative)
- Automatic backtesting & MAPE accuracy
- AI-powered insights (optional Anthropic API key)
- Excel report export
- Data validation with 3-gate system

---

## How to run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## How to deploy on Streamlit Cloud

1. Push this folder to a GitHub repository
2. Go to share.streamlit.io
3. Connect your GitHub repo
4. Set main file: `app.py`
5. Deploy — done!

---

## Data template format

| Date       | Zone_1 | Zone_2 | Zone_N |
|------------|--------|--------|--------|
| 2019-01-01 | 1540.2 | 823.5  | ...    |
| 2019-02-01 | 1623.1 | 791.0  | ...    |

- Minimum 36 months required
- 60+ months recommended for best accuracy
- Add as many zone columns as needed

---

## Requirements

- Python 3.9+
- See requirements.txt for full list
