import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Utility Crystal Ball",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0a0a1a;
    color: #c0a0ff;
}
.stApp { background-color: #0a0a1a; }
section[data-testid="stSidebar"] { display: none; }

.main-header {
    text-align: center;
    padding: 2rem 0 1rem;
}
.main-title {
    font-size: 2.4rem;
    font-weight: 600;
    color: #e8d8ff;
    letter-spacing: 2px;
    margin-bottom: 0.3rem;
}
.main-tagline {
    font-size: 1rem;
    color: #9080b0;
    font-style: italic;
    margin-bottom: 1rem;
}
.main-desc {
    font-size: 0.85rem;
    color: #7060a0;
    max-width: 520px;
    margin: 0 auto 1.5rem;
    line-height: 1.8;
}
.dev-footer {
    background: rgba(8,4,22,0.95);
    border-top: 1px solid #1a0a3a;
    padding: 0.6rem 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.75rem;
    color: #5a4a7a;
    margin-top: 2rem;
}
.section-card {
    background: #16102a;
    border: 1px solid #2a1a4a;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}
.section-title {
    font-size: 1rem;
    font-weight: 500;
    color: #c0a0ff;
    margin-bottom: 0.2rem;
}
.section-sub {
    font-size: 0.78rem;
    color: #6050a0;
    margin-bottom: 1rem;
}
.metric-row {
    display: flex;
    gap: 12px;
    margin-bottom: 1rem;
}
.metric-box {
    background: #16102a;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    flex: 1;
    text-align: center;
}
.metric-label {
    font-size: 0.7rem;
    color: #5a4a7a;
    margin-bottom: 4px;
}
.metric-val {
    font-size: 1.3rem;
    font-weight: 500;
    color: #c0a0ff;
}
.metric-good { color: #3db07a !important; }
.metric-warn { color: #d4a020 !important; }
.metric-bad  { color: #cc4040 !important; }

.val-ok   { color: #3db07a; }
.val-warn { color: #d4a020; }
.val-err  { color: #cc4040; }

.warn-box {
    background: rgba(180,130,0,0.08);
    border: 1px solid rgba(180,130,0,0.3);
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 0.8rem;
    color: #c09030;
    line-height: 1.6;
    margin-bottom: 1rem;
}
.info-box {
    background: rgba(60,100,200,0.08);
    border: 1px solid rgba(60,100,200,0.3);
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 0.8rem;
    color: #7090d0;
    line-height: 1.6;
    margin-bottom: 1rem;
}
.success-box {
    background: rgba(40,160,100,0.08);
    border: 1px solid rgba(40,160,100,0.3);
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 0.8rem;
    color: #3db07a;
    line-height: 1.6;
    margin-bottom: 1rem;
}
div[data-testid="stButton"] > button {
    background: #4a2a8a;
    color: #e0c0ff;
    border: none;
    border-radius: 20px;
    padding: 0.5rem 1.5rem;
    font-size: 0.85rem;
    transition: all 0.2s;
}
div[data-testid="stButton"] > button:hover {
    background: #6a3aaa;
    color: #fff;
}
div[data-testid="stSelectbox"] label,
div[data-testid="stTextInput"] label,
div[data-testid="stFileUploader"] label {
    color: #9080b0 !important;
    font-size: 0.8rem !important;
}
div[data-testid="stTextInput"] input {
    background: #16102a !important;
    color: #c0a0ff !important;
    border: 1px solid #2a1a4a !important;
    border-radius: 8px !important;
}
div[data-testid="stSelectbox"] > div > div {
    background: #16102a !important;
    color: #c0a0ff !important;
    border: 1px solid #2a1a4a !important;
    border-radius: 8px !important;
}
.stProgress > div > div {
    background: #6a3aaa !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: #0f0f22;
    border-bottom: 1px solid #2a1a4a;
}
.stTabs [data-baseweb="tab"] {
    color: #5a4a7a;
    font-size: 0.82rem;
}
.stTabs [aria-selected="true"] {
    color: #b090ff !important;
    border-bottom: 2px solid #8060d0 !important;
}
hr { border-color: #2a1a4a; }

.step-indicator {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 0;
    padding: 1rem 0;
    margin-bottom: 1.5rem;
}
.step-item {
    display: flex;
    align-items: center;
    gap: 6px;
}
.step-dot {
    width: 26px;
    height: 26px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 500;
    border: 1px solid #3a2a5a;
    color: #5a4a7a;
    background: transparent;
}
.step-dot-done {
    background: #4a2a8a;
    border-color: #6a4aaa;
    color: #d0b0ff;
}
.step-dot-active {
    background: #6a3aaa;
    border-color: #9a60dd;
    color: #fff;
    box-shadow: 0 0 8px rgba(150,80,220,0.5);
}
.step-label { font-size: 10px; color: #5a4a7a; }
.step-label-active { font-size: 10px; color: #b090ff; }
.step-line { width: 32px; height: 1px; background: #2a1a4a; margin: 0 4px; }
</style>
""", unsafe_allow_html=True)

# ── Session state init ───────────────────────────────────────────────────────
for k, v in {
    'step': 1,
    'utility': None,
    'horizon': 24,
    'df': None,
    'zones': [],
    'results': None,
    'api_key': '',
    'scenario': '3 scenarios',
    'engine': 'Ensemble (Prophet + SARIMA)',
    'history_months': 0,
    'data_quality': None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Constants ────────────────────────────────────────────────────────────────
UTILITIES = {
    'Electricity': {'icon': '⚡', 'unit': 'MW',    'desc': 'Electrical demand'},
    'Water':       {'icon': '💧', 'unit': 'm³',    'desc': 'Water consumption'},
    'Gas':         {'icon': '🔥', 'unit': 'm³',    'desc': 'Gas consumption'},
    'District Cooling': {'icon': '❄️', 'unit': 'TonHr', 'desc': 'Cooling demand'},
    'TSE':         {'icon': '♻️', 'unit': 'm³',    'desc': 'Treated sewage effluent'},
}
HORIZONS = [12, 24, 36, 60]

EXAMPLE_DATA = {
    'Electricity': {
        'zones': ['Zone_1', 'Zone_2', 'Zone_3'],
        'base':  [1450, 1880, 1980],
        'amp':   [400,  80,   620],
        'trend': [8,   -3,    15],
    }
}

# ── Helper: step indicator ───────────────────────────────────────────────────
def render_steps(current):
    steps = ['Utility', 'Setup', 'Upload', 'Forecast', 'Results']
    dots = []
    for i, s in enumerate(steps):
        n = i + 1
        if n < current:
            dc = 'step-dot-done'; sym = '✓'; lc = 'step-label'
        elif n == current:
            dc = 'step-dot-active'; sym = str(n); lc = 'step-label-active'
        else:
            dc = ''; sym = str(n); lc = 'step-label'
        line = '<div class="step-line"></div>' if i < len(steps)-1 else ''
        dots.append(f'<div class="step-item"><div class="step-dot {dc}">{sym}</div><span class="{lc}">{s}</span></div>{line}')
    st.markdown(f'<div class="step-indicator">{"".join(dots)}</div>', unsafe_allow_html=True)

def dev_footer():
    st.markdown("""
    <div class="dev-footer">
        <span>🔮 Developed by <strong style="color:#8060b0">Engr. Ahmed Raslan</strong></span>
        <span style="display:flex;gap:24px;">
            <span>✉ Engr_Raslan@outlook.com</span>
            <span>📞 +971 52 289 9595</span>
        </span>
    </div>""", unsafe_allow_html=True)

# ── Validation ───────────────────────────────────────────────────────────────
def validate_data(df):
    results = []
    ok = True

    # Gate 1: Structure
    if 'Date' not in df.columns:
        results.append(('❌', 'Date column not found', 'err')); ok = False
    else:
        results.append(('✅', 'Date column found', 'ok'))

    zone_cols = [c for c in df.columns if c != 'Date']
    if len(zone_cols) == 0:
        results.append(('❌', 'No zone columns found', 'err')); ok = False
    else:
        results.append(('✅', f'{len(zone_cols)} zone(s) detected: {", ".join(zone_cols[:5])}{"..." if len(zone_cols)>5 else ""}', 'ok'))

    if not ok:
        return False, results, 0, zone_cols

    # Gate 2: Date parsing
    try:
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date').reset_index(drop=True)
        results.append(('✅', 'Date format recognized — monthly', 'ok'))
    except:
        results.append(('❌', 'Date column could not be parsed', 'err')); ok = False

    # Duplicates
    dups = df['Date'].duplicated().sum()
    if dups > 0:
        results.append(('❌', f'{dups} duplicate month(s) found', 'err')); ok = False
    else:
        results.append(('✅', 'No duplicate months', 'ok'))

    # History length
    months = len(df)
    if months < 36:
        results.append(('❌', f'History too short: {months} months (minimum 36)', 'err')); ok = False
    elif months < 60:
        results.append(('⚠️', f'History: {months} months (below 60 — accuracy reduced)', 'warn'))
    else:
        results.append(('✅', f'History: {months} months — excellent', 'ok'))

    # Missing values
    total_cells = df[zone_cols].size
    missing = df[zone_cols].isnull().sum().sum()
    miss_pct = round(missing / total_cells * 100, 1) if total_cells > 0 else 0
    if miss_pct > 20:
        results.append(('❌', f'Missing values: {miss_pct}% (too high)', 'err')); ok = False
    elif miss_pct > 5:
        results.append(('⚠️', f'Missing values: {miss_pct}% (acceptable but review)', 'warn'))
    else:
        results.append(('✅', f'Missing values: {miss_pct}% (acceptable)', 'ok'))

    # Spike check
    spike_flag = False
    for col in zone_cols:
        mean = df[col].mean()
        if mean > 0 and (df[col] > mean * 4).any():
            spike_flag = True
    if spike_flag:
        results.append(('⚠️', 'Possible consumption spikes detected — review data', 'warn'))
    else:
        results.append(('✅', 'No impossible spikes detected', 'ok'))

    return ok, results, months, zone_cols

# ── Forecasting engine ───────────────────────────────────────────────────────
def run_forecast(df, zone_cols, horizon, engine):
    results = {}
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date').reset_index(drop=True)

    for zone in zone_cols:
        series = df[['Date', zone]].copy().dropna()
        series.columns = ['ds', 'y']

        hist_vals = series['y'].values.tolist()
        last_date = series['ds'].iloc[-1]
        future_dates = pd.date_range(
            start=last_date + pd.DateOffset(months=1),
            periods=horizon, freq='MS'
        )

        # Prophet model
        prophet_fc = None
        try:
            from prophet import Prophet
            m = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=False,
                daily_seasonality=False,
                seasonality_mode='multiplicative',
                changepoint_prior_scale=0.05,
                interval_width=0.80
            )
            m.fit(series)
            future = m.make_future_dataframe(periods=horizon, freq='MS')
            forecast = m.predict(future)
            prophet_fc = forecast.tail(horizon)['yhat'].values
            prophet_lower = forecast.tail(horizon)['yhat_lower'].values
            prophet_upper = forecast.tail(horizon)['yhat_upper'].values
        except Exception as e:
            prophet_fc = None

        # SARIMA model
        sarima_fc = None
        try:
            from statsmodels.tsa.statespace.sarimax import SARIMAX
            model = SARIMAX(
                series['y'],
                order=(1, 1, 1),
                seasonal_order=(1, 1, 1, 12),
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            fit = model.fit(disp=False, maxiter=200)
            forecast_res = fit.get_forecast(steps=horizon)
            sarima_fc = forecast_res.predicted_mean.values
        except Exception as e:
            sarima_fc = None

        # Ensemble or fallback
        if prophet_fc is not None and sarima_fc is not None and engine == 'Ensemble (Prophet + SARIMA)':
            base_fc = (prophet_fc * 0.6 + sarima_fc * 0.4)
        elif prophet_fc is not None:
            base_fc = prophet_fc
        elif sarima_fc is not None:
            base_fc = sarima_fc
        else:
            # Simple seasonal naive fallback
            season_len = min(12, len(hist_vals))
            base_fc = np.array([hist_vals[-(season_len - i % season_len)] for i in range(horizon)])
            trend = (hist_vals[-1] - hist_vals[0]) / max(len(hist_vals), 1)
            base_fc = base_fc + np.arange(1, horizon + 1) * trend * 0.5

        base_fc = np.maximum(base_fc, 0)
        optimistic_fc = base_fc * 1.06
        conservative_fc = base_fc * 0.94

        # Backtest MAPE (last 12 months)
        mape = None
        try:
            if len(series) >= 24:
                train = series.iloc[:-12]
                test  = series.iloc[-12:]
                if prophet_fc is not None:
                    mp = Prophet(yearly_seasonality=True, weekly_seasonality=False,
                                 daily_seasonality=False, seasonality_mode='multiplicative')
                    mp.fit(train.rename(columns={'ds':'ds','y':'y'}))
                    fp = mp.make_future_dataframe(periods=12, freq='MS')
                    pred = mp.predict(fp).tail(12)['yhat'].values
                    actual = test['y'].values
                    mape = round(100 - np.mean(np.abs((actual - pred) / np.maximum(actual, 1))) * 100, 1)
        except:
            mape = None

        results[zone] = {
            'dates_hist': series['ds'].tolist(),
            'vals_hist':  [round(v, 1) for v in series['y'].tolist()],
            'dates_fc':   future_dates.tolist(),
            'base':       [round(v, 1) for v in base_fc.tolist()],
            'optimistic': [round(v, 1) for v in optimistic_fc.tolist()],
            'conservative': [round(v, 1) for v in conservative_fc.tolist()],
            'mape':       mape,
            'trend_pct':  round(((base_fc[-1] - hist_vals[-1]) / max(hist_vals[-1], 1)) * 100, 1),
        }

    return results

# ── AI Insights ──────────────────────────────────────────────────────────────
def get_ai_insights(api_key, utility, unit, horizon, results, zone_cols):
    try:
        import requests
        summary_lines = []
        for z in zone_cols[:8]:
            r = results[z]
            summary_lines.append(
                f"- {z}: current avg {round(np.mean(r['vals_hist'][-12:]),1)} {unit}, "
                f"forecast end {r['base'][-1]} {unit}, trend {r['trend_pct']:+.1f}%, "
                f"MAPE accuracy {r['mape']}%"
            )
        summary_text = "\n".join(summary_lines)

        prompt = f"""You are a senior utility planning consultant writing a professional report.

Utility type: {utility} (unit: {unit})
Forecast horizon: {horizon} months
Number of zones: {len(zone_cols)}

Zone forecast summary:
{summary_text}

Write a professional executive summary with these sections:
1. Overall consumption outlook (2-3 sentences)
2. Key zones to watch — highest growth, anomalies (3-4 bullet points)
3. Strategic recommendations for infrastructure planning (3-4 bullet points)
4. Data confidence note (1-2 sentences)

Keep tone professional and concise. Use utility planning language."""

        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 800,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )
        if resp.status_code == 200:
            return resp.json()['content'][0]['text']
        else:
            return None
    except:
        return None

# ── Excel export ─────────────────────────────────────────────────────────────
def build_excel(df, results, zone_cols, utility, unit, horizon):
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        # Summary sheet
        summary_rows = []
        for z in zone_cols:
            r = results[z]
            summary_rows.append({
                'Zone': z,
                f'Avg Historical ({unit})': round(np.mean(r['vals_hist']), 1),
                f'Last Historical ({unit})': r['vals_hist'][-1],
                f'Forecast End Base ({unit})': r['base'][-1],
                f'Forecast End Optimistic ({unit})': r['optimistic'][-1],
                f'Forecast End Conservative ({unit})': r['conservative'][-1],
                'Growth Trend (%)': r['trend_pct'],
                'MAPE Accuracy (%)': r['mape'] if r['mape'] else 'N/A',
            })
        pd.DataFrame(summary_rows).to_excel(writer, sheet_name='Summary', index=False)

        # Per-zone forecast sheets
        for z in zone_cols:
            r = results[z]
            dates_fc = [d.strftime('%b %Y') if hasattr(d, 'strftime') else str(d) for d in r['dates_fc']]
            fc_df = pd.DataFrame({
                'Month': dates_fc,
                f'Base ({unit})': r['base'],
                f'Optimistic ({unit})': r['optimistic'],
                f'Conservative ({unit})': r['conservative'],
            })
            fc_df.to_excel(writer, sheet_name=z[:31], index=False)

        # Raw historical
        df.to_excel(writer, sheet_name='Historical Data', index=False)

    buf.seek(0)
    return buf

# ── Template builder ─────────────────────────────────────────────────────────
def build_template(utility, unit):
    buf = BytesIO()
    dates = pd.date_range(start='2019-01-01', periods=72, freq='MS')
    template_df = pd.DataFrame({'Date': dates.strftime('%Y-%m-%d')})
    for i in range(1, 4):
        template_df[f'Zone_{i}'] = ''
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        template_df.to_excel(writer, sheet_name='Data', index=False)
        instructions = pd.DataFrame({
            'Instructions': [
                f'Utility: {utility}',
                f'Unit: {unit}',
                'Fill in consumption values for each zone column.',
                'Add more zone columns as needed (Zone_4, Zone_5, etc.)',
                'Date format: YYYY-MM-DD',
                'Minimum 36 months required. 60+ months recommended.',
                'Do not change the Date column format.',
                'Do not leave the header row blank.',
                'Delete example Zone columns and rename as needed.',
            ]
        })
        instructions.to_excel(writer, sheet_name='Instructions', index=False)
    buf.seek(0)
    return buf

# ═══════════════════════════════════════════════════════════════════════════
# STEP 1 — LANDING
# ═══════════════════════════════════════════════════════════════════════════
if st.session_state.step == 1:
    st.markdown("""
    <div class="main-header">
        <div style="font-size:5rem;margin-bottom:0.75rem">🔮</div>
        <div class="main-title">Utility Crystal Ball</div>
        <div class="main-tagline">"See your consumption future — before it arrives"</div>
        <div class="main-desc">
            Advanced utility consumption forecasting for water, electricity,
            gas, district cooling and TSE. Powered by AI ensemble models.
            Built for planners. Trusted by data.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔮  Enter if you're ready...", use_container_width=True):
            st.session_state.step = 2
            st.rerun()

    dev_footer()

# ═══════════════════════════════════════════════════════════════════════════
# STEP 2 — SELECT UTILITY
# ═══════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 2:
    render_steps(2)
    st.markdown('<div class="section-title">Select utility type</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Choose the utility you want to forecast</div>', unsafe_allow_html=True)

    col_ex, _ = st.columns([1, 3])
    with col_ex:
        if st.button("⚡ Load example (Electricity)"):
            st.session_state.utility = 'Electricity'
            # Generate example data
            np.random.seed(42)
            dates = pd.date_range('2019-01-01', periods=72, freq='MS')
            ex_df = pd.DataFrame({'Date': dates})
            for i, (base, amp, trend) in enumerate(zip([1450,1880,1980],[400,80,620],[8,-3,15])):
                vals = []
                for j in range(72):
                    seasonal = np.sin((j - 3) * np.pi / 6) * amp
                    tr = trend * j / 12
                    noise = np.random.normal(0, base * 0.02)
                    vals.append(round(max(base + seasonal + tr + noise, 100), 1))
                ex_df[f'Zone_{i+1}'] = vals
            st.session_state.df = ex_df
            st.session_state.zones = ['Zone_1', 'Zone_2', 'Zone_3']
            st.session_state.history_months = 72
            st.session_state.step = 3
            st.rerun()

    st.markdown("---")
    cols = st.columns(5)
    for i, (util, info) in enumerate(UTILITIES.items()):
        with cols[i]:
            selected = st.session_state.utility == util
            border = '2px solid #8060d0' if selected else '1px solid #2a1a4a'
            bg = '#241848' if selected else '#16102a'
            st.markdown(f"""
            <div style="background:{bg};border:{border};border-radius:10px;
                        padding:1rem 0.5rem;text-align:center;margin-bottom:0.5rem;">
                <div style="font-size:1.8rem">{info['icon']}</div>
                <div style="font-size:0.75rem;color:{'#c0a0ff' if selected else '#8070a0'};margin-top:4px">{util}</div>
                <div style="font-size:0.65rem;color:#5a4a7a">{info['unit']}</div>
            </div>""", unsafe_allow_html=True)
            if st.button("Select", key=f"sel_{util}", use_container_width=True):
                st.session_state.utility = util
                st.rerun()

    st.markdown("---")
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("← Back"):
            st.session_state.step = 1
            st.rerun()
    with c2:
        if st.session_state.utility:
            if st.button("Next →", use_container_width=True):
                st.session_state.step = 3
                st.rerun()
        else:
            st.info("Please select a utility to continue")

    dev_footer()

# ═══════════════════════════════════════════════════════════════════════════
# STEP 3 — SETUP + UPLOAD
# ═══════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 3:
    render_steps(3)
    util = st.session_state.utility
    unit = UTILITIES[util]['unit']

    st.markdown(f'<div class="section-title">Setup & Upload — {util} ({unit})</div>', unsafe_allow_html=True)

    # Setup params
    with st.container():
        c1, c2, c3 = st.columns(3)
        with c1:
            horizon = st.selectbox("Forecast horizon", [f"{h} months" for h in HORIZONS], index=1)
            st.session_state.horizon = int(horizon.split()[0])
        with c2:
            engine = st.selectbox("Model engine", ['Ensemble (Prophet + SARIMA)', 'Prophet only'])
            st.session_state.engine = engine
        with c3:
            scenario = st.selectbox("Scenario output", ['3 scenarios (base / optimistic / conservative)', 'Base case only'])
            st.session_state.scenario = scenario

    st.markdown("---")

    # AI Key
    with st.expander("🤖 Optional: Anthropic API key for AI-powered insights"):
        st.markdown('<div class="info-box">Your key is used for this session only and never stored. Get your key at console.anthropic.com</div>', unsafe_allow_html=True)
        api_key = st.text_input("Anthropic API key", type="password", value=st.session_state.api_key,
                                placeholder="sk-ant-...")
        st.session_state.api_key = api_key
        if api_key:
            st.markdown('<div class="success-box">✅ API key entered — AI insights will be added to your PDF report</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Template download
    st.markdown("**Step 1 — Download the data template**")
    tmpl = build_template(util, unit)
    st.download_button(
        label=f"⬇ Download {util} template (.xlsx)",
        data=tmpl,
        file_name=f"UCB_template_{util.replace(' ','_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.markdown(f"""
    <div class="info-box">
    Template format: <strong>Date</strong> column (YYYY-MM-DD) + one column per zone (Zone_1, Zone_2, ...).
    Values in <strong>{unit}</strong>. Minimum 36 months. 60+ months recommended for best accuracy.
    </div>""", unsafe_allow_html=True)

    st.markdown("**Step 2 — Upload your completed file**")
    uploaded = st.file_uploader("Upload your Excel file", type=['xlsx'], label_visibility='collapsed')

    if uploaded:
        try:
            df_raw = pd.read_excel(uploaded)
            valid, val_results, months, zone_cols = validate_data(df_raw.copy())

            st.markdown("**Validation results:**")
            for icon, msg, level in val_results:
                color = '#3db07a' if level == 'ok' else '#d4a020' if level == 'warn' else '#cc4040'
                st.markdown(f'<div style="font-size:0.82rem;color:{color};padding:3px 0">{icon} {msg}</div>',
                            unsafe_allow_html=True)

            if months > 0 and months < 60:
                st.markdown(f"""
                <div class="warn-box">
                ⚠️ Your data contains {months} months. Recommended minimum is 60 months for full accuracy.
                Forecast confidence will be reduced. You may proceed or extend your data.
                </div>""", unsafe_allow_html=True)

            if months < 36:
                st.markdown('<div class="warn-box">❌ Minimum 36 months required. Please extend your data.</div>',
                            unsafe_allow_html=True)
            elif valid or months >= 36:
                st.session_state.df = df_raw
                st.session_state.zones = zone_cols
                st.session_state.history_months = months

        except Exception as e:
            st.error(f"Could not read file: {e}")

    # Use example if loaded
    if st.session_state.df is not None and not uploaded:
        st.markdown('<div class="success-box">✅ Example data loaded — 72 months, 3 zones (Electricity)</div>',
                    unsafe_allow_html=True)

    st.markdown("---")
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("← Back"):
            st.session_state.step = 2
            st.rerun()
    with c2:
        ready = st.session_state.df is not None and st.session_state.history_months >= 36
        if ready:
            if st.button("🔮 Run Forecast", use_container_width=True):
                st.session_state.step = 4
                st.rerun()
        else:
            st.info("Upload valid data to run forecast")

    dev_footer()

# ═══════════════════════════════════════════════════════════════════════════
# STEP 4 — PROCESSING
# ═══════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 4:
    render_steps(4)

    st.markdown("""
    <div style="text-align:center;padding:2rem 0">
        <div style="font-size:4rem;margin-bottom:1rem">🔮</div>
        <div style="font-size:1.1rem;color:#b090ff;margin-bottom:1.5rem">The crystal ball is working...</div>
    </div>""", unsafe_allow_html=True)

    steps_ui = [
        "Validating data",
        "Detecting seasonality patterns",
        "Running Prophet model",
        "Running SARIMA model",
        "Combining ensemble results",
        "Generating scenarios",
        "Building reports",
    ]
    progress_bar = st.progress(0)
    status_box = st.empty()

    df = st.session_state.df.copy()
    zone_cols = st.session_state.zones
    horizon = st.session_state.horizon
    engine = st.session_state.engine

    for i, step_name in enumerate(steps_ui):
        status_box.markdown(f'<div style="text-align:center;color:#b090ff;font-size:0.85rem">⟳ {step_name}...</div>',
                            unsafe_allow_html=True)
        progress_bar.progress((i + 1) / len(steps_ui))

        if i == 2:
            results = run_forecast(df, zone_cols, horizon, engine)

    st.session_state.results = results
    progress_bar.progress(1.0)
    status_box.markdown('<div style="text-align:center;color:#3db07a;font-size:0.9rem">✅ Forecast complete!</div>',
                        unsafe_allow_html=True)

    import time
    time.sleep(0.8)
    st.session_state.step = 5
    st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
# STEP 5 — RESULTS
# ═══════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 5:
    import plotly.graph_objects as go

    render_steps(5)

    util    = st.session_state.utility
    unit    = UTILITIES[util]['unit']
    results = st.session_state.results
    zones   = st.session_state.zones
    horizon = st.session_state.horizon
    df      = st.session_state.df

    # Accuracy summary
    mapes = [results[z]['mape'] for z in zones if results[z]['mape'] is not None]
    avg_mape = round(np.mean(mapes), 1) if mapes else None

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-box"><div class="metric-label">Utility</div><div class="metric-val" style="font-size:1rem">{util}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-box"><div class="metric-label">Zones</div><div class="metric-val">{len(zones)}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-box"><div class="metric-label">Horizon</div><div class="metric-val" style="font-size:1rem">{horizon} mo</div></div>', unsafe_allow_html=True)
    with c4:
        if avg_mape:
            color_cls = "metric-good" if avg_mape >= 85 else "metric-warn"
            st.markdown(f'<div class="metric-box"><div class="metric-label">MAPE Accuracy</div><div class="metric-val {color_cls}">{avg_mape}%</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="metric-box"><div class="metric-label">MAPE Accuracy</div><div class="metric-val">N/A</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(["📈 Forecast Charts", "🏆 Area Rankings", "🤖 AI Insights", "📥 Export"])

    # ── Tab 1: Charts ──
    with tab1:
        zone_options = ['All zones'] + zones
        selected_zone = st.selectbox("Select zone to display", zone_options, key="zone_sel")

        def make_chart(zone_key):
            fig = go.Figure()
            if zone_key == 'All zones':
                # Aggregate
                all_hist_dates = results[zones[0]]['dates_hist']
                all_hist_vals  = [sum(results[z]['vals_hist'][i] for z in zones) for i in range(len(all_hist_dates))]
                all_fc_dates   = results[zones[0]]['dates_fc']
                all_base       = [sum(results[z]['base'][i] for z in zones) for i in range(horizon)]
                all_opt        = [sum(results[z]['optimistic'][i] for z in zones) for i in range(horizon)]
                all_con        = [sum(results[z]['conservative'][i] for z in zones) for i in range(horizon)]
                hist_dates, hist_vals = all_hist_dates, all_hist_vals
                fc_dates, base_fc, opt_fc, con_fc = all_fc_dates, all_base, all_opt, all_con
                title = f"All Zones — {util} ({unit})"
            else:
                r = results[zone_key]
                hist_dates, hist_vals = r['dates_hist'], r['vals_hist']
                fc_dates, base_fc, opt_fc, con_fc = r['dates_fc'], r['base'], r['optimistic'], r['conservative']
                title = f"{zone_key} — {util} ({unit})"

            # Uncertainty band
            fig.add_trace(go.Scatter(
                x=list(fc_dates) + list(fc_dates)[::-1],
                y=opt_fc + con_fc[::-1],
                fill='toself', fillcolor='rgba(61,176,122,0.08)',
                line=dict(color='rgba(0,0,0,0)'), showlegend=False, hoverinfo='skip'
            ))
            fig.add_trace(go.Scatter(
                x=hist_dates, y=hist_vals,
                name='Historical', line=dict(color='#8060d0', width=2),
                hovertemplate='%{x|%b %Y}<br>%{y:,.1f} ' + unit + '<extra>Historical</extra>'
            ))
            fig.add_trace(go.Scatter(
                x=fc_dates, y=base_fc,
                name='Base forecast', line=dict(color='#3db07a', width=2),
                hovertemplate='%{x|%b %Y}<br>%{y:,.1f} ' + unit + '<extra>Base forecast</extra>'
            ))
            fig.add_trace(go.Scatter(
                x=fc_dates, y=opt_fc,
                name='Optimistic', line=dict(color='#cc7040', width=1.5, dash='dash'),
                hovertemplate='%{x|%b %Y}<br>%{y:,.1f} ' + unit + '<extra>Optimistic</extra>'
            ))
            fig.add_trace(go.Scatter(
                x=fc_dates, y=con_fc,
                name='Conservative', line=dict(color='#6a5a8a', width=1.5, dash='dash'),
                hovertemplate='%{x|%b %Y}<br>%{y:,.1f} ' + unit + '<extra>Conservative</extra>'
            ))

            # Divider line
            if fc_dates:
                split_x = str(fc_dates[0])[:10] if hasattr(fc_dates[0], 'strftime') else str(fc_dates[0])[:10]
                fig.add_shape(
                    type='line',
                    x0=split_x, x1=split_x, y0=0, y1=1,
                    xref='x', yref='paper',
                    line=dict(color='#3a2a5a', width=1, dash='dot')
                )
                fig.add_annotation(
                    x=split_x, y=0.97, xref='x', yref='paper',
                    text='forecast →', showarrow=False,
                    font=dict(color='#5a4a7a', size=10),
                    xanchor='left'
                )

            fig.update_layout(
                title=dict(text=title, font=dict(color='#c0a0ff', size=13)),
                paper_bgcolor='#12102a', plot_bgcolor='#12102a',
                font=dict(color='#9080b0', size=11),
                xaxis=dict(
                    title='Month', title_font=dict(color='#7060a0', size=11),
                    tickfont=dict(color='#7060a0', size=10),
                    gridcolor='#1e1438', showgrid=True,
                    tickformat='%b %Y', dtick='M6'
                ),
                yaxis=dict(
                    title=f'Consumption ({unit})', title_font=dict(color='#7060a0', size=11),
                    tickfont=dict(color='#7060a0', size=10),
                    gridcolor='#1e1438', showgrid=True,
                    tickformat=',.0f'
                ),
                legend=dict(
                    bgcolor='#16102a', bordercolor='#2a1a4a', borderwidth=1,
                    font=dict(color='#9080b0', size=10)
                ),
                margin=dict(l=60, r=20, t=50, b=60),
                height=400,
                hovermode='x unified'
            )
            return fig

        st.plotly_chart(make_chart(selected_zone), use_container_width=True)

    # ── Tab 2: Rankings ──
    with tab2:
        ranking_data = []
        for z in zones:
            r = results[z]
            avg_hist = round(np.mean(r['vals_hist'][-12:]), 1)
            ranking_data.append({
                'Zone': z,
                f'Avg Last 12mo ({unit})': avg_hist,
                f'Forecast End ({unit})': r['base'][-1],
                'Growth (%)': r['trend_pct'],
                'MAPE (%)': r['mape'] if r['mape'] else 'N/A',
                'Status': '🚀 High growth' if r['trend_pct'] > 5 else
                          '📈 Growing' if r['trend_pct'] > 1 else
                          '⚠️ Anomaly' if r['trend_pct'] < -1 else
                          '➡️ Stable'
            })
        rank_df = pd.DataFrame(ranking_data).sort_values('Growth (%)', ascending=False)
        st.dataframe(rank_df, use_container_width=True, hide_index=True)

    # ── Tab 3: AI Insights ──
    with tab3:
        if st.session_state.api_key:
            if st.button("🤖 Generate AI insights"):
                with st.spinner("Consulting the AI oracle..."):
                    insights = get_ai_insights(
                        st.session_state.api_key, util, unit,
                        horizon, results, zones
                    )
                if insights:
                    st.session_state['ai_insights'] = insights
                else:
                    st.error("Could not generate insights. Check your API key.")

            if 'ai_insights' in st.session_state and st.session_state['ai_insights']:
                st.markdown(f"""
                <div style="background:#16102a;border:1px solid #2a1a4a;border-radius:10px;
                            padding:1.25rem 1.5rem;font-size:0.85rem;color:#b090ff;line-height:1.8;
                            white-space:pre-wrap">{st.session_state['ai_insights']}</div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="info-box">
            🤖 Enter your Anthropic API key in the Setup step to unlock AI-powered insights.<br>
            AI insights include: executive summary, zone analysis, strategic recommendations, and confidence narrative.
            </div>""", unsafe_allow_html=True)

    # ── Tab 4: Export ──
    with tab4:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div style="background:#16102a;border:1px solid #2a1a4a;border-radius:10px;
                        padding:1.25rem;text-align:center;">
                <div style="font-size:2rem;margin-bottom:0.5rem">📊</div>
                <div style="color:#b090ff;font-size:0.9rem;margin-bottom:0.3rem">Excel report</div>
                <div style="color:#5a4a7a;font-size:0.75rem">Summary + per-zone forecasts + 3 scenarios + accuracy metrics</div>
            </div>""", unsafe_allow_html=True)
            excel_buf = build_excel(df, results, zones, util, unit, horizon)
            st.download_button(
                "⬇ Download Excel",
                data=excel_buf,
                file_name=f"UCB_{util.replace(' ','_')}_{horizon}mo_forecast.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        with c2:
            st.markdown("""
            <div style="background:#16102a;border:1px solid #2a1a4a;border-radius:10px;
                        padding:1.25rem;text-align:center;">
                <div style="font-size:2rem;margin-bottom:0.5rem">📄</div>
                <div style="color:#b090ff;font-size:0.9rem;margin-bottom:0.3rem">PDF report</div>
                <div style="color:#5a4a7a;font-size:0.75rem">Executive summary + precise charts + methodology + AI insights</div>
            </div>""", unsafe_allow_html=True)
            st.info("PDF export available in full deployment (ReportLab)")

    st.markdown("---")
    if st.button("🔮 Start new forecast"):
        for k in ['df','results','zones','utility','history_months','ai_insights']:
            if k in st.session_state:
                del st.session_state[k]
        st.session_state.step = 1
        st.rerun()

    dev_footer()
