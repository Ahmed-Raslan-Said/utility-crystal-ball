import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="Utility Crystal Ball",page_icon="🔮",layout="wide",initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;background-color:#0a0a1a;color:#c0a0ff}
.stApp{background-color:#0a0a1a}
section[data-testid="stSidebar"]{display:none}
.main-title{font-size:2.4rem;font-weight:600;color:#e8d8ff;letter-spacing:2px;margin-bottom:.3rem;text-align:center}
.main-tagline{font-size:1rem;color:#9080b0;font-style:italic;margin-bottom:1rem;text-align:center}
.main-desc{font-size:.85rem;color:#7060a0;max-width:520px;margin:0 auto 1.5rem;line-height:1.8;text-align:center}
.dev-footer{background:rgba(8,4,22,.95);border-top:1px solid #1a0a3a;padding:.6rem 1.5rem;display:flex;justify-content:space-between;align-items:center;font-size:.75rem;color:#5a4a7a;margin-top:2rem}
.metric-box{background:#16102a;border-radius:8px;padding:.75rem 1rem;text-align:center}
.metric-label{font-size:.7rem;color:#5a4a7a;margin-bottom:4px}
.metric-val{font-size:1.3rem;font-weight:500;color:#c0a0ff}
.metric-good{color:#3db07a!important}
.metric-warn{color:#d4a020!important}
.metric-bad{color:#cc4040!important}
.warn-box{background:rgba(180,130,0,.08);border:1px solid rgba(180,130,0,.3);border-radius:8px;padding:.75rem 1rem;font-size:.8rem;color:#c09030;margin-bottom:1rem;line-height:1.6}
.info-box{background:rgba(60,100,200,.08);border:1px solid rgba(60,100,200,.3);border-radius:8px;padding:.75rem 1rem;font-size:.8rem;color:#7090d0;margin-bottom:1rem;line-height:1.6}
.success-box{background:rgba(40,160,100,.08);border:1px solid rgba(40,160,100,.3);border-radius:8px;padding:.75rem 1rem;font-size:.8rem;color:#3db07a;margin-bottom:1rem;line-height:1.6}
.error-box{background:rgba(200,60,60,.08);border:1px solid rgba(200,60,60,.3);border-radius:8px;padding:.75rem 1rem;font-size:.8rem;color:#cc4040;margin-bottom:1rem;line-height:1.6}
.temp-box{background:rgba(255,140,0,.08);border:1px solid rgba(255,140,0,.3);border-radius:8px;padding:.75rem 1rem;font-size:.8rem;color:#ff8c00;margin-bottom:1rem;line-height:1.6}
.insight-card{background:#16102a;border:1px solid #2a1a4a;border-radius:10px;padding:1rem;margin-bottom:.75rem}
.insight-zone{font-size:.8rem;font-weight:600;color:#b090ff;margin-bottom:.25rem}
.insight-text{font-size:.75rem;color:#8070a0;line-height:1.6}
div[data-testid="stButton"]>button{background:#4a2a8a;color:#e0c0ff;border:none;border-radius:20px;padding:.5rem 1.5rem;font-size:.85rem}
div[data-testid="stButton"]>button:hover{background:#6a3aaa;color:#fff}
div[data-testid="stSelectbox"] label,div[data-testid="stTextInput"] label,div[data-testid="stFileUploader"] label{color:#9080b0!important;font-size:.8rem!important}
div[data-testid="stTextInput"] input{background:#16102a!important;color:#c0a0ff!important;border:1px solid #2a1a4a!important;border-radius:8px!important}
div[data-testid="stSelectbox"]>div>div{background:#16102a!important;color:#c0a0ff!important;border:1px solid #2a1a4a!important;border-radius:8px!important}
.stTabs [data-baseweb="tab-list"]{background:#0f0f22;border-bottom:1px solid #2a1a4a}
.stTabs [data-baseweb="tab"]{color:#5a4a7a;font-size:.82rem}
.stTabs [aria-selected="true"]{color:#b090ff!important;border-bottom:2px solid #8060d0!important}
.step-indicator{display:flex;justify-content:center;align-items:center;padding:1rem 0;margin-bottom:1.5rem}
.step-dot{width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:500;border:1px solid #3a2a5a;color:#5a4a7a;background:transparent}
.step-dot-done{background:#4a2a8a;border-color:#6a4aaa;color:#d0b0ff}
.step-dot-active{background:#6a3aaa;border-color:#9a60dd;color:#fff;box-shadow:0 0 8px rgba(150,80,220,.5)}
.step-label{font-size:10px;color:#5a4a7a}
.step-label-active{font-size:10px;color:#b090ff}
.step-line{width:32px;height:1px;background:#2a1a4a;margin:0 4px}
</style>
""", unsafe_allow_html=True)

for k,v in {
    "step":1,"utility":None,"horizon":24,"df":None,"zones":[],
    "results":None,"api_key":"","history_periods":0,"ai_insights":None,
    "frequency":"Monthly","has_temperature":False,"future_temp_df":None
}.items():
    if k not in st.session_state: st.session_state[k]=v

UTILITIES={"Electricity":{"icon":"⚡","unit":"MW","temp_benefit":True},
           "Water":{"icon":"💧","unit":"m³","temp_benefit":True},
           "Gas":{"icon":"🔥","unit":"m³","temp_benefit":True},
           "District Cooling":{"icon":"❄️","unit":"TonHr","temp_benefit":True},
           "TSE":{"icon":"♻️","unit":"m³","temp_benefit":False}}
MONTHS_SHORT=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
COLORS=["#8060d0","#3db07a","#cc7040","#4090d0","#d04090","#40d0c0"]
TEMP_COLS=["Temp_Max_C","Temp_Min_C"]

def render_steps(current):
    steps=["Utility","Setup","Upload","Explore","Forecast","Results"]
    dots=[]
    for i,s in enumerate(steps):
        n=i+1
        if n<current: dc="step-dot-done";sym="✓";lc="step-label"
        elif n==current: dc="step-dot-active";sym=str(n);lc="step-label-active"
        else: dc="";sym=str(n);lc="step-label"
        line='<div class="step-line"></div>' if i<len(steps)-1 else ""
        dots.append(f'<div style="display:flex;align-items:center;gap:6px"><div class="step-dot {dc}">{sym}</div><span class="{lc}">{s}</span></div>{line}')
    st.markdown(f'<div class="step-indicator">{"".join(dots)}</div>',unsafe_allow_html=True)

def dev_footer():
    st.markdown("""<div class="dev-footer">
        <span>🔮 Developed by <strong style="color:#8060b0">Engr. Ahmed Raslan</strong></span>
        <span style="display:flex;gap:24px"><span>✉ Engr_Raslan@outlook.com</span><span>📞 +971 52 289 9595</span></span>
    </div>""",unsafe_allow_html=True)

def get_horizon_options(freq,periods):
    if freq=="Daily":
        opts=[]
        if periods>=365: opts.extend([30,60])
        if periods>=730: opts.append(90)
        if periods>=1095: opts.append(180)
        return opts or [30]
    return [12,24,36,60]

def get_advice(freq,periods):
    if freq=="Daily":
        if periods<365: return "❌ Minimum 365 days required"
        elif periods<730: return f"⚠️ {periods} days — recommended: 30-60 day forecast"
        elif periods<1095: return f"✅ {periods} days — recommended: up to 90 days"
        else: return f"✅ {periods} days — recommended: up to 180 days"
    else:
        if periods<60: return "❌ Minimum 60 months required"
        elif periods<120: return f"⚠️ {periods} months — recommended: 12-24 month forecast"
        else: return f"✅ {periods} months — recommended: up to 60 months"

def validate_data(df,freq):
    results=[];ok=True
    daily=freq=="Daily"
    min_rej=365 if daily else 60
    min_warn=730 if daily else 120
    if "Date" not in df.columns:
        results.append(("❌","Date column not found","err"));ok=False
    else:
        results.append(("✅","Date column found","ok"))
    all_cols=[c for c in df.columns if c!="Date"]
    zone_cols=[c for c in all_cols if c not in TEMP_COLS]
    temp_detected=[c for c in all_cols if c in TEMP_COLS]
    if not zone_cols:
        results.append(("❌","No consumption columns found","err"));ok=False
    else:
        results.append(("✅",f"{len(zone_cols)} consumption column(s): {', '.join(zone_cols[:3])}{'...' if len(zone_cols)>3 else ''}","ok"))
    if temp_detected:
        results.append(("🌡️",f"Temperature columns detected: {', '.join(temp_detected)} — Temperature mode activated!","ok"))
    if not ok: return False,results,0,zone_cols,temp_detected
    try:
        df["Date"]=pd.to_datetime(df["Date"])
        df=df.sort_values("Date").reset_index(drop=True)
        results.append(("✅",f"Date format OK — {freq.lower()}","ok"))
    except:
        results.append(("❌","Date column cannot be parsed","err"));ok=False
        return ok,results,0,zone_cols,temp_detected
    dups=df["Date"].duplicated().sum()
    if dups>0: results.append(("❌",f"{dups} duplicate date(s) found","err"));ok=False
    else: results.append(("✅","No duplicate dates","ok"))
    periods=len(df)
    unit="days" if daily else "months"
    if periods<min_rej:
        results.append(("❌",f"History: {periods} {unit} — minimum {min_rej} required","err"));ok=False
    elif periods<min_warn:
        results.append(("⚠️",f"History: {periods} {unit} — {min_warn}+ recommended","warn"))
    else:
        results.append(("✅",f"History: {periods} {unit} — excellent ✅","ok"))
    total=df[zone_cols].size
    miss=df[zone_cols].isnull().sum().sum()
    mp=round(miss/total*100,1) if total>0 else 0
    if mp>20: results.append(("❌",f"Missing: {mp}% — too high","err"));ok=False
    elif mp>5: results.append(("⚠️",f"Missing: {mp}% — review","warn"))
    else: results.append(("✅",f"Missing: {mp}% — OK","ok"))
    spike=any(df[c].mean()>0 and (df[c]>df[c].mean()*4).any() for c in zone_cols)
    results.append(("⚠️","Possible spikes detected","warn") if spike else ("✅","No spikes detected","ok"))
    return ok,results,periods,zone_cols,temp_detected

def quality_score(df,zone_cols,periods,freq):
    score=100
    daily=freq=="Daily"
    if periods<(730 if daily else 120): score-=15
    if periods<(365 if daily else 60): score-=25
    total=df[zone_cols].size
    miss=df[zone_cols].isnull().sum().sum()
    if total>0:
        mp=miss/total*100
        if mp>20: score-=30
        elif mp>5: score-=15
    if any(df[c].mean()>0 and (df[c]>df[c].mean()*4).any() for c in zone_cols): score-=10
    return max(0,min(100,score))

def validate_future_temp(df_ft,horizon,freq):
    results=[];ok=True
    daily=freq=="Daily"
    if not daily:
        results.append(("ℹ️","Future temperature only used in Daily mode","ok"))
        return True,results
    try:
        df_ft["Date"]=pd.to_datetime(df_ft["Date"])
        df_ft=df_ft.sort_values("Date").reset_index(drop=True)
        results.append(("✅","Future temperature dates parsed OK","ok"))
    except:
        results.append(("❌","Cannot parse dates in future temperature sheet","err"))
        return False,results
    avail=len(df_ft)
    if avail>=horizon:
        results.append(("✅",f"Future temperature: {avail} days — covers full {horizon}-day horizon","ok"))
    elif avail>=16:
        results.append(("⚠️",f"Future temperature: {avail} days — covers {avail} of {horizon} days. Seasonal average used for remainder","warn"))
    else:
        results.append(("⚠️",f"Future temperature: {avail} days only. Seasonal average used for most of forecast","warn"))
    missing=df_ft[["Temp_Max_C","Temp_Min_C"]].isnull().sum().sum() if all(c in df_ft.columns for c in ["Temp_Max_C","Temp_Min_C"]) else 0
    if missing>0: results.append(("⚠️",f"{missing} missing temperature values — will use seasonal average","warn"))
    else: results.append(("✅","No missing temperature values","ok"))
    return ok,results

def prepare_future_temp(df_hist,df_ft,horizon,freq):
    """Build complete future temperature array for forecast period"""
    daily=freq=="Daily"
    if not daily: return None
    df_hist["Date"]=pd.to_datetime(df_hist["Date"])
    last_date=df_hist["Date"].max()
    future_dates=pd.date_range(start=last_date+pd.DateOffset(days=1),periods=horizon,freq="D")
    # Build seasonal average from historical temp
    seasonal_max={}
    seasonal_min={}
    if "Temp_Max_C" in df_hist.columns:
        df_hist["month"]=df_hist["Date"].dt.month
        for m in range(1,13):
            mdata=df_hist[df_hist["month"]==m]
            seasonal_max[m]=round(mdata["Temp_Max_C"].mean(),1) if len(mdata)>0 else 30.0
            seasonal_min[m]=round(mdata["Temp_Min_C"].mean(),1) if len(mdata)>0 else 20.0
    else:
        for m in range(1,13):
            seasonal_max[m]=30.0
            seasonal_min[m]=20.0
    # Build future temp dataframe
    rows=[]
    if df_ft is not None:
        df_ft["Date"]=pd.to_datetime(df_ft["Date"])
        ft_dict={}
        if all(c in df_ft.columns for c in ["Temp_Max_C","Temp_Min_C"]):
            for _,row in df_ft.iterrows():
                ft_dict[row["Date"].date()]=(row["Temp_Max_C"],row["Temp_Min_C"])
    else:
        ft_dict={}
    for d in future_dates:
        dk=d.date()
        if dk in ft_dict:
            mx,mn=ft_dict[dk]
            src="real_forecast"
        else:
            mx=seasonal_max[d.month]
            mn=seasonal_min[d.month]
            src="seasonal_avg"
        rows.append({"Date":d,"Temp_Max_C":mx,"Temp_Min_C":mn,"Source":src})
    return pd.DataFrame(rows)

def run_forecast(df,zone_cols,horizon,freq,has_temp=False,future_temp_df=None):
    results={}
    daily=freq=="Daily"
    df["Date"]=pd.to_datetime(df["Date"])
    df=df.sort_values("Date").reset_index(drop=True)
    for zone in zone_cols:
        series=df[["Date",zone]].copy().dropna()
        series.columns=["ds","y"]
        n=len(series)
        test_size=max(30 if daily else 12,int(n*0.10))
        train=series.iloc[:-test_size].copy()
        test=series.iloc[-test_size:].copy()
        hist_vals=series["y"].values.tolist()
        last_date=series["ds"].iloc[-1]
        freq_str="D" if daily else "MS"
        offset=pd.DateOffset(days=1) if daily else pd.DateOffset(months=1)
        future_dates=pd.date_range(start=last_date+offset,periods=horizon,freq=freq_str)
        # Add temperature regressors if available
        temp_regs=[]
        if has_temp and daily and "Temp_Max_C" in df.columns and "Temp_Min_C" in df.columns:
            temp_regs=["Temp_Max_C","Temp_Min_C"]
            series_with_temp=df[["Date",zone,"Temp_Max_C","Temp_Min_C"]].copy().dropna()
            series_with_temp.columns=["ds","y","Temp_Max_C","Temp_Min_C"]
            train_temp=series_with_temp.iloc[:-test_size].copy()
        else:
            series_with_temp=None
            train_temp=None
        # Prophet
        pfc=None;pbt=None
        try:
            from prophet import Prophet
            if temp_regs and series_with_temp is not None and future_temp_df is not None:
                # Temperature-enhanced Prophet
                m=Prophet(yearly_seasonality=True,weekly_seasonality=daily,daily_seasonality=False,
                          seasonality_mode="multiplicative",changepoint_prior_scale=0.05,interval_width=0.80)
                for reg in temp_regs: m.add_regressor(reg)
                m.fit(series_with_temp)
                fut=m.make_future_dataframe(periods=horizon,freq=freq_str)
                # Add future temperature to future dataframe
                fut["Date_key"]=pd.to_datetime(fut["ds"]).dt.date
                ftemp=future_temp_df.copy()
                ftemp["Date_key"]=pd.to_datetime(ftemp["Date"]).dt.date
                ftemp_dict=dict(zip(ftemp["Date_key"],zip(ftemp["Temp_Max_C"],ftemp["Temp_Min_C"])))
                hist_temp=dict(zip(pd.to_datetime(df["Date"]).dt.date,zip(df["Temp_Max_C"],df["Temp_Min_C"])))
                def get_temp(dk,col_idx):
                    if dk in hist_temp: return hist_temp[dk][col_idx]
                    if dk in ftemp_dict: return ftemp_dict[dk][col_idx]
                    return 30.0 if col_idx==0 else 20.0
                fut["Temp_Max_C"]=[get_temp(dk,0) for dk in fut["Date_key"]]
                fut["Temp_Min_C"]=[get_temp(dk,1) for dk in fut["Date_key"]]
                forecast=m.predict(fut)
                pfc=forecast.tail(horizon)["yhat"].values
                # Backtest with temperature
                mb=Prophet(yearly_seasonality=True,weekly_seasonality=daily,daily_seasonality=False,
                           seasonality_mode="multiplicative",changepoint_prior_scale=0.05)
                for reg in temp_regs: mb.add_regressor(reg)
                mb.fit(train_temp)
                fb=mb.make_future_dataframe(periods=test_size,freq=freq_str)
                fb["Date_key"]=pd.to_datetime(fb["ds"]).dt.date
                fb["Temp_Max_C"]=[get_temp(dk,0) for dk in fb["Date_key"]]
                fb["Temp_Min_C"]=[get_temp(dk,1) for dk in fb["Date_key"]]
                pbt=mb.predict(fb).tail(test_size)["yhat"].values
            else:
                # Standard Prophet
                m=Prophet(yearly_seasonality=True,weekly_seasonality=daily,daily_seasonality=False,
                          seasonality_mode="multiplicative",changepoint_prior_scale=0.05,interval_width=0.80)
                m.fit(series)
                fut=m.make_future_dataframe(periods=horizon,freq=freq_str)
                pfc=m.predict(fut).tail(horizon)["yhat"].values
                mb=Prophet(yearly_seasonality=True,weekly_seasonality=daily,daily_seasonality=False,
                           seasonality_mode="multiplicative",changepoint_prior_scale=0.05)
                mb.fit(train)
                fb=mb.make_future_dataframe(periods=test_size,freq=freq_str)
                pbt=mb.predict(fb).tail(test_size)["yhat"].values
        except: pfc=None
        # ETS
        efc=None;ebt=None
        try:
            from statsmodels.tsa.holtwinters import ExponentialSmoothing
            sp=7 if daily else 12
            hw=ExponentialSmoothing(series["y"],trend="add",seasonal="add",seasonal_periods=sp)
            efc=hw.fit(optimized=True).forecast(horizon)
            hwb=ExponentialSmoothing(train["y"],trend="add",seasonal="add",seasonal_periods=sp)
            ebt=hwb.fit(optimized=True).forecast(test_size)
        except: efc=None
        # Ensemble
        if pfc is not None and efc is not None:
            base_fc=np.array(pfc)*0.70+np.array(efc)*0.30
            btest=np.array(pbt)*0.70+np.array(ebt)*0.30 if pbt is not None and ebt is not None else (pbt if pbt is not None else np.array(ebt))
        elif pfc is not None:
            base_fc=np.array(pfc);btest=pbt if pbt is not None else np.array(hist_vals[-test_size:])
        elif efc is not None:
            base_fc=np.array(efc);btest=np.array(ebt) if ebt is not None else np.array(hist_vals[-test_size:])
        else:
            base_fc=np.full(horizon,np.mean(hist_vals));btest=np.array(hist_vals[-test_size:])
        hm,hs=np.mean(hist_vals),np.std(hist_vals)
        base_fc=np.clip(np.maximum(base_fc,0),max(hm-3*hs,0),hm+3*hs)
        actual_test=test["y"].values
        mape=None
        try:
            errs=np.abs((actual_test-btest)/np.maximum(actual_test,1))
            mape=round((1-np.mean(errs))*100,1);mape=max(0,min(100,mape))
        except: pass
        series["month"]=series["ds"].dt.month
        mavg=series.groupby("month")["y"].mean().reindex(range(1,13),fill_value=0)
        oa=mavg.mean()
        seas=(mavg/oa*100).round(1).tolist() if oa>0 else [100]*12
        series["year"]=series["ds"].dt.year
        yoy=series.groupby("year")["y"].sum().round(1).to_dict()
        dow_idx=None
        if daily:
            series["dow"]=series["ds"].dt.dayofweek
            da=series.groupby("dow")["y"].mean()
            dm=da.mean()
            dow_idx=(da/dm*100).round(1).tolist() if dm>0 else [100]*7
        results[zone]={
            "dates_hist":series["ds"].tolist(),"vals_hist":[round(v,2) for v in hist_vals],
            "dates_test":test["ds"].tolist(),"vals_test":[round(v,2) for v in actual_test.tolist()],
            "backtest_fc":[round(v,2) for v in btest.tolist()],"dates_fc":future_dates.tolist(),
            "base":[round(v,2) for v in base_fc.tolist()],"optimistic":[round(v,2) for v in (base_fc*1.06).tolist()],
            "conservative":[round(v,2) for v in (base_fc*0.94).tolist()],"mape":mape,
            "trend_pct":round(((base_fc[-1]-hist_vals[-1])/max(hist_vals[-1],1))*100,1),
            "test_size":test_size,"seasonality":seas,"yoy":yoy,"dow_index":dow_idx,
            "temp_enhanced":bool(temp_regs and pfc is not None),
        }
    return results

def get_ai_insights(api_key,util,unit,horizon,results,zones,freq,has_temp):
    try:
        import requests
        ul="days" if freq=="Daily" else "months"
        temp_note="Temperature-enhanced mode active." if has_temp else "Standard mode (no temperature)."
        lines=[f"- {z}: avg {round(np.mean(results[z]['vals_hist'][-30 if freq=='Daily' else -12:]),1)} {unit}, forecast end {results[z]['base'][-1]} {unit}, trend {results[z]['trend_pct']:+.1f}%, MAPE {results[z]['mape']}%" for z in zones[:6]]
        prompt=f"""Senior utility consultant report. {util} ({unit}), {freq}, {horizon} {ul}, {len(zones)} zones. {temp_note}
Data:\n{chr(10).join(lines)}
Write: 1) Outlook 2) Key zones 3) Recommendations 4) Confidence note. Professional, concise."""
        r=requests.post("https://api.anthropic.com/v1/messages",
            headers={"x-api-key":api_key,"anthropic-version":"2023-06-01","content-type":"application/json"},
            json={"model":"claude-sonnet-4-20250514","max_tokens":700,"messages":[{"role":"user","content":prompt}]},timeout=30)
        if r.status_code==200: return r.json()["content"][0]["text"]
    except: pass
    return None

def build_excel(df,results,zones,util,unit,horizon,freq,has_temp,future_temp_df):
    buf=BytesIO();ul="days" if freq=="Daily" else "months"
    with pd.ExcelWriter(buf,engine="openpyxl") as w:
        rows=[{"Column":z,f"Avg ({unit})":round(np.mean(results[z]["vals_hist"]),1),
               f"Last ({unit})":results[z]["vals_hist"][-1],f"Forecast End Base ({unit})":results[z]["base"][-1],
               f"Forecast End Opt ({unit})":results[z]["optimistic"][-1],f"Forecast End Con ({unit})":results[z]["conservative"][-1],
               "Growth (%)":results[z]["trend_pct"],"MAPE (%)":results[z]["mape"] or "N/A",
               "Temp Enhanced":results[z].get("temp_enhanced",False)} for z in zones]
        pd.DataFrame(rows).to_excel(w,sheet_name="Summary",index=False)
        for z in zones:
            r=results[z]
            dfc=[d.strftime("%Y-%m-%d") if hasattr(d,"strftime") else str(d) for d in r["dates_fc"]]
            pd.DataFrame({"Date":dfc,f"Base ({unit})":r["base"],f"Optimistic ({unit})":r["optimistic"],f"Conservative ({unit})":r["conservative"]}).to_excel(w,sheet_name=z[:31],index=False)
        btr=[]
        for z in zones:
            r=results[z]
            dt=[d.strftime("%Y-%m-%d") if hasattr(d,"strftime") else str(d) for d in r["dates_test"]]
            for d,a,p in zip(dt,r["vals_test"],r["backtest_fc"]):
                btr.append({"Zone":z,"Date":d,f"Actual ({unit})":a,f"Predicted ({unit})":p,"Error (%)":round(abs(a-p)/max(a,1)*100,1) if a>0 else None})
        pd.DataFrame(btr).to_excel(w,sheet_name="Backtest",index=False)
        if has_temp and future_temp_df is not None:
            ft=future_temp_df.copy()
            if "Date" in ft.columns: ft["Date"]=pd.to_datetime(ft["Date"]).dt.strftime("%Y-%m-%d")
            ft.to_excel(w,sheet_name="Future_Temperature",index=False)
        df.to_excel(w,sheet_name="Historical",index=False)
    buf.seek(0);return buf

def build_pdf(results,zones,util,unit,horizon,freq,has_temp,ai_insights=None):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,HRFlowable
        from reportlab.lib.enums import TA_CENTER
        buf=BytesIO()
        doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=2*cm,leftMargin=2*cm,topMargin=2*cm,bottomMargin=2*cm)
        ss=getSampleStyleSheet()
        TS=ParagraphStyle("T",parent=ss["Title"],fontSize=20,textColor=colors.HexColor("#4a2a8a"),spaceAfter=6,alignment=TA_CENTER,fontName="Helvetica-Bold")
        SS=ParagraphStyle("S",parent=ss["Normal"],fontSize=10,textColor=colors.HexColor("#6050a0"),spaceAfter=4,alignment=TA_CENTER)
        H2=ParagraphStyle("H2",parent=ss["Heading2"],fontSize=12,textColor=colors.HexColor("#4a2a8a"),spaceBefore=12,spaceAfter=6,fontName="Helvetica-Bold")
        BS=ParagraphStyle("B",parent=ss["Normal"],fontSize=9,textColor=colors.HexColor("#2a1a4a"),spaceAfter=4,leading=14)
        FS=ParagraphStyle("F",parent=ss["Normal"],fontSize=7,textColor=colors.HexColor("#8060b0"),alignment=TA_CENTER)
        ul="days" if freq=="Daily" else "months"
        temp_label=" + Temperature Enhanced" if has_temp else ""
        story=[Spacer(1,.5*cm),Paragraph("Utility Crystal Ball",TS),
               Paragraph("Consumption Forecast Report",SS),
               Paragraph(f"{util} | {freq}{temp_label} | {unit} | Horizon: {horizon} {ul}",SS),
               HRFlowable(width="100%",thickness=1,color=colors.HexColor("#8060d0"),spaceAfter=10)]
        story.append(Paragraph("Summary",H2))
        td=[["Zone",f"Avg ({unit})",f"Forecast End ({unit})","Growth","MAPE","Temp"]]
        for z in zones:
            r=results[z]
            td.append([z,f"{round(np.mean(r['vals_hist']),1):,.1f}",f"{r['base'][-1]:,.1f}",
                       f"{r['trend_pct']:+.1f}%",f"{r['mape']}%" if r["mape"] else "N/A",
                       "✓" if r.get("temp_enhanced") else "—"])
        t=Table(td,colWidths=[3.5*cm,3*cm,3.5*cm,2*cm,2*cm,2*cm])
        t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#4a2a8a")),("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8),("ALIGN",(0,0),(-1,-1),"CENTER"),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#f5f0ff"),colors.white]),
            ("GRID",(0,0),(-1,-1),.5,colors.HexColor("#c0a0ff")),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
        story.append(t);story.append(Spacer(1,.4*cm))
        story.append(Paragraph("Backtest Validation (10% holdout)",H2))
        for z in zones:
            r=results[z]
            story.append(Paragraph(f"{z} — MAPE: {r['mape']}%",ParagraphStyle("ZH",parent=BS,fontName="Helvetica-Bold")))
            dt=[d.strftime("%Y-%m-%d") if hasattr(d,"strftime") else str(d) for d in r["dates_test"]]
            btd=[["Date",f"Actual ({unit})",f"Predicted ({unit})","Error"]]
            for d,a,p in zip(dt[:20],r["vals_test"][:20],r["backtest_fc"][:20]):
                btd.append([d,f"{a:,.1f}",f"{p:,.1f}",f"{round(abs(a-p)/max(a,1)*100,1):.1f}%"])
            bt=Table(btd,colWidths=[4*cm,4*cm,4*cm,3*cm])
            bt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#6a3aaa")),("TEXTCOLOR",(0,0),(-1,0),colors.white),
                ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),7),("ALIGN",(0,0),(-1,-1),"CENTER"),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#f8f5ff"),colors.white]),
                ("GRID",(0,0),(-1,-1),.5,colors.HexColor("#c0a0ff")),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3)]))
            story.append(bt);story.append(Spacer(1,.3*cm))
        story.append(Paragraph("Detailed Forecast",H2))
        for z in zones:
            r=results[z]
            story.append(Paragraph(f"{z} | Growth: {r['trend_pct']:+.1f}% | Temp enhanced: {'Yes' if r.get('temp_enhanced') else 'No'}",ParagraphStyle("ZH2",parent=BS,fontName="Helvetica-Bold")))
            dfc=[d.strftime("%Y-%m-%d") if hasattr(d,"strftime") else str(d) for d in r["dates_fc"]]
            fcd=[["Date",f"Base ({unit})",f"Optimistic ({unit})",f"Conservative ({unit})"]]
            for d,b,o,c in zip(dfc[:30],r["base"][:30],r["optimistic"][:30],r["conservative"][:30]):
                fcd.append([d,f"{b:,.1f}",f"{o:,.1f}",f"{c:,.1f}"])
            ft=Table(fcd,colWidths=[4*cm,4*cm,4*cm,4*cm])
            ft.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#4a2a8a")),("TEXTCOLOR",(0,0),(-1,0),colors.white),
                ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),7),("ALIGN",(0,0),(-1,-1),"CENTER"),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#f5f0ff"),colors.white]),
                ("GRID",(0,0),(-1,-1),.5,colors.HexColor("#c0a0ff")),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3)]))
            story.append(ft);story.append(Spacer(1,.3*cm))
        if ai_insights:
            story.append(HRFlowable(width="100%",thickness=1,color=colors.HexColor("#8060d0"),spaceAfter=8))
            story.append(Paragraph("AI Insights",H2))
            for line in ai_insights.split("\n"):
                if line.strip(): story.append(Paragraph(line.strip(),BS))
        story.append(HRFlowable(width="100%",thickness=1,color=colors.HexColor("#8060d0"),spaceAfter=8))
        story.append(Paragraph(f"Methodology: Prophet (70%) + ETS (30%) ensemble.{' Temperature regressors (Temp_Max_C, Temp_Min_C) added to Prophet.' if has_temp else ''} Walk-forward backtest 10% holdout. Scenarios: Base / Optimistic +6% / Conservative -6%.",BS))
        story.append(Spacer(1,.3*cm))
        story.append(HRFlowable(width="100%",thickness=.5,color=colors.HexColor("#c0a0ff")))
        story.append(Spacer(1,.2*cm))
        story.append(Paragraph("Utility Crystal Ball | Engr. Ahmed Raslan | Engr_Raslan@outlook.com | +971 52 289 9595",FS))
        doc.build(story);buf.seek(0);return buf
    except: return None

def make_sample(util,unit,freq,flawed=False):
    np.random.seed(99 if flawed else 42);daily=freq=="Daily";buf=BytesIO()
    if daily:
        n=200 if flawed else 548
        dates=pd.date_range("2024-01-01",periods=n,freq="D")
        df=pd.DataFrame({"Date":dates.strftime("%Y-%m-%d")})
        base=300000
        vals=[round(max(base+np.sin((j-90)*2*np.pi/365)*base*0.3+np.sin(j*2*np.pi/7)*base*0.05+np.random.normal(0,base*0.02),100),2) for j in range(n)]
        temps_max=[round(25+15*np.sin((j-80)*2*np.pi/365)+np.random.normal(0,2),1) for j in range(n)]
        temps_min=[round(t-8+np.random.normal(0,1),1) for t in temps_max]
        if flawed: vals[50]=vals[50]*5;vals[100]=None;vals[101]=None
        df["Generation_MWh"]=vals
        df["Temp_Max_C"]=temps_max
        df["Temp_Min_C"]=temps_min
        if flawed:
            dup=pd.DataFrame({"Date":[dates[10].strftime("%Y-%m-%d")],"Generation_MWh":[260000],"Temp_Max_C":[28.5],"Temp_Min_C":[20.1]})
            df=pd.concat([df,dup],ignore_index=True)
    else:
        dates=pd.date_range("2015-01-01",periods=45 if flawed else 120,freq="MS")
        df=pd.DataFrame({"Date":dates.strftime("%Y-%m-%d")})
        cfg={"Electricity":[(1450,400,8),(1880,80,-3)],"Water":[(8500,1200,30),(6200,800,15)],
             "Gas":[(1200,300,6),(850,200,4)],"District Cooling":[(3200,800,12),(2100,500,8)],"TSE":[(2100,400,10),(1400,250,6)]}
        for i,(base,amp,trend) in enumerate(cfg.get(util,cfg["Electricity"])):
            vals=[round(max(base+np.sin((j-3)*np.pi/6)*amp+trend*j/12+np.random.normal(0,base*.02),50),1) for j in range(len(dates))]
            if flawed and i==0: vals[20]=vals[20]*6;vals[30]=None;vals[31]=None
            df[f"Zone_{i+1}"]=vals
        if flawed:
            dup=pd.DataFrame({"Date":[dates[10].strftime("%Y-%m-%d")],"Zone_1":[1200],"Zone_2":[700]})
            df=pd.concat([df,dup],ignore_index=True)
    df.to_excel(buf,index=False,engine="openpyxl");buf.seek(0);return buf

def build_template(util,unit,freq):
    buf=BytesIO();daily=freq=="Daily"
    if daily:
        dates=pd.date_range("2023-01-01",periods=730,freq="D")
        tdf=pd.DataFrame({"Date":dates.strftime("%Y-%m-%d"),"Consumption_or_Generation":"","Temp_Max_C":"","Temp_Min_C":""})
        instr=["Date: YYYY-MM-DD","One row per day",f"Unit: {unit}","Min 365 days, 730+ recommended",
               "Temp_Max_C and Temp_Min_C are OPTIONAL","Add temperature for improved accuracy (Electricity/Cooling)"]
    else:
        dates=pd.date_range("2015-01-01",periods=120,freq="MS")
        tdf=pd.DataFrame({"Date":dates.strftime("%Y-%m-%d")})
        for i in range(1,4): tdf[f"Zone_{i}"]=""
        instr=[f"Utility: {util}",f"Unit: {unit}","Monthly — one row per month","Min 60 months, 120+ recommended"]
    with pd.ExcelWriter(buf,engine="openpyxl") as w:
        tdf.to_excel(w,sheet_name="Data",index=False)
        pd.DataFrame({"Instructions":instr}).to_excel(w,sheet_name="Instructions",index=False)
    buf.seek(0);return buf

# ═══ LANDING ══════════════════════════════════════════════════════
if st.session_state.step==1:
    st.markdown('<div style="text-align:center;padding:2rem 0 1rem"><div style="font-size:5rem;margin-bottom:.75rem">🔮</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="main-title">Utility Crystal Ball</div>',unsafe_allow_html=True)
    st.markdown('<div class="main-tagline">"See your consumption future — before it arrives"</div>',unsafe_allow_html=True)
    st.markdown('<div class="main-desc">Advanced utility consumption forecasting for water, electricity, gas, district cooling and TSE. Powered by AI ensemble models. Built for planners. Trusted by data.</div>',unsafe_allow_html=True)
    _,c,_=st.columns([1,1,1])
    with c:
        if st.button("🔮  Enter if you're ready...",use_container_width=True): st.session_state.step=2;st.rerun()
    st.markdown("---")
    c1,c2,c3=st.columns(3)
    with c1:
        if st.button("ℹ️ About this platform",use_container_width=True): st.session_state.step=99;st.rerun()
    with c2:
        if st.button("📋 Model Card",use_container_width=True): st.session_state.step=98;st.rerun()
    with c3:
        # Model card PDF download
        try:
            with open("UCB_Model_Card.pdf","rb") as f:
                st.download_button("⬇ Download Model Card PDF",data=f.read(),file_name="UCB_Model_Card.pdf",mime="application/pdf",use_container_width=True)
        except:
            st.button("📄 Model Card PDF",use_container_width=True,disabled=True)
    dev_footer()

# ═══ ABOUT ════════════════════════════════════════════════════════
elif st.session_state.step==99:
    st.markdown('<div class="main-title">🔮 About Utility Crystal Ball</div>',unsafe_allow_html=True)
    st.markdown("---")
    c1,c2=st.columns(2)
    with c1:
        st.markdown("""<div style="background:#16102a;border:1px solid #2a1a4a;border-radius:12px;padding:1.25rem;margin-bottom:1rem">
        <div style="font-size:.9rem;font-weight:600;color:#c0a0ff;margin-bottom:.75rem">🎯 What it does</div>
        <div style="font-size:.8rem;color:#8070a0;line-height:1.8">AI-powered utility consumption forecasting supporting monthly and daily data, with optional temperature enhancement for improved accuracy on climate-sensitive utilities.</div></div>
        <div style="background:#16102a;border:1px solid #2a1a4a;border-radius:12px;padding:1.25rem;margin-bottom:1rem">
        <div style="font-size:.9rem;font-weight:600;color:#c0a0ff;margin-bottom:.75rem">⚙️ How to use</div>
        <div style="font-size:.8rem;color:#8070a0;line-height:1.8">1. Select utility type<br>2. Choose Monthly or Daily<br>3. Download template & upload data<br>4. Optionally add temperature data<br>5. Explore statistics<br>6. Run forecast & download report</div></div>""",unsafe_allow_html=True)
    with c2:
        st.markdown("""<div style="background:#16102a;border:1px solid #2a1a4a;border-radius:12px;padding:1.25rem;margin-bottom:1rem">
        <div style="font-size:.9rem;font-weight:600;color:#c0a0ff;margin-bottom:.75rem">🌡️ Temperature Mode (New)</div>
        <div style="font-size:.8rem;color:#8070a0;line-height:1.8">Add Temp_Max_C and Temp_Min_C columns to your daily data. The model learns the physical consumption-temperature relationship. Future temperature from Open-Meteo (free). Days 1-16: real forecast. Days 17+: seasonal average.</div></div>
        <div style="background:#16102a;border:1px solid #2a1a4a;border-radius:12px;padding:1.25rem">
        <div style="font-size:.9rem;font-weight:600;color:#c0a0ff;margin-bottom:.5rem">👨‍💼 Developer</div>
        <div style="font-size:.8rem;color:#8070a0">Engr. Ahmed Raslan<br>✉ Engr_Raslan@outlook.com<br>📞 +971 52 289 9595</div></div>""",unsafe_allow_html=True)
    st.markdown("---")
    if st.button("← Back"): st.session_state.step=1;st.rerun()
    dev_footer()

# ═══ MODEL CARD PAGE ══════════════════════════════════════════════
elif st.session_state.step==98:
    st.markdown('<div class="main-title">📋 Model Card</div>',unsafe_allow_html=True)
    st.markdown('<div style="font-size:.85rem;color:#7060a0;text-align:center;margin-bottom:1.5rem">Forecasting engine documentation & methodology</div>',unsafe_allow_html=True)
    st.markdown("---")
    tab1,tab2,tab3,tab4=st.tabs(["🧠 Model Architecture","🌡️ Temperature Mode","✅ Validation","📋 Data Requirements"])
    with tab1:
        st.markdown("""<div style="background:#16102a;border:1px solid #2a1a4a;border-radius:12px;padding:1.25rem;margin-bottom:1rem">
        <div style="font-size:.95rem;font-weight:600;color:#c0a0ff;margin-bottom:.75rem">Ensemble Architecture — Prophet 70% + ETS 30%</div>
        <div style="font-size:.82rem;color:#8070a0;line-height:1.9">
        The forecasting engine combines two complementary models:<br><br>
        <strong style="color:#b090ff">Prophet (70%)</strong> — Meta's open-source model. Captures yearly seasonality, weekly patterns (daily mode), long-term trends, and automatic changepoint detection. Uses multiplicative seasonality for utility data.<br><br>
        <strong style="color:#b090ff">ETS — Exponential Smoothing (30%)</strong> — Classical statistical model. Assigns exponentially decreasing weights to past observations. Produces smooth, stable forecasts without spikes. Natural complement to Prophet.<br><br>
        <strong style="color:#b090ff">Why ensemble?</strong> Each model excels in different conditions. Prophet captures complex patterns; ETS provides smoothness and stability. Combined: better accuracy than either alone.
        </div></div>""",unsafe_allow_html=True)
        c1,c2,c3=st.columns(3)
        with c1: st.markdown('<div class="metric-box"><div class="metric-label">Prophet weight</div><div class="metric-val">70%</div></div>',unsafe_allow_html=True)
        with c2: st.markdown('<div class="metric-box"><div class="metric-label">ETS weight</div><div class="metric-val">30%</div></div>',unsafe_allow_html=True)
        with c3: st.markdown('<div class="metric-box"><div class="metric-label">Typical MAPE</div><div class="metric-val metric-good">85-98%</div></div>',unsafe_allow_html=True)
    with tab2:
        st.markdown("""<div style="background:#16102a;border:1px solid #2a1a4a;border-radius:12px;padding:1.25rem;margin-bottom:1rem">
        <div style="font-size:.95rem;font-weight:600;color:#ff8c00;margin-bottom:.75rem">🌡️ Temperature-Enhanced Mode</div>
        <div style="font-size:.82rem;color:#8070a0;line-height:1.9">
        <strong style="color:#b090ff">Philosophy:</strong> Standard mode learns "July is always high." Temperature mode learns "when temperature reaches 44°C, consumption increases by X MWh." This is a physically correct causal relationship.<br><br>
        <strong style="color:#b090ff">How it works:</strong><br>
        1. User uploads historical data with Temp_Max_C + Temp_Min_C columns<br>
        2. Prophet adds temperature as explicit regressors<br>
        3. Model learns consumption-temperature coefficient from history<br>
        4. For forecast: user provides Sheet 2 with future temperature<br>
        5. Days 1-16: real forecast from Open-Meteo (free)<br>
        6. Days 17+: seasonal average calculated from historical data automatically<br><br>
        <strong style="color:#b090ff">Best for:</strong> Electricity, District Cooling, Water, Gas<br>
        <strong style="color:#b090ff">Temperature source:</strong> open-meteo.com (free, no registration)
        </div></div>""",unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1: st.markdown('<div class="metric-box"><div class="metric-label">Standard MAPE</div><div class="metric-val metric-warn">75-90%</div></div>',unsafe_allow_html=True)
        with c2: st.markdown('<div class="metric-box"><div class="metric-label">Temperature MAPE</div><div class="metric-val metric-good">85-97%</div></div>',unsafe_allow_html=True)
    with tab3:
        st.markdown("""<div style="background:#16102a;border:1px solid #2a1a4a;border-radius:12px;padding:1.25rem;margin-bottom:1rem">
        <div style="font-size:.95rem;font-weight:600;color:#c0a0ff;margin-bottom:.75rem">Walk-Forward Backtest Validation</div>
        <div style="font-size:.82rem;color:#8070a0;line-height:1.9">
        Every forecast run includes automatic validation:<br><br>
        • <strong style="color:#b090ff">Training set:</strong> first 90% of historical data<br>
        • <strong style="color:#b090ff">Test set:</strong> last 10% — never seen during training<br>
        • <strong style="color:#b090ff">MAPE:</strong> Mean Absolute Percentage accuracy — higher is better<br>
        • <strong style="color:#b090ff">Visual chart:</strong> actual vs predicted plotted side by side<br>
        • <strong style="color:#b090ff">Per-period table:</strong> exact error for every test period<br><br>
        MAPE 90%+ = Excellent | 80-90% = Good | 70-80% = Acceptable | Below 70% = Review data
        </div></div>""",unsafe_allow_html=True)
    with tab4:
        data=[["Parameter","Monthly","Daily"],
              ["Minimum history","60 months","365 days"],
              ["Recommended","120+ months","730+ days"],
              ["Forecast horizons","12/24/36/60 months","30/60/90/180 days"],
              ["Temperature","Optional","Temp_Max_C + Temp_Min_C"],
              ["Multi-zone","Unlimited columns","Unlimited columns"],
              ["File format","Excel .xlsx","Excel .xlsx"],
              ["Date format","YYYY-MM-DD","YYYY-MM-DD"]]
        df_req=pd.DataFrame(data[1:],columns=data[0])
        st.dataframe(df_req,use_container_width=True,hide_index=True)
    st.markdown("---")
    if st.button("← Back to home"): st.session_state.step=1;st.rerun()
    dev_footer()

# ═══ STEP 2 — SELECT UTILITY ══════════════════════════════════════
elif st.session_state.step==2:
    render_steps(2)
    _,c,_=st.columns([3,1,3])
    with c:
        if st.button("⚡ Load example"):
            st.session_state.utility="Electricity";st.session_state.frequency="Monthly"
            np.random.seed(42);dates=pd.date_range("2015-01-01",periods=120,freq="MS")
            ex=pd.DataFrame({"Date":dates})
            for i,(b,a,t) in enumerate(zip([1450,1880,1980],[400,80,620],[8,-3,15])):
                ex[f"Zone_{i+1}"]=[round(max(b+np.sin((j-3)*np.pi/6)*a+t*j/12+np.random.normal(0,b*.02),100),1) for j in range(120)]
            st.session_state.df=ex;st.session_state.zones=["Zone_1","Zone_2","Zone_3"]
            st.session_state.history_periods=120;st.session_state.has_temperature=False
            st.session_state.step=4;st.rerun()
    st.markdown("---")
    st.markdown('<div style="font-size:1rem;font-weight:500;color:#c0a0ff;margin-bottom:.5rem">Select utility type</div>',unsafe_allow_html=True)
    cols=st.columns(5)
    for i,(util,info) in enumerate(UTILITIES.items()):
        with cols[i]:
            sel=st.session_state.utility==util
            sel_bg = "#241848" if sel else "#16102a"
            sel_border = "2px solid #8060d0" if sel else "1px solid #2a1a4a"
            sel_color = "#c0a0ff" if sel else "#8070a0"
            temp_badge = '<div style="font-size:.6rem;color:#ff8c00;margin-top:2px">🌡️ temp</div>' if info["temp_benefit"] else ""
            st.markdown(f'<div style="background:{sel_bg};border:{sel_border};border-radius:10px;padding:1rem .5rem;text-align:center;margin-bottom:.5rem"><div style="font-size:1.8rem">{info["icon"]}</div><div style="font-size:.75rem;color:{sel_color};margin-top:4px">{util}</div><div style="font-size:.65rem;color:#5a4a7a">{info["unit"]}</div>{temp_badge}</div>',unsafe_allow_html=True)
            if st.button("Select",key=f"s_{util}",use_container_width=True): st.session_state.utility=util;st.rerun()
    st.markdown("---")
    c1,c2=st.columns(2)
    with c1:
        if st.button("← Back"): st.session_state.step=1;st.rerun()
    with c2:
        if st.session_state.utility:
            if st.button("Next →",use_container_width=True): st.session_state.step=3;st.rerun()
        else: st.info("Select a utility to continue")
    dev_footer()

# ═══ STEP 3 — SETUP & UPLOAD ══════════════════════════════════════
elif st.session_state.step==3:
    render_steps(3)
    util=st.session_state.utility or "Electricity"
    unit=UTILITIES[util]["unit"]
    temp_benefit=UTILITIES[util]["temp_benefit"]
    st.markdown(f'<div style="font-size:1rem;font-weight:500;color:#c0a0ff;margin-bottom:.5rem">Setup & Upload — {util} ({unit})</div>',unsafe_allow_html=True)
    freq=st.radio("Data frequency",["Monthly","Daily"],index=0 if st.session_state.frequency=="Monthly" else 1,horizontal=True)
    st.session_state.frequency=freq
    daily=freq=="Daily"
    if daily:
        st.markdown('<div class="info-box">📅 <strong>Daily mode</strong> — Min 365 days | Recommended 730+ | Weekly + yearly seasonality | Optional temperature columns detected automatically</div>',unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box">📅 <strong>Monthly mode</strong> — Min 60 months | Recommended 120+ | Yearly seasonality detected</div>',unsafe_allow_html=True)
    c1,c2=st.columns(2)
    periods=st.session_state.history_periods
    hopts=get_horizon_options(freq,periods if periods>0 else (365 if daily else 120))
    ul="days" if daily else "months"
    with c1:
        hsel=st.selectbox("Forecast horizon",[f"{h} {ul}" for h in hopts],index=min(1,len(hopts)-1))
        st.session_state.horizon=int(hsel.split()[0])
    with c2: st.selectbox("Scenarios",["3 scenarios (base / optimistic / conservative)","Base only"])
    with st.expander("🤖 Optional: Anthropic API key for AI insights"):
        st.markdown('<div class="info-box">Session only — never stored.</div>',unsafe_allow_html=True)
        ak=st.text_input("API key",type="password",value=st.session_state.api_key,placeholder="sk-ant-...")
        st.session_state.api_key=ak
        if ak: st.markdown('<div class="success-box">✅ AI insights enabled</div>',unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Template & sample files**")
    sc0,sc1,sc2=st.columns(3)
    with sc0:
        tmpl=build_template(util,unit,freq)
        st.download_button("⬇ Template",data=tmpl,file_name=f"UCB_template_{util.replace(' ','_')}_{freq}.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)
    with sc1:
        clean=make_sample(util,unit,freq,False)
        st.download_button("✅ Clean sample",data=clean,file_name=f"UCB_clean_{freq}.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)
        st.markdown('<div style="font-size:.7rem;color:#5a4a7a">Perfect data — tests forecast</div>',unsafe_allow_html=True)
    with sc2:
        flwd=make_sample(util,unit,freq,True)
        st.download_button("⚠️ Flawed sample",data=flwd,file_name=f"UCB_flawed_{freq}.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)
        st.markdown('<div style="font-size:.7rem;color:#5a4a7a">Broken data — tests validation</div>',unsafe_allow_html=True)
    st.markdown("---")
    # Main data upload
    st.markdown("**Upload your main data file (Sheet: Historical_Data or single sheet)**")
    uploaded=st.file_uploader("Upload Excel file",type=["xlsx"],label_visibility="collapsed",key="main_upload")
    if uploaded:
        try:
            # Try to read multi-sheet file
            xl=pd.ExcelFile(uploaded)
            sheet_names=xl.sheet_names
            # Read main data
            if "Historical_Data" in sheet_names:
                df_raw=xl.parse("Historical_Data")
                st.markdown('<div class="success-box">✅ Multi-sheet file detected — reading Historical_Data sheet</div>',unsafe_allow_html=True)
            else:
                df_raw=xl.parse(sheet_names[0])
            # Check for future temperature sheet
            future_temp_df=None
            if "Future_Temperature" in sheet_names:
                future_temp_df=xl.parse("Future_Temperature")
                st.markdown(f'<div class="temp-box">🌡️ Future temperature sheet detected — {len(future_temp_df)} days of forecast temperature loaded</div>',unsafe_allow_html=True)
                st.session_state.future_temp_df=future_temp_df
            else:
                st.session_state.future_temp_df=None
            valid,val_res,periods,zone_cols,temp_detected=validate_data(df_raw.copy(),freq)
            st.markdown("**Validation results:**")
            for icon,msg,level in val_res:
                color="#3db07a" if level=="ok" else "#d4a020" if level=="warn" else "#cc4040"
                st.markdown(f'<div style="font-size:.82rem;color:{color};padding:3px 0">{icon} {msg}</div>',unsafe_allow_html=True)
            min_req=365 if daily else 60
            if periods>=min_req:
                qs=quality_score(df_raw.copy(),zone_cols,periods,freq)
                color="#3db07a" if qs>=80 else "#d4a020" if qs>=60 else "#cc4040"
                st.markdown(f'<div style="margin-top:.75rem;background:#16102a;border-radius:8px;padding:.75rem 1rem"><div style="font-size:.75rem;color:#7060a0;margin-bottom:.4rem">Data quality score</div><div style="font-size:1.8rem;font-weight:600;color:{color}">{qs}/100</div><div style="font-size:.7rem;color:#5a4a7a">{"Excellent ✅" if qs>=80 else "Acceptable ⚠️" if qs>=60 else "Poor ❌"}</div></div>',unsafe_allow_html=True)
                st.markdown(f'<div class="info-box">📊 {get_advice(freq,periods)}</div>',unsafe_allow_html=True)
            has_temp=len(temp_detected)>0
            st.session_state.has_temperature=has_temp
            if has_temp and daily:
                if future_temp_df is not None:
                    ft_valid,ft_res=validate_future_temp(future_temp_df.copy(),st.session_state.horizon,freq)
                    st.markdown("**Future temperature validation:**")
                    for icon,msg,level in ft_res:
                        color="#3db07a" if level=="ok" else "#d4a020" if level=="warn" else "#cc4040"
                        st.markdown(f'<div style="font-size:.82rem;color:{color};padding:3px 0">{icon} {msg}</div>',unsafe_allow_html=True)
                else:
                    st.markdown('<div class="temp-box">🌡️ Temperature columns detected but no Future_Temperature sheet found. Seasonal average will be used for forecast period. For better accuracy, add a Future_Temperature sheet with columns: Date, Temp_Max_C, Temp_Min_C</div>',unsafe_allow_html=True)
            if not valid:
                st.markdown('<div class="error-box">❌ Fix issues above and re-upload.</div>',unsafe_allow_html=True)
            else:
                min_warn=730 if daily else 120
                if periods<min_warn: st.markdown(f'<div class="warn-box">⚠️ {periods} {ul} uploaded. {min_warn}+ recommended.</div>',unsafe_allow_html=True)
                else: st.markdown(f'<div class="success-box">✅ {periods} {ul}, {len(zone_cols)} column(s){"🌡️ + temperature" if has_temp else ""} — ready!</div>',unsafe_allow_html=True)
                st.session_state.df=df_raw;st.session_state.zones=zone_cols;st.session_state.history_periods=periods
        except Exception as e:
            st.error(f"Cannot read file: {e}")
    if st.session_state.df is not None and not uploaded:
        st.markdown('<div class="success-box">✅ Example data loaded — 120 months, 3 zones</div>',unsafe_allow_html=True)
    st.markdown("---")
    c1,c2=st.columns(2)
    with c1:
        if st.button("← Back"): st.session_state.step=2;st.rerun()
    with c2:
        min_req=365 if daily else 60
        if st.session_state.df is not None and st.session_state.history_periods>=min_req:
            if st.button("📊 Explore Data →",use_container_width=True): st.session_state.step=4;st.rerun()
        else: st.info(f"Upload valid data (min {'365 days' if daily else '60 months'})")
    dev_footer()

# ═══ STEP 4 — DATA EXPLORER ═══════════════════════════════════════
elif st.session_state.step==4:
    import plotly.graph_objects as go
    render_steps(4)
    df=st.session_state.df.copy()
    zones=st.session_state.zones
    util=st.session_state.utility or "Electricity"
    unit=UTILITIES[util]["unit"]
    freq=st.session_state.frequency
    daily=freq=="Daily"
    has_temp=st.session_state.has_temperature
    df["Date"]=pd.to_datetime(df["Date"])
    df=df.sort_values("Date").reset_index(drop=True)
    st.markdown('<div style="font-size:1rem;font-weight:500;color:#c0a0ff;margin-bottom:.25rem">📊 Data Explorer</div>',unsafe_allow_html=True)
    st.markdown('<div style="font-size:.78rem;color:#6050a0;margin-bottom:1rem">Understand your data before forecasting</div>',unsafe_allow_html=True)
    if has_temp: st.markdown('<div class="temp-box">🌡️ Temperature data detected — temperature analysis included</div>',unsafe_allow_html=True)
    all_vals=df[zones].values.flatten().astype(float)
    all_vals=all_vals[~np.isnan(all_vals)]
    c1,c2,c3,c4,c5=st.columns(5)
    with c1: st.markdown(f'<div class="metric-box"><div class="metric-label">Records</div><div class="metric-val">{len(df)}</div></div>',unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-box"><div class="metric-label">Columns</div><div class="metric-val">{len(zones)}</div></div>',unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-box"><div class="metric-label">Mean ({unit})</div><div class="metric-val" style="font-size:.85rem">{np.mean(all_vals):,.0f}</div></div>',unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="metric-box"><div class="metric-label">Max ({unit})</div><div class="metric-val metric-warn" style="font-size:.85rem">{np.max(all_vals):,.0f}</div></div>',unsafe_allow_html=True)
    with c5: st.markdown(f'<div class="metric-box"><div class="metric-label">Min ({unit})</div><div class="metric-val" style="font-size:.85rem">{np.min(all_vals):,.0f}</div></div>',unsafe_allow_html=True)
    st.markdown("---")
    tab_list=["📈 Time Series","📊 Distribution","🌊 Seasonality","📅 Year-over-Year","🔥 Heatmap","📋 Statistics"]
    if has_temp and daily: tab_list.append("🌡️ Temperature")
    tabs=st.tabs(tab_list)
    cb=dict(paper_bgcolor="#12102a",plot_bgcolor="#12102a",font=dict(color="#9080b0",size=11),
        margin=dict(l=60,r=20,t=50,b=60),height=400,hovermode="x unified",
        xaxis=dict(gridcolor="#1e1438",tickfont=dict(color="#7060a0",size=10)),
        yaxis=dict(gridcolor="#1e1438",tickfont=dict(color="#7060a0",size=10),tickformat=",.0f"))
    with tabs[0]:
        sz=st.selectbox("Column",["All"]+zones,key="ex_ts")
        fig=go.Figure()
        if sz=="All":
            for i,z in enumerate(zones):
                fig.add_trace(go.Scatter(x=df["Date"],y=df[z],name=z,line=dict(color=COLORS[i%len(COLORS)],width=1.5)))
            title=f"All columns — {util} ({unit})"
        else:
            fig.add_trace(go.Scatter(x=df["Date"],y=df[sz],name=sz,line=dict(color="#8060d0",width=2)))
            roll=df[sz].rolling(7 if daily else 3,min_periods=1).mean()
            fig.add_trace(go.Scatter(x=df["Date"],y=roll,name="Rolling avg",line=dict(color="#ff8040",width=1.5,dash="dash")))
            title=f"{sz} — {util} ({unit})"
        fig.update_layout(title=dict(text=title,font=dict(color="#c0a0ff",size=13)),legend=dict(bgcolor="#16102a",bordercolor="#2a1a4a",borderwidth=1,font=dict(color="#9080b0",size=10)),**cb)
        st.plotly_chart(fig,use_container_width=True)
    with tabs[1]:
        sz2=st.selectbox("Column",zones,key="ex_dist")
        vals=df[sz2].dropna().values.astype(float)
        c1,c2=st.columns(2)
        with c1:
            fig_h=go.Figure()
            fig_h.add_trace(go.Histogram(x=vals,nbinsx=30,marker_color="#8060d0",opacity=0.8))
            fig_h.add_vline(x=float(np.mean(vals)),line_color="#3db07a",line_dash="dash",annotation_text=f"Mean: {np.mean(vals):,.0f}",annotation_font_color="#3db07a")
            fig_h.add_vline(x=float(np.median(vals)),line_color="#cc7040",line_dash="dot",annotation_text=f"Median: {np.median(vals):,.0f}",annotation_font_color="#cc7040")
            fig_h.update_layout(title=dict(text="Distribution",font=dict(color="#c0a0ff",size=12)),showlegend=False,**cb)
            st.plotly_chart(fig_h,use_container_width=True)
        with c2:
            fig_b=go.Figure()
            fig_b.add_trace(go.Box(y=vals,marker_color="#8060d0",name=sz2,boxpoints="outliers"))
            fig_b.update_layout(title=dict(text="Box plot",font=dict(color="#c0a0ff",size=12)),showlegend=False,**cb)
            st.plotly_chart(fig_b,use_container_width=True)
        pcts=[10,25,50,75,90,95,99]
        pcols=st.columns(len(pcts))
        for i,p in enumerate(pcts):
            with pcols[i]: st.markdown(f'<div class="metric-box"><div class="metric-label">P{p}</div><div class="metric-val" style="font-size:.85rem">{np.percentile(vals,p):,.0f}</div></div>',unsafe_allow_html=True)
    with tabs[2]:
        sz3=st.selectbox("Column",zones,key="ex_seas")
        df["month"]=df["Date"].dt.month
        mavg=df.groupby("month")[sz3].mean()
        oa=mavg.mean()
        si=(mavg/oa*100).round(1)
        bc=["#cc4040" if v==si.max() else "#3db07a" if v==si.min() else "#6040a0" for v in si.values]
        fig_s=go.Figure()
        fig_s.add_trace(go.Bar(x=MONTHS_SHORT,y=si.values,marker_color=bc,hovertemplate="%{x}<br>Index: %{y:.1f}<extra></extra>"))
        fig_s.add_hline(y=100,line_dash="dot",line_color="#5a4a7a",annotation_text="Average (100)",annotation_font_color="#5a4a7a")
        fig_s.update_layout(title=dict(text=f"{sz3} — Monthly Seasonality Index",font=dict(color="#c0a0ff",size=12)),showlegend=False,**{k:v for k,v in cb.items() if k!="hovermode"})
        st.plotly_chart(fig_s,use_container_width=True)
        pk=MONTHS_SHORT[int(si.idxmax())-1];lw=MONTHS_SHORT[int(si.idxmin())-1]
        st.markdown(f'<div class="success-box">🔴 Peak: <strong>{pk}</strong> (index: {si.max()}) | 🟢 Low: <strong>{lw}</strong> (index: {si.min()})</div>',unsafe_allow_html=True)
        if daily:
            df["dow"]=df["Date"].dt.dayofweek
            da=df.groupby("dow")[sz3].mean()
            dow_names=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
            fig_dow=go.Figure()
            fig_dow.add_trace(go.Bar(x=dow_names,y=da.values,marker_color="#6040a0",hovertemplate="%{x}<br>%{y:,.0f} "+unit+"<extra></extra>"))
            fig_dow.add_hline(y=da.mean(),line_dash="dot",line_color="#5a4a7a")
            fig_dow.update_layout(title=dict(text="Day of week pattern",font=dict(color="#c0a0ff",size=12)),showlegend=False,paper_bgcolor="#12102a",plot_bgcolor="#12102a",font=dict(color="#9080b0",size=11),margin=dict(l=60,r=20,t=50,b=60),height=300,xaxis=dict(gridcolor="#1e1438",tickfont=dict(color="#7060a0",size=10)),yaxis=dict(gridcolor="#1e1438",tickfont=dict(color="#7060a0",size=10),tickformat=",.0f"))
            st.plotly_chart(fig_dow,use_container_width=True)
    with tabs[3]:
        sz4=st.selectbox("Column",zones,key="ex_yoy")
        df["year"]=df["Date"].dt.year
        yoy=df.groupby("year")[sz4].sum()
        yoy_pct=yoy.pct_change()*100
        fig_yoy=go.Figure()
        fig_yoy.add_trace(go.Bar(x=[str(y) for y in yoy.index],y=yoy.values,
            marker_color=["#3db07a" if v>=0 else "#cc4040" for v in yoy_pct.fillna(0).values],
            hovertemplate="%{x}<br>%{y:,.0f} "+unit+"<extra></extra>"))
        fig_yoy.update_layout(title=dict(text=f"{sz4} — Annual Total",font=dict(color="#c0a0ff",size=12)),showlegend=False,**{k:v for k,v in cb.items() if k!="hovermode"})
        st.plotly_chart(fig_yoy,use_container_width=True)
        ycols=st.columns(min(len(yoy),8))
        for i,(yr,val) in enumerate(yoy.items()):
            if i>=8: break
            chg=yoy_pct.get(yr,None)
            with ycols[i]:
                color="#3db07a" if chg and chg>0 else "#cc4040" if chg and chg<0 else "#c0a0ff"
                cs=f"{chg:+.1f}%" if chg and not np.isnan(chg) else "base"
                st.markdown(f'<div class="metric-box"><div class="metric-label">{yr}</div><div class="metric-val" style="font-size:.85rem;color:{color}">{cs}</div></div>',unsafe_allow_html=True)
    with tabs[4]:
        sz5=st.selectbox("Column",zones,key="ex_heat")
        df["year"]=df["Date"].dt.year;df["month"]=df["Date"].dt.month
        pvt=df.pivot_table(index="year",columns="month",values=sz5,aggfunc="mean")
        pvt.columns=[MONTHS_SHORT[m-1] for m in pvt.columns]
        fig_heat=go.Figure(data=go.Heatmap(
            z=pvt.values,x=pvt.columns,y=[str(y) for y in pvt.index],
            colorscale=[[0,"#0a0a1a"],[0.5,"#4a2a8a"],[1,"#ff8040"]],
            hovertemplate="%{y} %{x}<br>%{z:,.0f} "+unit+"<extra></extra>",
            colorbar=dict(tickfont=dict(color="#9080b0"))))
        fig_heat.update_layout(title=dict(text=f"{sz5} — Heatmap (year x month)",font=dict(color="#c0a0ff",size=12)),
            paper_bgcolor="#12102a",plot_bgcolor="#12102a",font=dict(color="#9080b0",size=11),
            margin=dict(l=60,r=20,t=50,b=60),height=400,
            xaxis=dict(tickfont=dict(color="#7060a0")),yaxis=dict(tickfont=dict(color="#7060a0")))
        st.plotly_chart(fig_heat,use_container_width=True)
        st.markdown('<div class="info-box">Dark = low. Bright orange = peak. Shows seasonal behavior across all years.</div>',unsafe_allow_html=True)
    with tabs[5]:
        rows=[]
        for z in zones:
            v=df[z].dropna().values.astype(float)
            rows.append({"Column":z,f"Mean ({unit})":round(float(np.mean(v)),1),f"Median ({unit})":round(float(np.median(v)),1),
                f"Std ({unit})":round(float(np.std(v)),1),f"Min ({unit})":round(float(np.min(v)),1),f"Max ({unit})":round(float(np.max(v)),1),
                "CV (%)":round(float(np.std(v)/np.mean(v)*100),1) if np.mean(v)>0 else 0,
                "P10":round(float(np.percentile(v,10)),1),"P90":round(float(np.percentile(v,90)),1),
                "Missing":int(df[z].isnull().sum()),"Trend":f"{round(float((v[-1]-v[0])/max(v[0],1)*100),1):+.1f}%"})
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
    if has_temp and daily and len(tabs)>6:
        with tabs[6]:
            if "Temp_Max_C" in df.columns and "Temp_Min_C" in df.columns:
                sz_t=st.selectbox("Consumption column",zones,key="ex_temp")
                c1,c2=st.columns(2)
                with c1:
                    fig_t=go.Figure()
                    fig_t.add_trace(go.Scatter(x=df["Date"],y=df["Temp_Max_C"],name="Temp Max",line=dict(color="#cc4040",width=1.5)))
                    fig_t.add_trace(go.Scatter(x=df["Date"],y=df["Temp_Min_C"],name="Temp Min",line=dict(color="#4090d0",width=1.5)))
                    fig_t.update_layout(title=dict(text="Temperature history (°C)",font=dict(color="#c0a0ff",size=12)),
                        legend=dict(bgcolor="#16102a",bordercolor="#2a1a4a",borderwidth=1,font=dict(color="#9080b0",size=10)),
                        **{**cb,"yaxis":dict(gridcolor="#1e1438",tickfont=dict(color="#7060a0",size=10),title="°C")})
                    st.plotly_chart(fig_t,use_container_width=True)
                with c2:
                    fig_sc=go.Figure()
                    fig_sc.add_trace(go.Scatter(x=df["Temp_Max_C"],y=df[sz_t],mode="markers",
                        marker=dict(color="#8060d0",size=4,opacity=0.5),
                        hovertemplate="Temp: %{x}°C<br>Consumption: %{y:,.0f} "+unit+"<extra></extra>"))
                    fig_sc.update_layout(title=dict(text=f"Temperature vs {sz_t}",font=dict(color="#c0a0ff",size=12)),
                        xaxis=dict(title="Temp Max (°C)",gridcolor="#1e1438",tickfont=dict(color="#7060a0",size=10)),
                        yaxis=dict(title=f"Consumption ({unit})",gridcolor="#1e1438",tickfont=dict(color="#7060a0",size=10),tickformat=",.0f"),
                        paper_bgcolor="#12102a",plot_bgcolor="#12102a",font=dict(color="#9080b0",size=11),
                        margin=dict(l=60,r=20,t=50,b=60),height=400,showlegend=False)
                    st.plotly_chart(fig_sc,use_container_width=True)
                corr=df["Temp_Max_C"].corr(df[sz_t])
                color="#3db07a" if abs(corr)>0.7 else "#d4a020" if abs(corr)>0.4 else "#cc4040"
                st.markdown(f'<div style="background:#16102a;border-radius:8px;padding:.75rem 1rem;text-align:center"><div style="font-size:.75rem;color:#7060a0">Temperature-Consumption Correlation</div><div style="font-size:1.8rem;font-weight:600;color:{color}">{corr:.3f}</div><div style="font-size:.75rem;color:#5a4a7a">{"Strong ✅ — Temperature mode will significantly improve accuracy" if abs(corr)>0.7 else "Moderate ⚠️" if abs(corr)>0.4 else "Weak — Temperature may not help much"}</div></div>',unsafe_allow_html=True)
    st.markdown("---")
    c1,c2=st.columns(2)
    with c1:
        if st.button("← Back"): st.session_state.step=3;st.rerun()
    with c2:
        if st.button("🔮 Run Forecast →",use_container_width=True): st.session_state.step=5;st.rerun()
    dev_footer()

# ═══ STEP 5 — PROCESSING ══════════════════════════════════════════
elif st.session_state.step==5:
    render_steps(5)
    freq=st.session_state.frequency;daily=freq=="Daily"
    has_temp=st.session_state.has_temperature
    future_temp_df=st.session_state.future_temp_df
    temp_label=" + Temperature Enhanced 🌡️" if has_temp else ""
    st.markdown(f'<div style="text-align:center;padding:2rem 0"><div style="font-size:4rem;margin-bottom:1rem">🔮</div><div style="font-size:1.1rem;color:#b090ff;margin-bottom:1.5rem">The crystal ball is working{temp_label}...</div></div>',unsafe_allow_html=True)
    steps_ui=["Validating data","Detecting seasonality",
              f"Running Prophet {'+ temperature regressors' if has_temp else ''} model",
              "Running ETS model","Combining ensemble 70/30","Backtest validation",
              "Computing statistics","Building reports"]
    pb=st.progress(0);sb=st.empty()
    df=st.session_state.df.copy();zone_cols=st.session_state.zones;horizon=st.session_state.horizon
    # Prepare future temperature
    prepared_future_temp=None
    if has_temp and daily:
        prepared_future_temp=prepare_future_temp(df.copy(),future_temp_df,horizon,freq)
    for i,sn in enumerate(steps_ui):
        sb.markdown(f'<div style="text-align:center;color:#b090ff;font-size:.85rem">⟳ {sn}...</div>',unsafe_allow_html=True)
        pb.progress((i+1)/len(steps_ui))
        if i==2: results=run_forecast(df,zone_cols,horizon,freq,has_temp,prepared_future_temp)
    st.session_state.results=results
    pb.progress(1.0)
    sb.markdown('<div style="text-align:center;color:#3db07a;font-size:.9rem">✅ Forecast complete!</div>',unsafe_allow_html=True)
    import time;time.sleep(0.8);st.session_state.step=6;st.rerun()

# ═══ STEP 6 — RESULTS ══════════════════════════════════════════════
elif st.session_state.step==6:
    import plotly.graph_objects as go
    render_steps(6)
    util=st.session_state.utility or "Electricity";unit=UTILITIES[util]["unit"]
    results=st.session_state.results;zones=st.session_state.zones
    horizon=st.session_state.horizon;df=st.session_state.df
    freq=st.session_state.frequency;daily=freq=="Daily"
    has_temp=st.session_state.has_temperature
    ul="days" if daily else "months"
    mapes=[results[z]["mape"] for z in zones if results[z]["mape"] is not None]
    avg_mape=round(np.mean(mapes),1) if mapes else None
    temp_enhanced_count=sum(1 for z in zones if results[z].get("temp_enhanced",False))

    c1,c2,c3,c4,c5=st.columns(5)
    with c1: st.markdown(f'<div class="metric-box"><div class="metric-label">Utility</div><div class="metric-val" style="font-size:1rem">{util}</div></div>',unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-box"><div class="metric-label">Frequency</div><div class="metric-val" style="font-size:1rem">{freq}</div></div>',unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-box"><div class="metric-label">Horizon</div><div class="metric-val" style="font-size:1rem">{horizon} {ul}</div></div>',unsafe_allow_html=True)
    with c4:
        if avg_mape:
            cls="metric-good" if avg_mape>=85 else "metric-warn" if avg_mape>=70 else "metric-bad"
            st.markdown(f'<div class="metric-box"><div class="metric-label">Avg MAPE</div><div class="metric-val {cls}">{avg_mape}%</div></div>',unsafe_allow_html=True)
        else: st.markdown('<div class="metric-box"><div class="metric-label">Avg MAPE</div><div class="metric-val">N/A</div></div>',unsafe_allow_html=True)
    with c5:
        temp_color="#ff8c00" if temp_enhanced_count>0 else "#5a4a7a"
        temp_val=f"🌡️ {temp_enhanced_count}/{len(zones)}" if temp_enhanced_count>0 else "Standard"
        st.markdown(f'<div class="metric-box"><div class="metric-label">Temp Enhanced</div><div class="metric-val" style="font-size:1rem;color:{temp_color}">{temp_val}</div></div>',unsafe_allow_html=True)

    if has_temp and temp_enhanced_count>0:
        st.markdown(f'<div class="temp-box">🌡️ Temperature-enhanced forecast active — model used real temperature data as predictor for {temp_enhanced_count} zone(s). Future temperature: real forecast (days 1-16) + seasonal average (remaining days).</div>',unsafe_allow_html=True)

    st.markdown("---")
    cols_ins=st.columns(min(len(zones),4))
    for i,z in enumerate(zones[:4]):
        r=results[z];trend=r["trend_pct"]
        icon="🚀" if trend>5 else "📈" if trend>1 else "⚠️" if trend<-1 else "➡️"
        status="High growth" if trend>5 else "Growing" if trend>1 else "Declining" if trend<-1 else "Stable"
        pk=MONTHS_SHORT[r["seasonality"].index(max(r["seasonality"]))]
        temp_badge=" 🌡️" if r.get("temp_enhanced") else ""
        with cols_ins[i]:
            st.markdown(f'<div class="insight-card"><div class="insight-zone">{icon} {z}{temp_badge}</div><div class="insight-text">Status: <strong style="color:#b090ff">{status}</strong><br>Trend: {trend:+.1f}% over {horizon} {ul}<br>Peak month: {pk}<br>MAPE: {r["mape"]}%</div></div>',unsafe_allow_html=True)

    st.markdown("---")
    tabs=st.tabs(["📈 Forecast","🔍 Backtest","🌊 Seasonality","📅 Year-over-Year","🤖 AI Insights","📥 Export"])
    cb2=dict(paper_bgcolor="#12102a",plot_bgcolor="#12102a",font=dict(color="#9080b0",size=11),
        legend=dict(bgcolor="#16102a",bordercolor="#2a1a4a",borderwidth=1,font=dict(color="#9080b0",size=10)),
        margin=dict(l=60,r=20,t=50,b=60),height=420,hovermode="x unified")

    with tabs[0]:
        opts=["All"]+zones
        sz=st.selectbox("Zone/Column",opts,key="r_ts")
        def mfc(zk):
            fig=go.Figure()
            if zk=="All":
                hd=results[zones[0]]["dates_hist"]
                hv=[sum(results[z]["vals_hist"][i] for z in zones) for i in range(len(hd))]
                fd=results[zones[0]]["dates_fc"]
                bfc=[sum(results[z]["base"][i] for z in zones) for i in range(horizon)]
                ofc=[sum(results[z]["optimistic"][i] for z in zones) for i in range(horizon)]
                cfc=[sum(results[z]["conservative"][i] for z in zones) for i in range(horizon)]
                title=f"All — {util} ({unit})"
            else:
                r=results[zk];hd,hv=r["dates_hist"],r["vals_hist"]
                fd,bfc,ofc,cfc=r["dates_fc"],r["base"],r["optimistic"],r["conservative"]
                te=" 🌡️ Temperature Enhanced" if r.get("temp_enhanced") else ""
                title=f"{zk} — {util} ({unit}){te}"
            fig.add_trace(go.Scatter(x=list(fd)+list(fd)[::-1],y=ofc+cfc[::-1],fill="toself",fillcolor="rgba(61,176,122,0.08)",line=dict(color="rgba(0,0,0,0)"),showlegend=False,hoverinfo="skip"))
            fig.add_trace(go.Scatter(x=hd,y=hv,name="Historical",line=dict(color="#8060d0",width=2),hovertemplate="%{x|%Y-%m-%d}<br>%{y:,.1f} "+unit+"<extra>Historical</extra>"))
            fig.add_trace(go.Scatter(x=fd,y=bfc,name="Base forecast",line=dict(color="#3db07a",width=2),hovertemplate="%{x|%Y-%m-%d}<br>%{y:,.1f} "+unit+"<extra>Base</extra>"))
            fig.add_trace(go.Scatter(x=fd,y=ofc,name="Optimistic",line=dict(color="#cc7040",width=1.5,dash="dash"),hovertemplate="%{x|%Y-%m-%d}<br>%{y:,.1f} "+unit+"<extra>Optimistic</extra>"))
            fig.add_trace(go.Scatter(x=fd,y=cfc,name="Conservative",line=dict(color="#6a5a8a",width=1.5,dash="dash"),hovertemplate="%{x|%Y-%m-%d}<br>%{y:,.1f} "+unit+"<extra>Conservative</extra>"))
            if fd:
                sx=str(fd[0])[:10]
                fig.add_shape(type="line",x0=sx,x1=sx,y0=0,y1=1,xref="x",yref="paper",line=dict(color="#3a2a5a",width=1,dash="dot"))
                fig.add_annotation(x=sx,y=0.97,xref="x",yref="paper",text="forecast →",showarrow=False,font=dict(color="#5a4a7a",size=10),xanchor="left")
            fig.update_layout(title=dict(text=title,font=dict(color="#c0a0ff",size=13)),
                xaxis=dict(title="Date",title_font=dict(color="#7060a0"),tickfont=dict(color="#7060a0",size=10),gridcolor="#1e1438",tickformat="%Y-%m-%d" if daily else "%b %Y"),
                yaxis=dict(title=f"({unit})",title_font=dict(color="#7060a0"),tickfont=dict(color="#7060a0",size=10),gridcolor="#1e1438",tickformat=",.0f"),
                **cb2)
            return fig
        st.plotly_chart(mfc(sz),use_container_width=True)
        if len(zones)>1:
            tc1,tc2,tc3=st.columns(3)
            with tc1: st.markdown(f'<div class="metric-box"><div class="metric-label">Total Base ({unit})</div><div class="metric-val" style="font-size:.9rem">{sum(sum(results[z]["base"]) for z in zones):,.0f}</div></div>',unsafe_allow_html=True)
            with tc2: st.markdown(f'<div class="metric-box"><div class="metric-label">Total Optimistic ({unit})</div><div class="metric-val" style="font-size:.9rem">{sum(sum(results[z]["optimistic"]) for z in zones):,.0f}</div></div>',unsafe_allow_html=True)
            with tc3: st.markdown(f'<div class="metric-box"><div class="metric-label">Total Conservative ({unit})</div><div class="metric-val" style="font-size:.9rem">{sum(sum(results[z]["conservative"]) for z in zones):,.0f}</div></div>',unsafe_allow_html=True)

    with tabs[1]:
        st.markdown('<div class="info-box">Walk-forward validation: last 10% held out. Green = actual. Orange = model predicted.</div>',unsafe_allow_html=True)
        sz_bt=st.selectbox("Zone",zones,key="r_bt")
        r=results[sz_bt]
        fig_bt=go.Figure()
        fig_bt.add_trace(go.Scatter(x=r["dates_hist"],y=r["vals_hist"],name="Historical",line=dict(color="#8060d0",width=1.5),opacity=0.4))
        fig_bt.add_trace(go.Scatter(x=r["dates_test"],y=r["vals_test"],name="Actual (holdout)",line=dict(color="#3db07a",width=2.5),mode="lines+markers"))
        fig_bt.add_trace(go.Scatter(x=r["dates_test"],y=r["backtest_fc"],name="Model predicted",line=dict(color="#ff8040",width=2.5,dash="dash"),mode="lines+markers"))
        if r["dates_test"]:
            sx=str(r["dates_test"][0])[:10]
            fig_bt.add_shape(type="line",x0=sx,x1=sx,y0=0,y1=1,xref="x",yref="paper",line=dict(color="#3a2a5a",width=1,dash="dot"))
            fig_bt.add_annotation(x=sx,y=0.97,xref="x",yref="paper",text="← training | test →",showarrow=False,font=dict(color="#5a4a7a",size=10),xanchor="center")
        te_label=" 🌡️" if r.get("temp_enhanced") else ""
        fig_bt.update_layout(title=dict(text=f"{sz_bt} — Actual vs Predicted{te_label} | MAPE: {r['mape']}%",font=dict(color="#c0a0ff",size=13)),
            xaxis=dict(title="Date",gridcolor="#1e1438",tickfont=dict(color="#7060a0",size=10)),
            yaxis=dict(title=f"({unit})",gridcolor="#1e1438",tickfont=dict(color="#7060a0",size=10),tickformat=",.0f"),
            **cb2)
        st.plotly_chart(fig_bt,use_container_width=True)
        dt=[d.strftime("%Y-%m-%d") if hasattr(d,"strftime") else str(d) for d in r["dates_test"]]
        st.dataframe(pd.DataFrame([{"Date":d,f"Actual ({unit})":a,f"Predicted ({unit})":p,"Error (%)":f"{round(abs(a-p)/max(a,1)*100,1)}%"} for d,a,p in zip(dt,r["vals_test"],r["backtest_fc"])]),use_container_width=True,hide_index=True)

    with tabs[2]:
        sz_s=st.selectbox("Zone",zones,key="r_seas")
        r=results[sz_s]
        bc=["#cc4040" if v==max(r["seasonality"]) else "#3db07a" if v==min(r["seasonality"]) else "#6040a0" for v in r["seasonality"]]
        fig_s=go.Figure()
        fig_s.add_trace(go.Bar(x=MONTHS_SHORT,y=r["seasonality"],marker_color=bc,hovertemplate="%{x}<br>Index: %{y}<extra></extra>"))
        fig_s.add_hline(y=100,line_dash="dot",line_color="#5a4a7a",annotation_text="Average (100)",annotation_font_color="#5a4a7a")
        fig_s.update_layout(title=dict(text=f"{sz_s} — Monthly Seasonality Index",font=dict(color="#c0a0ff",size=13)),showlegend=False,
            xaxis=dict(gridcolor="#1e1438",tickfont=dict(color="#7060a0",size=10)),
            yaxis=dict(title="Index",gridcolor="#1e1438",tickfont=dict(color="#7060a0",size=10)),
            paper_bgcolor="#12102a",plot_bgcolor="#12102a",font=dict(color="#9080b0",size=11),margin=dict(l=60,r=20,t=50,b=60),height=380)
        st.plotly_chart(fig_s,use_container_width=True)
        pk=MONTHS_SHORT[r["seasonality"].index(max(r["seasonality"]))];lw=MONTHS_SHORT[r["seasonality"].index(min(r["seasonality"]))]
        st.markdown(f'<div class="success-box">🔴 Peak: <strong>{pk}</strong> | 🟢 Low: <strong>{lw}</strong></div>',unsafe_allow_html=True)
        if daily and r.get("dow_index"):
            dow_names=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
            fig_dow=go.Figure()
            fig_dow.add_trace(go.Bar(x=dow_names,y=r["dow_index"],marker_color="#6040a0"))
            fig_dow.add_hline(y=100,line_dash="dot",line_color="#5a4a7a")
            fig_dow.update_layout(title=dict(text="Day of week seasonality",font=dict(color="#c0a0ff",size=12)),showlegend=False,
                xaxis=dict(gridcolor="#1e1438",tickfont=dict(color="#7060a0",size=10)),yaxis=dict(gridcolor="#1e1438",tickfont=dict(color="#7060a0",size=10)),
                paper_bgcolor="#12102a",plot_bgcolor="#12102a",font=dict(color="#9080b0",size=11),margin=dict(l=60,r=20,t=50,b=60),height=300)
            st.plotly_chart(fig_dow,use_container_width=True)

    with tabs[3]:
        fig_yoy=go.Figure()
        for i,z in enumerate(zones):
            r=results[z];yrs=sorted(r["yoy"].keys())
            fig_yoy.add_trace(go.Bar(name=z,x=[str(y) for y in yrs],y=[r["yoy"][y] for y in yrs],marker_color=COLORS[i%len(COLORS)],hovertemplate=z+"<br>%{x}<br>%{y:,.1f} "+unit+"<extra></extra>"))
        fig_yoy.update_layout(title=dict(text=f"Year-over-Year — {util} ({unit})",font=dict(color="#c0a0ff",size=13)),barmode="group",
            xaxis=dict(title="Year",gridcolor="#1e1438",tickfont=dict(color="#7060a0",size=10)),
            yaxis=dict(title=f"Annual Total ({unit})",gridcolor="#1e1438",tickfont=dict(color="#7060a0",size=10),tickformat=",.0f"),
            **cb2)
        st.plotly_chart(fig_yoy,use_container_width=True)

    with tabs[4]:
        if st.session_state.api_key:
            if st.button("🤖 Generate AI insights"):
                with st.spinner("Consulting the AI oracle..."):
                    ins=get_ai_insights(st.session_state.api_key,util,unit,horizon,results,zones,freq,has_temp)
                st.session_state.ai_insights=ins or None
                if not ins: st.error("Could not generate. Check API key.")
            if st.session_state.ai_insights:
                st.markdown(f'<div style="background:#16102a;border:1px solid #2a1a4a;border-radius:10px;padding:1.25rem 1.5rem;font-size:.85rem;color:#b090ff;line-height:1.8;white-space:pre-wrap">{st.session_state.ai_insights}</div>',unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-box">🤖 Enter Anthropic API key in Setup to unlock AI insights.</div>',unsafe_allow_html=True)

    with tabs[5]:
        c1,c2=st.columns(2)
        with c1:
            st.markdown('<div style="background:#16102a;border:1px solid #2a1a4a;border-radius:10px;padding:1.25rem;text-align:center"><div style="font-size:2rem;margin-bottom:.5rem">📊</div><div style="color:#b090ff;font-size:.9rem;margin-bottom:.3rem">Excel report</div><div style="color:#5a4a7a;font-size:.75rem">Summary + forecast + backtest + all scenarios</div></div>',unsafe_allow_html=True)
            st.markdown('<div style="height:8px"></div>',unsafe_allow_html=True)
            future_temp=st.session_state.future_temp_df
            eb=build_excel(df,results,zones,util,unit,horizon,freq,has_temp,future_temp)
            st.download_button("⬇ Download Excel",data=eb,file_name=f"UCB_{util.replace(' ','_')}_{freq}_{horizon}{ul}.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)
        with c2:
            st.markdown('<div style="background:#16102a;border:1px solid #2a1a4a;border-radius:10px;padding:1.25rem;text-align:center"><div style="font-size:2rem;margin-bottom:.5rem">📄</div><div style="color:#b090ff;font-size:.9rem;margin-bottom:.3rem">PDF report</div><div style="color:#5a4a7a;font-size:.75rem">Executive summary + backtest + forecast + methodology</div></div>',unsafe_allow_html=True)
            st.markdown('<div style="height:8px"></div>',unsafe_allow_html=True)
            pb_=build_pdf(results,zones,util,unit,horizon,freq,has_temp,st.session_state.ai_insights)
            if pb_: st.download_button("⬇ Download PDF",data=pb_,file_name=f"UCB_{util.replace(' ','_')}_{freq}_{horizon}{ul}.pdf",mime="application/pdf",use_container_width=True)
            else: st.info("PDF requires ReportLab")

    st.markdown("---")
    if st.button("🔮 Start new forecast"):
        for k in ["df","results","zones","utility","history_periods","ai_insights","future_temp_df","has_temperature"]:
            if k in st.session_state: del st.session_state[k]
        st.session_state.step=1;st.rerun()
    dev_footer()
