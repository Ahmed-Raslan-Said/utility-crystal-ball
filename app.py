import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import warnings
warnings.filterwarnings('ignore')

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
.quality-bar{height:12px;border-radius:6px;background:linear-gradient(90deg,#3db07a,#d4a020,#cc4040);position:relative;margin:8px 0}
.quality-needle{position:absolute;top:-4px;width:4px;height:20px;background:#fff;border-radius:2px;transform:translateX(-50%)}
</style>
""", unsafe_allow_html=True)

# ── Session state ────────────────────────────────────────────────────────────
for k,v in {
    'step':1,'utility':None,'horizon':24,'df':None,'zones':[],
    'results':None,'api_key':'','history_months':0,'ai_insights':None
}.items():
    if k not in st.session_state:
        st.session_state[k]=v

UTILITIES={
    'Electricity':{'icon':'⚡','unit':'MW'},
    'Water':{'icon':'💧','unit':'m³'},
    'Gas':{'icon':'🔥','unit':'m³'},
    'District Cooling':{'icon':'❄️','unit':'TonHr'},
    'TSE':{'icon':'♻️','unit':'m³'},
}
HORIZONS=[12,24,36,60]
MONTHS_SHORT=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

def render_steps(current):
    steps=['Utility','Setup','Upload','Forecast','Results']
    dots=[]
    for i,s in enumerate(steps):
        n=i+1
        if n<current: dc='step-dot-done';sym='✓';lc='step-label'
        elif n==current: dc='step-dot-active';sym=str(n);lc='step-label-active'
        else: dc='';sym=str(n);lc='step-label'
        line='<div class="step-line"></div>' if i<len(steps)-1 else ''
        dots.append(f'<div style="display:flex;align-items:center;gap:6px"><div class="step-dot {dc}">{sym}</div><span class="{lc}">{s}</span></div>{line}')
    st.markdown(f'<div class="step-indicator">{"".join(dots)}</div>',unsafe_allow_html=True)

def dev_footer():
    st.markdown("""<div class="dev-footer">
        <span>🔮 Developed by <strong style="color:#8060b0">Engr. Ahmed Raslan</strong></span>
        <span style="display:flex;gap:24px"><span>✉ Engr_Raslan@outlook.com</span><span>📞 +971 52 289 9595</span></span>
    </div>""",unsafe_allow_html=True)

# ── Data quality score ───────────────────────────────────────────────────────
def quality_score(df, zone_cols, months):
    score=100
    if months<60: score-=40
    elif months<120: score-=15
    total=df[zone_cols].size
    missing=df[zone_cols].isnull().sum().sum()
    miss_pct=missing/total*100 if total>0 else 0
    if miss_pct>20: score-=30
    elif miss_pct>5: score-=15
    for col in zone_cols:
        mean=df[col].mean()
        if mean>0 and (df[col]>mean*4).any(): score-=10;break
    dups=df.duplicated(subset=['Date']).sum() if 'Date' in df.columns else 0
    if dups>0: score-=20
    return max(0,min(100,score))

# ── Validation ───────────────────────────────────────────────────────────────
def validate_data(df):
    results=[];ok=True
    if 'Date' not in df.columns:
        results.append(('❌','Date column not found','err'));ok=False
    else:
        results.append(('✅','Date column found','ok'))
    zone_cols=[c for c in df.columns if c!='Date']
    if len(zone_cols)==0:
        results.append(('❌','No zone columns found','err'));ok=False
    else:
        preview=', '.join(zone_cols[:5])+('...' if len(zone_cols)>5 else '')
        results.append(('✅',f'{len(zone_cols)} zone(s) detected: {preview}','ok'))
    if not ok: return False,results,0,zone_cols
    try:
        df['Date']=pd.to_datetime(df['Date'])
        df=df.sort_values('Date').reset_index(drop=True)
        results.append(('✅','Date format recognized — monthly','ok'))
    except:
        results.append(('❌','Date column could not be parsed','err'));ok=False
    dups=df['Date'].duplicated().sum()
    if dups>0:
        results.append(('❌',f'{dups} duplicate month(s) found — remove duplicates','err'));ok=False
    else:
        results.append(('✅','No duplicate months','ok'))
    months=len(df)
    if months<60:
        results.append(('❌',f'History too short: {months} months — minimum 60 required','err'));ok=False
    elif months<120:
        results.append(('⚠️',f'History: {months} months — 120+ recommended for full accuracy','warn'))
    else:
        results.append(('✅',f'History: {months} months — excellent ✅','ok'))
    total=df[zone_cols].size
    missing=df[zone_cols].isnull().sum().sum()
    miss_pct=round(missing/total*100,1) if total>0 else 0
    if miss_pct>20:
        results.append(('❌',f'Missing values: {miss_pct}% — too high (max 20%)','err'));ok=False
    elif miss_pct>5:
        results.append(('⚠️',f'Missing values: {miss_pct}% — review recommended','warn'))
    else:
        results.append(('✅',f'Missing values: {miss_pct}% — acceptable','ok'))
    spike_flag=False
    for col in zone_cols:
        mean=df[col].mean()
        if mean>0 and (df[col]>mean*4).any(): spike_flag=True
    if spike_flag:
        results.append(('⚠️','Possible consumption spikes detected — review data','warn'))
    else:
        results.append(('✅','No impossible spikes detected','ok'))
    return ok,results,months,zone_cols

# ── Sample data generators ───────────────────────────────────────────────────
def make_clean_sample(utility,unit):
    np.random.seed(42)
    dates=pd.date_range('2015-01-01',periods=120,freq='MS')
    df=pd.DataFrame({'Date':dates.strftime('%Y-%m-%d')})
    configs={
        'Electricity':[(1450,400,8),(1880,80,-3),(1980,620,15)],
        'Water':[(8500,1200,30),(6200,800,15),(4100,600,-20)],
        'Gas':[(1200,300,6),(850,200,4),(2000,400,-10)],
        'District Cooling':[(3200,800,12),(2100,500,8),(1500,300,-8)],
        'TSE':[(2100,400,10),(1400,250,6),(900,150,-5)],
    }
    cfg=configs.get(utility,configs['Electricity'])
    for i,(base,amp,trend) in enumerate(cfg):
        vals=[round(max(base+np.sin((j-3)*np.pi/6)*amp+trend*j/12+np.random.normal(0,base*.02),50),1) for j in range(120)]
        df[f'Zone_{i+1}']=vals
    buf=BytesIO()
    df.to_excel(buf,index=False,engine='openpyxl')
    buf.seek(0)
    return buf

def make_flawed_sample(utility,unit):
    np.random.seed(99)
    dates=pd.date_range('2021-01-01',periods=45,freq='MS')
    df=pd.DataFrame({'Date':dates.strftime('%Y-%m-%d')})
    base=1500
    vals=[round(max(base+np.sin(j*np.pi/6)*300+np.random.normal(0,50),100),1) for j in range(45)]
    vals[20]=base*6  # spike
    vals[30]=None    # missing
    vals[31]=None
    vals[32]=None
    df['Zone_1']=vals
    df['Zone_2']=[round(max(800+np.random.normal(0,30),100),1) for _ in range(45)]
    # Add duplicate months
    dup_row=pd.DataFrame({'Date':[dates[10].strftime('%Y-%m-%d'),dates[15].strftime('%Y-%m-%d'),dates[20].strftime('%Y-%m-%d')],
                          'Zone_1':[1200,1300,1100],'Zone_2':[700,750,720]})
    df=pd.concat([df,dup_row],ignore_index=True)
    buf=BytesIO()
    df.to_excel(buf,index=False,engine='openpyxl')
    buf.seek(0)
    return buf

# ── Forecast engine ──────────────────────────────────────────────────────────
def run_forecast(df,zone_cols,horizon):
    results={}
    df['Date']=pd.to_datetime(df['Date'])
    df=df.sort_values('Date').reset_index(drop=True)
    for zone in zone_cols:
        series=df[['Date',zone]].copy().dropna()
        series.columns=['ds','y']
        n=len(series)
        test_size=max(12,int(n*0.10))
        train=series.iloc[:-test_size].copy()
        test=series.iloc[-test_size:].copy()
        hist_vals=series['y'].values.tolist()
        last_date=series['ds'].iloc[-1]
        future_dates=pd.date_range(start=last_date+pd.DateOffset(months=1),periods=horizon,freq='MS')

        # Prophet
        prophet_fc=None;prophet_bt=None
        try:
            from prophet import Prophet
            m=Prophet(yearly_seasonality=True,weekly_seasonality=False,daily_seasonality=False,
                      seasonality_mode='multiplicative',changepoint_prior_scale=0.05,interval_width=0.80)
            m.fit(series)
            future=m.make_future_dataframe(periods=horizon,freq='MS')
            prophet_fc=m.predict(future).tail(horizon)['yhat'].values
            mb=Prophet(yearly_seasonality=True,weekly_seasonality=False,daily_seasonality=False,
                       seasonality_mode='multiplicative',changepoint_prior_scale=0.05)
            mb.fit(train)
            fb=mb.make_future_dataframe(periods=test_size,freq='MS')
            prophet_bt=mb.predict(fb).tail(test_size)['yhat'].values
        except: prophet_fc=None

        # ETS
        ets_fc=None;ets_bt=None
        try:
            from statsmodels.tsa.holtwinters import ExponentialSmoothing
            hw=ExponentialSmoothing(series['y'],trend='add',seasonal='add',seasonal_periods=12)
            ets_fc=hw.fit(optimized=True).forecast(horizon)
            hwb=ExponentialSmoothing(train['y'],trend='add',seasonal='add',seasonal_periods=12)
            ets_bt=hwb.fit(optimized=True).forecast(test_size)
        except: ets_fc=None

        # Ensemble
        if prophet_fc is not None and ets_fc is not None:
            base_fc=np.array(prophet_fc)*0.70+np.array(ets_fc)*0.30
            backtest_fc=np.array(prophet_bt)*0.70+np.array(ets_bt)*0.30 if prophet_bt is not None and ets_bt is not None else (prophet_bt if prophet_bt is not None else np.array(ets_bt))
        elif prophet_fc is not None:
            base_fc=np.array(prophet_fc);backtest_fc=prophet_bt if prophet_bt is not None else np.array(hist_vals[-test_size:])
        elif ets_fc is not None:
            base_fc=np.array(ets_fc);backtest_fc=np.array(ets_bt) if ets_bt is not None else np.array(hist_vals[-test_size:])
        else:
            sl=min(12,len(hist_vals))
            base_fc=np.array([hist_vals[-(sl-i%sl)] for i in range(horizon)])
            trend=(hist_vals[-1]-hist_vals[0])/max(len(hist_vals),1)
            base_fc=base_fc+np.arange(1,horizon+1)*trend*0.5
            backtest_fc=np.array(hist_vals[-test_size:])

        # Smooth spikes
        hm=np.mean(hist_vals);hs=np.std(hist_vals)
        base_fc=np.clip(base_fc,max(hm-3*hs,0),hm+3*hs)
        base_fc=np.maximum(base_fc,0)

        # MAPE
        actual_test=test['y'].values
        mape=None
        try:
            errors=np.abs((actual_test-backtest_fc)/np.maximum(actual_test,1))
            mape=round((1-np.mean(errors))*100,1)
            mape=max(0,min(100,mape))
        except: pass

        # Seasonality — average by month
        series['month']=series['ds'].dt.month
        monthly_avg=series.groupby('month')['y'].mean().reindex(range(1,13),fill_value=0)
        overall_avg=monthly_avg.mean()
        seasonality_index=(monthly_avg/overall_avg*100).round(1).tolist() if overall_avg>0 else [100]*12

        # YoY
        series['year']=series['ds'].dt.year
        yoy=series.groupby('year')['y'].sum().round(1).to_dict()

        results[zone]={
            'dates_hist':series['ds'].tolist(),
            'vals_hist':[round(v,1) for v in hist_vals],
            'dates_test':test['ds'].tolist(),
            'vals_test':[round(v,1) for v in actual_test.tolist()],
            'backtest_fc':[round(v,1) for v in backtest_fc.tolist()],
            'dates_fc':future_dates.tolist(),
            'base':[round(v,1) for v in base_fc.tolist()],
            'optimistic':[round(v,1) for v in (base_fc*1.06).tolist()],
            'conservative':[round(v,1) for v in (base_fc*0.94).tolist()],
            'mape':mape,
            'trend_pct':round(((base_fc[-1]-hist_vals[-1])/max(hist_vals[-1],1))*100,1),
            'test_size':test_size,
            'seasonality':seasonality_index,
            'yoy':yoy,
        }
    return results

def get_ai_insights(api_key,utility,unit,horizon,results,zone_cols):
    try:
        import requests
        lines=[f"- {z}: avg {round(np.mean(results[z]['vals_hist'][-12:]),1)} {unit}, forecast end {results[z]['base'][-1]} {unit}, trend {results[z]['trend_pct']:+.1f}%, MAPE {results[z]['mape']}%" for z in zone_cols[:8]]
        prompt=f"""You are a senior utility planning consultant writing a professional executive report.
Utility: {utility} ({unit}) | Forecast horizon: {horizon} months | Zones: {len(zone_cols)}
Zone summary:\n{chr(10).join(lines)}
Write a professional report with:
1. Overall consumption outlook (2-3 sentences)
2. Key zones to watch (3-4 bullets)
3. Strategic infrastructure recommendations (3-4 bullets)
4. Model confidence note (1-2 sentences)
Use professional utility planning language. Be concise."""
        resp=requests.post("https://api.anthropic.com/v1/messages",
            headers={"x-api-key":api_key,"anthropic-version":"2023-06-01","content-type":"application/json"},
            json={"model":"claude-sonnet-4-20250514","max_tokens":800,"messages":[{"role":"user","content":prompt}]},timeout=30)
        if resp.status_code==200: return resp.json()['content'][0]['text']
    except: pass
    return None

def build_excel(df,results,zone_cols,utility,unit,horizon):
    buf=BytesIO()
    with pd.ExcelWriter(buf,engine='openpyxl') as writer:
        # Summary
        rows=[]
        for z in zone_cols:
            r=results[z]
            rows.append({'Zone':z,
                f'Avg Historical ({unit})':round(np.mean(r['vals_hist']),1),
                f'Last Historical ({unit})':r['vals_hist'][-1],
                f'Total Forecast Base ({unit})':round(sum(r['base']),1),
                f'Forecast End Base ({unit})':r['base'][-1],
                f'Forecast End Optimistic ({unit})':r['optimistic'][-1],
                f'Forecast End Conservative ({unit})':r['conservative'][-1],
                'Growth Trend (%)':r['trend_pct'],
                'MAPE Accuracy (%)':r['mape'] if r['mape'] else 'N/A'})
        # Total row
        total_row={'Zone':'TOTAL'}
        for k in rows[0]:
            if k!='Zone' and k!='Growth Trend (%)' and k!='MAPE Accuracy (%)':
                try: total_row[k]=round(sum(row[k] for row in rows if isinstance(row[k],(int,float))),1)
                except: total_row[k]=''
        total_row['Growth Trend (%)']=''
        total_row['MAPE Accuracy (%)']=round(np.mean([r['mape'] for r in results.values() if r['mape']]),1)
        rows.append(total_row)
        pd.DataFrame(rows).to_excel(writer,sheet_name='Summary',index=False)
        # Per zone
        for z in zone_cols:
            r=results[z]
            dates_fc=[d.strftime('%b %Y') if hasattr(d,'strftime') else str(d) for d in r['dates_fc']]
            pd.DataFrame({'Month':dates_fc,f'Base ({unit})':r['base'],
                f'Optimistic ({unit})':r['optimistic'],f'Conservative ({unit})':r['conservative']
            }).to_excel(writer,sheet_name=z[:31],index=False)
        # Backtest
        bt_rows=[]
        for z in zone_cols:
            r=results[z]
            dates_t=[d.strftime('%b %Y') if hasattr(d,'strftime') else str(d) for d in r['dates_test']]
            for dt,act,pred in zip(dates_t,r['vals_test'],r['backtest_fc']):
                err=round(abs(act-pred)/max(act,1)*100,1) if act>0 else None
                bt_rows.append({'Zone':z,'Month':dt,f'Actual ({unit})':act,f'Predicted ({unit})':pred,'Error (%)':err})
        pd.DataFrame(bt_rows).to_excel(writer,sheet_name='Backtest Validation',index=False)
        # Seasonality
        seas_rows=[]
        for z in zone_cols:
            row={'Zone':z}
            for i,m in enumerate(MONTHS_SHORT): row[m]=results[z]['seasonality'][i]
            seas_rows.append(row)
        pd.DataFrame(seas_rows).to_excel(writer,sheet_name='Seasonality Index',index=False)
        # YoY
        all_years=sorted(set(yr for r in results.values() for yr in r['yoy'].keys()))
        yoy_rows=[]
        for z in zone_cols:
            row={'Zone':z}
            for yr in all_years: row[str(yr)]=results[z]['yoy'].get(yr,'')
            yoy_rows.append(row)
        pd.DataFrame(yoy_rows).to_excel(writer,sheet_name='Year-over-Year',index=False)
        df.to_excel(writer,sheet_name='Historical Data',index=False)
    buf.seek(0)
    return buf

def build_template(utility,unit):
    buf=BytesIO()
    dates=pd.date_range(start='2015-01-01',periods=120,freq='MS')
    tdf=pd.DataFrame({'Date':dates.strftime('%Y-%m-%d')})
    for i in range(1,4): tdf[f'Zone_{i}']=''
    with pd.ExcelWriter(buf,engine='openpyxl') as writer:
        tdf.to_excel(writer,sheet_name='Data',index=False)
        pd.DataFrame({'Instructions':[f'Utility: {utility}',f'Unit: {unit}',
            'Fill consumption values per zone.','Add zones as needed (Zone_4, Zone_5...).',
            'Date: YYYY-MM-DD format.','Minimum 60 months. 120+ recommended.',
        ]}).to_excel(writer,sheet_name='Instructions',index=False)
    buf.seek(0)
    return buf

def build_pdf(results,zone_cols,utility,unit,horizon,ai_insights=None):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,HRFlowable
        from reportlab.lib.enums import TA_CENTER
        buf=BytesIO()
        doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=2*cm,leftMargin=2*cm,topMargin=2*cm,bottomMargin=2*cm)
        styles=getSampleStyleSheet()
        TS=ParagraphStyle('T',parent=styles['Title'],fontSize=20,textColor=colors.HexColor('#4a2a8a'),spaceAfter=6,alignment=TA_CENTER,fontName='Helvetica-Bold')
        SS=ParagraphStyle('S',parent=styles['Normal'],fontSize=10,textColor=colors.HexColor('#6050a0'),spaceAfter=4,alignment=TA_CENTER)
        H2=ParagraphStyle('H2',parent=styles['Heading2'],fontSize=12,textColor=colors.HexColor('#4a2a8a'),spaceBefore=12,spaceAfter=6,fontName='Helvetica-Bold')
        BS=ParagraphStyle('B',parent=styles['Normal'],fontSize=9,textColor=colors.HexColor('#2a1a4a'),spaceAfter=4,leading=14)
        FS=ParagraphStyle('F',parent=styles['Normal'],fontSize=7,textColor=colors.HexColor('#8060b0'),alignment=TA_CENTER)
        story=[]
        story.append(Spacer(1,.5*cm))
        story.append(Paragraph('🔮 Utility Crystal Ball',TS))
        story.append(Paragraph('Consumption Forecast Report',SS))
        story.append(Paragraph(f'{utility} | Unit: {unit} | Horizon: {horizon} months | Zones: {len(zone_cols)}',SS))
        story.append(HRFlowable(width='100%',thickness=1,color=colors.HexColor('#8060d0'),spaceAfter=10))
        # Summary table
        story.append(Paragraph('Forecast Accuracy Summary',H2))
        td=[['Zone',f'Avg Hist ({unit})',f'Forecast End ({unit})','Growth (%)','MAPE']]
        for z in zone_cols:
            r=results[z]
            td.append([z,f"{round(np.mean(r['vals_hist']),1):,.1f}",f"{r['base'][-1]:,.1f}",f"{r['trend_pct']:+.1f}%",f"{r['mape']}%" if r['mape'] else 'N/A'])
        t=Table(td,colWidths=[3*cm,4*cm,4*cm,3*cm,3*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#4a2a8a')),('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),8),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#f5f0ff'),colors.white]),
            ('GRID',(0,0),(-1,-1),.5,colors.HexColor('#c0a0ff')),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ]))
        story.append(t);story.append(Spacer(1,.4*cm))
        # Seasonality
        story.append(Paragraph('Seasonality Index (100 = average month)',H2))
        sh=[['Zone']+MONTHS_SHORT]
        for z in zone_cols: sh.append([z]+[str(v) for v in results[z]['seasonality']])
        st_=Table(sh,colWidths=[3*cm]+[1.2*cm]*12)
        st_.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#6a3aaa')),('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),7),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#f8f5ff'),colors.white]),
            ('GRID',(0,0),(-1,-1),.5,colors.HexColor('#c0a0ff')),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
        ]))
        story.append(st_);story.append(Spacer(1,.4*cm))
        # Backtest
        story.append(Paragraph('Backtest Validation — Actual vs Predicted (10% holdout)',H2))
        for z in zone_cols:
            r=results[z]
            story.append(Paragraph(f'Zone: {z} | MAPE Accuracy: {r["mape"]}%',ParagraphStyle('ZH',parent=BS,fontName='Helvetica-Bold')))
            dates_t=[d.strftime('%b %Y') if hasattr(d,'strftime') else str(d) for d in r['dates_test']]
            btd=[['Month',f'Actual ({unit})',f'Predicted ({unit})','Error (%)']]
            for dt,act,pred in zip(dates_t,r['vals_test'],r['backtest_fc']):
                err=round(abs(act-pred)/max(act,1)*100,1) if act>0 else 0
                btd.append([dt,f'{act:,.1f}',f'{pred:,.1f}',f'{err:.1f}%'])
            bt=Table(btd,colWidths=[3.5*cm,4*cm,4*cm,3.5*cm])
            bt.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#6a3aaa')),('TEXTCOLOR',(0,0),(-1,0),colors.white),
                ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),7),
                ('ALIGN',(0,0),(-1,-1),'CENTER'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#f8f5ff'),colors.white]),
                ('GRID',(0,0),(-1,-1),.5,colors.HexColor('#c0a0ff')),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
            ]))
            story.append(bt);story.append(Spacer(1,.3*cm))
        # Forecast tables
        story.append(Paragraph('Detailed Forecast — All Scenarios',H2))
        for z in zone_cols:
            r=results[z]
            story.append(Paragraph(f'Zone: {z} | Growth: {r["trend_pct"]:+.1f}%',ParagraphStyle('ZH2',parent=BS,fontName='Helvetica-Bold')))
            dates_fc=[d.strftime('%b %Y') if hasattr(d,'strftime') else str(d) for d in r['dates_fc']]
            fcd=[['Month',f'Base ({unit})',f'Optimistic ({unit})',f'Conservative ({unit})']]
            for dt,b,o,c in zip(dates_fc,r['base'],r['optimistic'],r['conservative']):
                fcd.append([dt,f'{b:,.1f}',f'{o:,.1f}',f'{c:,.1f}'])
            ft=Table(fcd,colWidths=[3.5*cm,4*cm,4*cm,4*cm])
            ft.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#4a2a8a')),('TEXTCOLOR',(0,0),(-1,0),colors.white),
                ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),7),
                ('ALIGN',(0,0),(-1,-1),'CENTER'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#f5f0ff'),colors.white]),
                ('GRID',(0,0),(-1,-1),.5,colors.HexColor('#c0a0ff')),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
            ]))
            story.append(ft);story.append(Spacer(1,.3*cm))
        if ai_insights:
            story.append(HRFlowable(width='100%',thickness=1,color=colors.HexColor('#8060d0'),spaceAfter=8))
            story.append(Paragraph('AI-Powered Executive Insights',H2))
            for line in ai_insights.split('\n'):
                if line.strip(): story.append(Paragraph(line.strip(),BS))
        story.append(HRFlowable(width='100%',thickness=1,color=colors.HexColor('#8060d0'),spaceAfter=8))
        story.append(Paragraph('Methodology',H2))
        story.append(Paragraph(f'Ensemble: Prophet (70%) + ETS (30%). Walk-forward backtest: 10% holdout ({results[zone_cols[0]]["test_size"]} months). Horizon: {horizon} months. Scenarios: Base / Optimistic (+6%) / Conservative (-6%).',BS))
        story.append(Spacer(1,.3*cm))
        story.append(HRFlowable(width='100%',thickness=.5,color=colors.HexColor('#c0a0ff')))
        story.append(Spacer(1,.2*cm))
        story.append(Paragraph('🔮 Utility Crystal Ball | Engr. Ahmed Raslan | Engr_Raslan@outlook.com | +971 52 289 9595',FS))
        doc.build(story)
        buf.seek(0)
        return buf
    except Exception as e:
        return None

# ═══════════════════════════════════════════════════════════════════════════
# STEP 1 — LANDING
# ═══════════════════════════════════════════════════════════════════════════
if st.session_state.step==1:
    st.markdown('<div style="text-align:center;padding:2rem 0 1rem"><div style="font-size:5rem;margin-bottom:.75rem">🔮</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="main-title">Utility Crystal Ball</div>',unsafe_allow_html=True)
    st.markdown('<div class="main-tagline">"See your consumption future — before it arrives"</div>',unsafe_allow_html=True)
    st.markdown('<div class="main-desc">Advanced utility consumption forecasting for water, electricity, gas, district cooling and TSE. Powered by AI ensemble models. Built for planners. Trusted by data.</div>',unsafe_allow_html=True)
    _,c,_=st.columns([1,1,1])
    with c:
        if st.button("🔮  Enter if you're ready...",use_container_width=True):
            st.session_state.step=2;st.rerun()
    st.markdown('---')
    _,c2,_=st.columns([1,2,1])
    with c2:
        if st.button("ℹ️  About this platform",use_container_width=True):
            st.session_state.step=99;st.rerun()
    dev_footer()

# ═══════════════════════════════════════════════════════════════════════════
# ABOUT PAGE
# ═══════════════════════════════════════════════════════════════════════════
elif st.session_state.step==99:
    st.markdown('<div class="main-title">🔮 About Utility Crystal Ball</div>',unsafe_allow_html=True)
    st.markdown('---')
    c1,c2=st.columns(2)
    with c1:
        st.markdown("""
        <div style="background:#16102a;border:1px solid #2a1a4a;border-radius:12px;padding:1.25rem;margin-bottom:1rem">
        <div style="font-size:.9rem;font-weight:600;color:#c0a0ff;margin-bottom:.75rem">🎯 What it does</div>
        <div style="font-size:.8rem;color:#8070a0;line-height:1.8">
        Utility Crystal Ball forecasts future utility consumption using AI ensemble models. 
        Upload your historical monthly data and receive multi-scenario forecasts with 
        measurable accuracy — ready for capital planning, asset management, and operations.
        </div></div>

        <div style="background:#16102a;border:1px solid #2a1a4a;border-radius:12px;padding:1.25rem;margin-bottom:1rem">
        <div style="font-size:.9rem;font-weight:600;color:#c0a0ff;margin-bottom:.75rem">⚙️ How to use</div>
        <div style="font-size:.8rem;color:#8070a0;line-height:1.8">
        1. Select your utility type<br>
        2. Download the data template<br>
        3. Fill your historical monthly data (min 60 months)<br>
        4. Upload and run forecast<br>
        5. Review results and download report
        </div></div>
        """,unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div style="background:#16102a;border:1px solid #2a1a4a;border-radius:12px;padding:1.25rem;margin-bottom:1rem">
        <div style="font-size:.9rem;font-weight:600;color:#c0a0ff;margin-bottom:.75rem">🧠 Methodology</div>
        <div style="font-size:.8rem;color:#8070a0;line-height:1.8">
        <strong style="color:#b090ff">Prophet (70%)</strong> — Meta's time series model. 
        Captures yearly seasonality, long-term trends, and calendar effects automatically.<br><br>
        <strong style="color:#b090ff">ETS (30%)</strong> — Exponential Smoothing. 
        Provides stable, smooth forecasting component that reduces volatility.<br><br>
        <strong style="color:#b090ff">Walk-forward backtest</strong> — Last 10% of your data 
        is held out to measure real predictive accuracy (MAPE).
        </div></div>

        <div style="background:#16102a;border:1px solid #2a1a4a;border-radius:12px;padding:1.25rem;margin-bottom:1rem">
        <div style="font-size:.9rem;font-weight:600;color:#c0a0ff;margin-bottom:.75rem">📋 Data requirements</div>
        <div style="font-size:.8rem;color:#8070a0;line-height:1.8">
        • Format: Excel (.xlsx)<br>
        • Column 1: Date (YYYY-MM-DD)<br>
        • Columns 2+: Zone consumption values<br>
        • Minimum: 60 months history<br>
        • Recommended: 120 months (10 years)<br>
        • Units: MW / m³ / TonHr per utility
        </div></div>
        """,unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#16102a;border:1px solid #2a1a4a;border-radius:12px;padding:1.25rem;margin-bottom:1rem">
    <div style="font-size:.9rem;font-weight:600;color:#c0a0ff;margin-bottom:.75rem">👨‍💼 Developer</div>
    <div style="font-size:.8rem;color:#8070a0;line-height:1.8">
    <strong style="color:#b090ff">Engr. Ahmed Raslan</strong> — Asset management and utility planning engineer with extensive experience 
    in infrastructure forecasting, capital planning, and operational optimization.<br><br>
    ✉ Engr_Raslan@outlook.com &nbsp;|&nbsp; 📞 +971 52 289 9595
    </div></div>
    """,unsafe_allow_html=True)
    st.markdown('---')
    if st.button("← Back to home"):
        st.session_state.step=1;st.rerun()
    dev_footer()

# ═══════════════════════════════════════════════════════════════════════════
# STEP 2 — SELECT UTILITY
# ═══════════════════════════════════════════════════════════════════════════
elif st.session_state.step==2:
    render_steps(2)
    _,c,_=st.columns([3,1,3])
    with c:
        if st.button("⚡ Load example"):
            st.session_state.utility='Electricity'
            np.random.seed(42)
            dates=pd.date_range('2015-01-01',periods=120,freq='MS')
            ex=pd.DataFrame({'Date':dates})
            for i,(base,amp,trend) in enumerate(zip([1450,1880,1980],[400,80,620],[8,-3,15])):
                ex[f'Zone_{i+1}']=[round(max(base+np.sin((j-3)*np.pi/6)*amp+trend*j/12+np.random.normal(0,base*.02),100),1) for j in range(120)]
            st.session_state.df=ex;st.session_state.zones=['Zone_1','Zone_2','Zone_3']
            st.session_state.history_months=120;st.session_state.step=3;st.rerun()
    st.markdown('---')
    st.markdown('<div style="font-size:1rem;font-weight:500;color:#c0a0ff;margin-bottom:.25rem">Select utility type</div>',unsafe_allow_html=True)
    st.markdown('<div style="font-size:.78rem;color:#6050a0;margin-bottom:1rem">Choose the utility you want to forecast</div>',unsafe_allow_html=True)
    cols=st.columns(5)
    for i,(util,info) in enumerate(UTILITIES.items()):
        with cols[i]:
            sel=st.session_state.utility==util
            st.markdown(f'<div style="background:{"#241848" if sel else "#16102a"};border:{"2px solid #8060d0" if sel else "1px solid #2a1a4a"};border-radius:10px;padding:1rem .5rem;text-align:center;margin-bottom:.5rem"><div style="font-size:1.8rem">{info["icon"]}</div><div style="font-size:.75rem;color:{"#c0a0ff" if sel else "#8070a0"};margin-top:4px">{util}</div><div style="font-size:.65rem;color:#5a4a7a">{info["unit"]}</div></div>',unsafe_allow_html=True)
            if st.button("Select",key=f"sel_{util}",use_container_width=True):
                st.session_state.utility=util;st.rerun()
    st.markdown('---')
    c1,c2=st.columns(2)
    with c1:
        if st.button("← Back"): st.session_state.step=1;st.rerun()
    with c2:
        if st.session_state.utility:
            if st.button("Next →",use_container_width=True): st.session_state.step=3;st.rerun()
        else: st.info("Please select a utility to continue")
    dev_footer()

# ═══════════════════════════════════════════════════════════════════════════
# STEP 3 — SETUP + UPLOAD
# ═══════════════════════════════════════════════════════════════════════════
elif st.session_state.step==3:
    render_steps(3)
    util=st.session_state.utility
    unit=UTILITIES[util]['unit']
    st.markdown(f'<div style="font-size:1rem;font-weight:500;color:#c0a0ff;margin-bottom:.25rem">Setup & Upload — {util} ({unit})</div>',unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        horizon=st.selectbox("Forecast horizon",[f"{h} months" for h in HORIZONS],index=1)
        st.session_state.horizon=int(horizon.split()[0])
    with c2:
        st.selectbox("Scenario output",['3 scenarios (base / optimistic / conservative)','Base case only'])
    with st.expander("🤖 Optional: Anthropic API key for AI-powered insights"):
        st.markdown('<div class="info-box">Session only — never stored. Get yours at console.anthropic.com</div>',unsafe_allow_html=True)
        api_key=st.text_input("API key",type="password",value=st.session_state.api_key,placeholder="sk-ant-...")
        st.session_state.api_key=api_key
        if api_key: st.markdown('<div class="success-box">✅ AI insights will be added to your PDF report</div>',unsafe_allow_html=True)
    st.markdown('---')
    st.markdown("**Step 1 — Download the data template**")
    tmpl=build_template(util,unit)
    st.download_button(f"⬇ Download {util} template (.xlsx)",data=tmpl,
        file_name=f"UCB_template_{util.replace(' ','_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.markdown('---')
    st.markdown("**Step 2 — No data yet? Download a sample file to test**")
    sc1,sc2=st.columns(2)
    with sc1:
        clean=make_clean_sample(util,unit)
        st.download_button(f"✅ Download clean sample (120 months)",data=clean,
            file_name=f"UCB_{util.replace(' ','_')}_clean_sample.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)
        st.markdown('<div style="font-size:.72rem;color:#5a4a7a">Perfect data — tests successful forecast</div>',unsafe_allow_html=True)
    with sc2:
        flawed=make_flawed_sample(util,unit)
        st.download_button(f"⚠️ Download flawed sample (validation test)",data=flawed,
            file_name=f"UCB_{util.replace(' ','_')}_flawed_sample.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)
        st.markdown('<div style="font-size:.72rem;color:#5a4a7a">Intentionally broken — tests validation gates</div>',unsafe_allow_html=True)
    st.markdown('---')
    st.markdown("**Step 3 — Upload your completed file**")
    uploaded=st.file_uploader("Upload Excel file",type=['xlsx'],label_visibility='collapsed')
    if uploaded:
        try:
            df_raw=pd.read_excel(uploaded)
            valid,val_results,months,zone_cols=validate_data(df_raw.copy())
            st.markdown("**Validation results:**")
            for icon,msg,level in val_results:
                color='#3db07a' if level=='ok' else '#d4a020' if level=='warn' else '#cc4040'
                st.markdown(f'<div style="font-size:.82rem;color:{color};padding:3px 0">{icon} {msg}</div>',unsafe_allow_html=True)
            if months>=60:
                qs=quality_score(df_raw.copy(),zone_cols,months)
                color='#3db07a' if qs>=80 else '#d4a020' if qs>=60 else '#cc4040'
                st.markdown(f'<div style="margin-top:.75rem;background:#16102a;border-radius:8px;padding:.75rem 1rem"><div style="font-size:.75rem;color:#7060a0;margin-bottom:.4rem">Data quality score</div><div style="font-size:1.8rem;font-weight:600;color:{color}">{qs}/100</div><div style="font-size:.7rem;color:#5a4a7a">{"Excellent ✅" if qs>=80 else "Acceptable ⚠️" if qs>=60 else "Poor ❌"}</div></div>',unsafe_allow_html=True)
            if not valid:
                st.markdown('<div class="error-box">❌ Data did not pass validation. Fix issues above and re-upload.</div>',unsafe_allow_html=True)
            else:
                if months<120: st.markdown(f'<div class="warn-box">⚠️ {months} months uploaded. 120+ recommended for maximum accuracy.</div>',unsafe_allow_html=True)
                else: st.markdown(f'<div class="success-box">✅ {months} months, {len(zone_cols)} zones — ready to forecast!</div>',unsafe_allow_html=True)
                st.session_state.df=df_raw;st.session_state.zones=zone_cols;st.session_state.history_months=months
        except Exception as e:
            st.error(f"Could not read file: {e}")
    if st.session_state.df is not None and not uploaded:
        st.markdown('<div class="success-box">✅ Example data loaded — 120 months, 3 zones (Electricity)</div>',unsafe_allow_html=True)
    st.markdown('---')
    c1,c2=st.columns(2)
    with c1:
        if st.button("← Back"): st.session_state.step=2;st.rerun()
    with c2:
        if st.session_state.df is not None and st.session_state.history_months>=60:
            if st.button("🔮 Run Forecast",use_container_width=True): st.session_state.step=4;st.rerun()
        else: st.info("Upload valid data (min 60 months) to run forecast")
    dev_footer()

# ═══════════════════════════════════════════════════════════════════════════
# STEP 4 — PROCESSING
# ═══════════════════════════════════════════════════════════════════════════
elif st.session_state.step==4:
    render_steps(4)
    st.markdown('<div style="text-align:center;padding:2rem 0"><div style="font-size:4rem;margin-bottom:1rem">🔮</div><div style="font-size:1.1rem;color:#b090ff;margin-bottom:1.5rem">The crystal ball is working...</div></div>',unsafe_allow_html=True)
    steps_ui=["Validating data","Detecting seasonality patterns","Running Prophet model",
              "Running ETS model","Combining ensemble (70/30)","Walk-forward backtest validation",
              "Computing seasonality index","Year-over-year analysis","Generating scenarios","Building reports"]
    pb=st.progress(0);sb=st.empty()
    df=st.session_state.df.copy();zone_cols=st.session_state.zones;horizon=st.session_state.horizon
    for i,sn in enumerate(steps_ui):
        sb.markdown(f'<div style="text-align:center;color:#b090ff;font-size:.85rem">⟳ {sn}...</div>',unsafe_allow_html=True)
        pb.progress((i+1)/len(steps_ui))
        if i==2: results=run_forecast(df,zone_cols,horizon)
    st.session_state.results=results
    pb.progress(1.0)
    sb.markdown('<div style="text-align:center;color:#3db07a;font-size:.9rem">✅ Forecast complete!</div>',unsafe_allow_html=True)
    import time;time.sleep(0.8)
    st.session_state.step=5;st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
# STEP 5 — RESULTS
# ═══════════════════════════════════════════════════════════════════════════
elif st.session_state.step==5:
    import plotly.graph_objects as go
    render_steps(5)
    util=st.session_state.utility;unit=UTILITIES[util]['unit']
    results=st.session_state.results;zones=st.session_state.zones
    horizon=st.session_state.horizon;df=st.session_state.df
    mapes=[results[z]['mape'] for z in zones if results[z]['mape'] is not None]
    avg_mape=round(np.mean(mapes),1) if mapes else None

    # Top metrics
    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(f'<div class="metric-box"><div class="metric-label">Utility</div><div class="metric-val" style="font-size:1rem">{util}</div></div>',unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-box"><div class="metric-label">Zones</div><div class="metric-val">{len(zones)}</div></div>',unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-box"><div class="metric-label">Horizon</div><div class="metric-val" style="font-size:1rem">{horizon} mo</div></div>',unsafe_allow_html=True)
    with c4:
        if avg_mape:
            cls="metric-good" if avg_mape>=85 else "metric-warn" if avg_mape>=70 else "metric-bad"
            st.markdown(f'<div class="metric-box"><div class="metric-label">Avg MAPE Accuracy</div><div class="metric-val {cls}">{avg_mape}%</div></div>',unsafe_allow_html=True)
        else: st.markdown(f'<div class="metric-box"><div class="metric-label">Avg MAPE</div><div class="metric-val">N/A</div></div>',unsafe_allow_html=True)

    st.markdown('---')

    # Zone insight cards
    st.markdown('<div style="font-size:.85rem;font-weight:500;color:#c0a0ff;margin-bottom:.5rem">Zone insights</div>',unsafe_allow_html=True)
    cols_ins=st.columns(len(zones))
    for i,z in enumerate(zones):
        r=results[z]
        trend=r['trend_pct']
        icon='🚀' if trend>5 else '📈' if trend>1 else '⚠️' if trend<-1 else '➡️'
        status='High growth' if trend>5 else 'Growing' if trend>1 else 'Declining' if trend<-1 else 'Stable'
        peak_month=MONTHS_SHORT[r['seasonality'].index(max(r['seasonality']))]
        low_month=MONTHS_SHORT[r['seasonality'].index(min(r['seasonality']))]
        with cols_ins[i]:
            st.markdown(f'<div class="insight-card"><div class="insight-zone">{icon} {z}</div><div class="insight-text">Status: <strong style="color:#b090ff">{status}</strong><br>Trend: {trend:+.1f}% over {horizon} mo<br>Peak month: {peak_month}<br>Low month: {low_month}<br>MAPE: {r["mape"]}%</div></div>',unsafe_allow_html=True)

    st.markdown('---')
    tab1,tab2,tab3,tab4,tab5,tab6=st.tabs(["📈 Forecast","🔍 Backtest","🌊 Seasonality","📅 Year-over-Year","🤖 AI Insights","📥 Export"])

    # ── Tab 1: Forecast ──────────────────────────────────────────────────────
    with tab1:
        zone_options=['All zones']+zones
        sel_zone=st.selectbox("Select zone",zone_options,key="zone_sel")
        def make_fc_chart(zk):
            fig=go.Figure()
            if zk=='All zones':
                hd=results[zones[0]]['dates_hist']
                hv=[sum(results[z]['vals_hist'][i] for z in zones) for i in range(len(hd))]
                fd=results[zones[0]]['dates_fc']
                bfc=[sum(results[z]['base'][i] for z in zones) for i in range(horizon)]
                ofc=[sum(results[z]['optimistic'][i] for z in zones) for i in range(horizon)]
                cfc=[sum(results[z]['conservative'][i] for z in zones) for i in range(horizon)]
                title=f"All Zones — {util} ({unit})"
            else:
                r=results[zk];hd,hv=r['dates_hist'],r['vals_hist']
                fd,bfc,ofc,cfc=r['dates_fc'],r['base'],r['optimistic'],r['conservative']
                title=f"{zk} — {util} ({unit})"
            fig.add_trace(go.Scatter(x=list(fd)+list(fd)[::-1],y=ofc+cfc[::-1],fill='toself',fillcolor='rgba(61,176,122,0.08)',line=dict(color='rgba(0,0,0,0)'),showlegend=False,hoverinfo='skip'))
            fig.add_trace(go.Scatter(x=hd,y=hv,name='Historical',line=dict(color='#8060d0',width=2),hovertemplate='%{x|%b %Y}<br>%{y:,.1f} '+unit+'<extra>Historical</extra>'))
            fig.add_trace(go.Scatter(x=fd,y=bfc,name='Base forecast',line=dict(color='#3db07a',width=2),hovertemplate='%{x|%b %Y}<br>%{y:,.1f} '+unit+'<extra>Base</extra>'))
            fig.add_trace(go.Scatter(x=fd,y=ofc,name='Optimistic',line=dict(color='#cc7040',width=1.5,dash='dash'),hovertemplate='%{x|%b %Y}<br>%{y:,.1f} '+unit+'<extra>Optimistic</extra>'))
            fig.add_trace(go.Scatter(x=fd,y=cfc,name='Conservative',line=dict(color='#6a5a8a',width=1.5,dash='dash'),hovertemplate='%{x|%b %Y}<br>%{y:,.1f} '+unit+'<extra>Conservative</extra>'))
            if fd:
                sx=str(fd[0])[:10]
                fig.add_shape(type='line',x0=sx,x1=sx,y0=0,y1=1,xref='x',yref='paper',line=dict(color='#3a2a5a',width=1,dash='dot'))
                fig.add_annotation(x=sx,y=0.97,xref='x',yref='paper',text='forecast →',showarrow=False,font=dict(color='#5a4a7a',size=10),xanchor='left')
            fig.update_layout(title=dict(text=title,font=dict(color='#c0a0ff',size=13)),
                paper_bgcolor='#12102a',plot_bgcolor='#12102a',font=dict(color='#9080b0',size=11),
                xaxis=dict(title='Month',title_font=dict(color='#7060a0',size=11),tickfont=dict(color='#7060a0',size=10),gridcolor='#1e1438',tickformat='%b %Y',dtick='M6'),
                yaxis=dict(title=f'Consumption ({unit})',title_font=dict(color='#7060a0',size=11),tickfont=dict(color='#7060a0',size=10),gridcolor='#1e1438',tickformat=',.0f'),
                legend=dict(bgcolor='#16102a',bordercolor='#2a1a4a',borderwidth=1,font=dict(color='#9080b0',size=10)),
                margin=dict(l=60,r=20,t=50,b=60),height=420,hovermode='x unified')
            return fig
        st.plotly_chart(make_fc_chart(sel_zone),use_container_width=True)
        # Total row
        if len(zones)>1:
            st.markdown('<div style="font-size:.78rem;color:#7060a0;margin-top:.5rem">📊 Total consumption across all zones</div>',unsafe_allow_html=True)
            total_base=sum(sum(results[z]['base']) for z in zones)
            total_opt=sum(sum(results[z]['optimistic']) for z in zones)
            total_con=sum(sum(results[z]['conservative']) for z in zones)
            tc1,tc2,tc3=st.columns(3)
            with tc1: st.markdown(f'<div class="metric-box"><div class="metric-label">Total Base ({unit})</div><div class="metric-val" style="font-size:1rem">{total_base:,.0f}</div></div>',unsafe_allow_html=True)
            with tc2: st.markdown(f'<div class="metric-box"><div class="metric-label">Total Optimistic ({unit})</div><div class="metric-val" style="font-size:1rem">{total_opt:,.0f}</div></div>',unsafe_allow_html=True)
            with tc3: st.markdown(f'<div class="metric-box"><div class="metric-label">Total Conservative ({unit})</div><div class="metric-val" style="font-size:1rem">{total_con:,.0f}</div></div>',unsafe_allow_html=True)

    # ── Tab 2: Backtest ──────────────────────────────────────────────────────
    with tab2:
        st.markdown('<div class="info-box">Walk-forward validation: last 10% of data held out. Model trained on 90%, predicted the holdout. Green = actual, orange = what model predicted.</div>',unsafe_allow_html=True)
        sel_bt=st.selectbox("Select zone",zones,key="bt_sel")
        r=results[sel_bt]
        fig_bt=go.Figure()
        fig_bt.add_trace(go.Scatter(x=r['dates_hist'],y=r['vals_hist'],name='Full historical',line=dict(color='#8060d0',width=2),opacity=0.4,hovertemplate='%{x|%b %Y}<br>%{y:,.1f} '+unit+'<extra>Historical</extra>'))
        fig_bt.add_trace(go.Scatter(x=r['dates_test'],y=r['vals_test'],name='Actual (holdout)',line=dict(color='#3db07a',width=2.5),mode='lines+markers',hovertemplate='%{x|%b %Y}<br>%{y:,.1f} '+unit+'<extra>Actual</extra>'))
        fig_bt.add_trace(go.Scatter(x=r['dates_test'],y=r['backtest_fc'],name='Model predicted',line=dict(color='#ff8040',width=2.5,dash='dash'),mode='lines+markers',hovertemplate='%{x|%b %Y}<br>%{y:,.1f} '+unit+'<extra>Predicted</extra>'))
        if r['dates_test']:
            sx=str(r['dates_test'][0])[:10]
            fig_bt.add_shape(type='line',x0=sx,x1=sx,y0=0,y1=1,xref='x',yref='paper',line=dict(color='#3a2a5a',width=1,dash='dot'))
            fig_bt.add_annotation(x=sx,y=0.97,xref='x',yref='paper',text='← training | test →',showarrow=False,font=dict(color='#5a4a7a',size=10),xanchor='center')
        fig_bt.update_layout(title=dict(text=f'{sel_bt} — Actual vs Predicted | MAPE Accuracy: {r["mape"]}%',font=dict(color='#c0a0ff',size=13)),
            paper_bgcolor='#12102a',plot_bgcolor='#12102a',font=dict(color='#9080b0',size=11),
            xaxis=dict(title='Month',title_font=dict(color='#7060a0',size=11),tickfont=dict(color='#7060a0',size=10),gridcolor='#1e1438',tickformat='%b %Y',dtick='M3'),
            yaxis=dict(title=f'Consumption ({unit})',title_font=dict(color='#7060a0',size=11),tickfont=dict(color='#7060a0',size=10),gridcolor='#1e1438',tickformat=',.0f'),
            legend=dict(bgcolor='#16102a',bordercolor='#2a1a4a',borderwidth=1,font=dict(color='#9080b0',size=10)),
            margin=dict(l=60,r=20,t=50,b=60),height=420,hovermode='x unified')
        st.plotly_chart(fig_bt,use_container_width=True)
        dates_t=[d.strftime('%b %Y') if hasattr(d,'strftime') else str(d) for d in r['dates_test']]
        bt_rows=[{'Month':dt,f'Actual ({unit})':act,f'Predicted ({unit})':pred,'Error (%)':f'{round(abs(act-pred)/max(act,1)*100,1)}%'} for dt,act,pred in zip(dates_t,r['vals_test'],r['backtest_fc'])]
        st.dataframe(pd.DataFrame(bt_rows),use_container_width=True,hide_index=True)

    # ── Tab 3: Seasonality ───────────────────────────────────────────────────
    with tab3:
        st.markdown('<div class="info-box">Seasonality index: 100 = average month. Above 100 = above average consumption. Below 100 = below average. Shows which months are always peak and always low.</div>',unsafe_allow_html=True)
        sel_seas=st.selectbox("Select zone",zones,key="seas_sel")
        r=results[sel_seas]
        fig_s=go.Figure()
        colors_bar=['#cc4040' if v==max(r['seasonality']) else '#3db07a' if v==min(r['seasonality']) else '#6040a0' for v in r['seasonality']]
        fig_s.add_trace(go.Bar(x=MONTHS_SHORT,y=r['seasonality'],marker_color=colors_bar,
            hovertemplate='%{x}<br>Index: %{y}<extra></extra>',name='Seasonality index'))
        fig_s.add_hline(y=100,line_dash='dot',line_color='#5a4a7a',annotation_text='Average (100)',annotation_font_color='#5a4a7a',annotation_font_size=10)
        fig_s.update_layout(title=dict(text=f'{sel_seas} — Monthly Seasonality Index',font=dict(color='#c0a0ff',size=13)),
            paper_bgcolor='#12102a',plot_bgcolor='#12102a',font=dict(color='#9080b0',size=11),
            xaxis=dict(title='Month',title_font=dict(color='#7060a0',size=11),tickfont=dict(color='#7060a0',size=10),gridcolor='#1e1438'),
            yaxis=dict(title='Seasonality Index',title_font=dict(color='#7060a0',size=11),tickfont=dict(color='#7060a0',size=10),gridcolor='#1e1438'),
            margin=dict(l=60,r=20,t=50,b=60),height=380,showlegend=False)
        st.plotly_chart(fig_s,use_container_width=True)
        peak=MONTHS_SHORT[r['seasonality'].index(max(r['seasonality']))]
        low=MONTHS_SHORT[r['seasonality'].index(min(r['seasonality']))]
        st.markdown(f'<div class="success-box">🔴 Peak month: <strong>{peak}</strong> (index: {max(r["seasonality"])}) &nbsp;|&nbsp; 🟢 Lowest month: <strong>{low}</strong> (index: {min(r["seasonality"])})</div>',unsafe_allow_html=True)

    # ── Tab 4: Year-over-Year ────────────────────────────────────────────────
    with tab4:
        st.markdown('<div class="info-box">Annual total consumption per zone — shows long term growth or decline trend year by year.</div>',unsafe_allow_html=True)
        fig_yoy=go.Figure()
        colors_zones=['#8060d0','#3db07a','#cc7040','#4090d0','#d04090']
        for i,z in enumerate(zones):
            r=results[z]
            yrs=sorted(r['yoy'].keys())
            vals=[r['yoy'][yr] for yr in yrs]
            fig_yoy.add_trace(go.Bar(name=z,x=[str(yr) for yr in yrs],y=vals,
                marker_color=colors_zones[i%len(colors_zones)],
                hovertemplate=z+'<br>%{x}<br>%{y:,.1f} '+unit+'<extra></extra>'))
        fig_yoy.update_layout(title=dict(text=f'Year-over-Year Total Consumption — {util} ({unit})',font=dict(color='#c0a0ff',size=13)),
            paper_bgcolor='#12102a',plot_bgcolor='#12102a',font=dict(color='#9080b0',size=11),
            xaxis=dict(title='Year',title_font=dict(color='#7060a0',size=11),tickfont=dict(color='#7060a0',size=10),gridcolor='#1e1438'),
            yaxis=dict(title=f'Annual Total ({unit})',title_font=dict(color='#7060a0',size=11),tickfont=dict(color='#7060a0',size=10),gridcolor='#1e1438',tickformat=',.0f'),
            legend=dict(bgcolor='#16102a',bordercolor='#2a1a4a',borderwidth=1,font=dict(color='#9080b0',size=10)),
            barmode='group',margin=dict(l=60,r=20,t=50,b=60),height=400)
        st.plotly_chart(fig_yoy,use_container_width=True)

    # ── Tab 5: AI Insights ───────────────────────────────────────────────────
    with tab5:
        if st.session_state.api_key:
            if st.button("🤖 Generate AI insights"):
                with st.spinner("Consulting the AI oracle..."):
                    ins=get_ai_insights(st.session_state.api_key,util,unit,horizon,results,zones)
                st.session_state.ai_insights=ins if ins else None
                if not ins: st.error("Could not generate insights. Check your API key.")
            if st.session_state.ai_insights:
                st.markdown(f'<div style="background:#16102a;border:1px solid #2a1a4a;border-radius:10px;padding:1.25rem 1.5rem;font-size:.85rem;color:#b090ff;line-height:1.8;white-space:pre-wrap">{st.session_state.ai_insights}</div>',unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-box">🤖 Enter your Anthropic API key in the Setup step to unlock AI-powered insights.</div>',unsafe_allow_html=True)

    # ── Tab 6: Export ─────────────────────────────────────────────────────────
    with tab6:
        c1,c2=st.columns(2)
        with c1:
            st.markdown('<div style="background:#16102a;border:1px solid #2a1a4a;border-radius:10px;padding:1.25rem;text-align:center"><div style="font-size:2rem;margin-bottom:.5rem">📊</div><div style="color:#b090ff;font-size:.9rem;margin-bottom:.3rem">Excel report</div><div style="color:#5a4a7a;font-size:.75rem">Summary + forecasts + backtest + seasonality + YoY</div></div>',unsafe_allow_html=True)
            st.markdown('<div style="height:8px"></div>',unsafe_allow_html=True)
            excel_buf=build_excel(df,results,zones,util,unit,horizon)
            st.download_button("⬇ Download Excel",data=excel_buf,file_name=f"UCB_{util.replace(' ','_')}_{horizon}mo.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)
        with c2:
            st.markdown('<div style="background:#16102a;border:1px solid #2a1a4a;border-radius:10px;padding:1.25rem;text-align:center"><div style="font-size:2rem;margin-bottom:.5rem">📄</div><div style="color:#b090ff;font-size:.9rem;margin-bottom:.3rem">PDF report</div><div style="color:#5a4a7a;font-size:.75rem">Summary + backtest + forecast tables + methodology + AI insights</div></div>',unsafe_allow_html=True)
            st.markdown('<div style="height:8px"></div>',unsafe_allow_html=True)
            pdf_buf=build_pdf(results,zones,util,unit,horizon,st.session_state.ai_insights)
            if pdf_buf:
                st.download_button("⬇ Download PDF",data=pdf_buf,file_name=f"UCB_{util.replace(' ','_')}_{horizon}mo_report.pdf",mime="application/pdf",use_container_width=True)
            else:
                st.info("PDF generation requires ReportLab — available on full deployment")

    st.markdown('---')
    if st.button("🔮 Start new forecast"):
        for k in ['df','results','zones','utility','history_months','ai_insights']:
            if k in st.session_state: del st.session_state[k]
        st.session_state.step=1;st.rerun()
    dev_footer()
