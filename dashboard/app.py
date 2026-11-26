"""Two-tab Airtel usage and service-quality dashboard."""
from pathlib import Path
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "raw" / "airtel.db"
st.set_page_config(page_title="Airtel | Network intelligence", page_icon="📶", layout="wide", initial_sidebar_state="collapsed")
NAVY, RED, MUTED = "#7A0019", "#D71935", "#70565A"
PAPER, WHITE, PLUM, ACCENT_RED = "#FFFFFF", "#FFFFFF", "#7A0019", "#A80E2B"
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
.stApp {{background:#FFFFFF;color:#7A0019}}
header[data-testid="stHeader"], .stAppHeader {{background:transparent !important;height:2rem !important;min-height:2rem !important;overflow:visible !important}}
div[data-testid="stToolbar"] {{display:none !important}}
div[data-testid="stAppViewContainer"] > .main {{padding-top:0 !important}}
.block-container {{padding:.5rem 1rem .45rem;max-width:1520px}}
.airtel-header {{display:flex;align-items:center;gap:16px;position:relative;overflow:hidden;background:linear-gradient(105deg,#A9001D 0%,#D71935 62%,#B50D29 100%);color:white;padding:8px 18px;border:1px solid #E4475C;border-radius:12px;margin-bottom:6px;box-shadow:0 7px 18px #7A00191A,inset 0 1px 0 #ffffff30}}
.airtel-header:after {{content:"";position:absolute;width:380px;height:140px;border-radius:50%;right:-40px;top:-100px;border:22px solid #ffffff14;pointer-events:none}}
.airtel-logo {{width:100px;height:42px;display:flex;align-items:center;position:relative;z-index:1;color:#FFFFFF;font-family:Manrope,sans-serif;font-size:27px;font-weight:800;letter-spacing:-.07em}}
.airtel-divider {{height:38px;border-left:1px solid #ffffff66;position:relative;z-index:1}}
.airtel-title {{font-family:Manrope,sans-serif;color:#fff;font-size:19px;font-weight:800;letter-spacing:-.025em;line-height:1.15;position:relative;z-index:1}}
.airtel-subtitle {{font-family:'DM Sans',sans-serif;color:#FFE7EA;font-size:10px;letter-spacing:.04em;margin-top:2px;position:relative;z-index:1}}
.chart-kind {{display:inline-flex;align-items:center;background:#FBEAED;border:1px solid #F0C5CE;color:#88001E;border-radius:999px;padding:2px 9px;font-size:9px;font-weight:700;letter-spacing:.025em;text-transform:lowercase;margin:0 0 2px}}
.metric {{background:#FFFFFF;border:1px solid #F0D9DE;border-top:3px solid #A80E2B;border-radius:13px;padding:13px 16px;min-height:83px;box-shadow:0 5px 16px #7A00190C}}
.ml {{color:#70565A;font-size:9px;text-transform:uppercase;letter-spacing:.14em;font-weight:700}}
.mv {{color:#7A0019;font-family:Manrope,sans-serif;font-size:25px;font-weight:800;margin-top:4px;letter-spacing:-.025em}}
.mn {{color:#70565A;font-size:10px}} .section {{font-family:Manrope,sans-serif;font-size:18px;font-weight:800;margin:9px 0 1px;color:#7A0019;letter-spacing:-.025em}}
.caption {{color:#70565A;font-size:11px;margin:0 0 8px;letter-spacing:.015em}} .insight {{background:#FFFFFF;border:1px solid #F0D9DE;border-left:4px solid #A80E2B;border-radius:0 10px 10px 0;padding:12px 15px;color:#641024;font-size:12px;box-shadow:0 5px 15px #7A00190B}}
div[data-testid="stPlotlyChart"] {{background:#FFFFFF;border:1px solid #E2E3E7;border-top:3px solid #D71935;border-radius:12px;padding:2px;box-shadow:0 4px 13px #27282C0D}}
div[data-testid="stPlotlyChart"]:hover {{transform:translateY(-1px);border-color:#C8102E;box-shadow:0 10px 23px #7A001916}}
div[data-testid="stTabs"] [data-baseweb="tab-list"] {{background:#FFFFFF;border:1px solid #E2E3E7;border-radius:12px;padding:4px;gap:4px}}
div[data-testid="stTabs"] button {{color:#70565A;font-size:12px;font-weight:600;padding:.5rem 1rem;transition:all .15s ease}}
div[data-testid="stTabs"] button:hover {{color:#7A0019;background:#FFFFFF;border-radius:9px}}
div[data-testid="stTabs"] button[aria-selected="true"] {{background:#C8102E;color:#fff;border:1px solid #A9001D;border-radius:9px;box-shadow:0 3px 9px #7A001922}}
div[data-testid="stTabs"] [data-baseweb="tab-list"] {{margin-bottom:0}}
div[data-testid="stVerticalBlock"] {{gap:.32rem}}
div[data-testid="stHorizontalBlock"] {{gap:.65rem}}
div[data-testid="stPopover"] button {{min-height:1.8rem;padding:.15rem .55rem;font-size:.72rem;border-color:#E4CFD3;color:#641024;background:#fff;border-radius:8px}}
div[data-testid="stPopover"] button:hover {{border-color:#A80E2B;color:#7A0019}}
label, div[data-testid="stMultiSelect"] *, div[data-testid="stSelectbox"] * {{color:#7A0019}}
div[data-baseweb="select"] > div {{background:#FFFFFF;border:1px solid #E4CFD3;border-radius:9px;min-height:40px;box-shadow:0 2px 5px #7A001908}}
div[data-baseweb="select"] > div:hover {{border-color:#A80E2B}}
div[data-baseweb="tag"] {{background:#FBEAED;color:#8A142B;border-radius:6px;font-weight:600}}
div[data-testid="stMultiSelect"] label {{font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#70565A}}
div[data-testid="stCaptionContainer"] p {{color:#70565A}}
div[data-testid="stAlert"] {{background:#FFFFFF;border-color:#A80E2B;color:#7A0019}}
.st-key-global-filter-panel {{min-height:calc(100vh - 155px);height:100%;background:linear-gradient(180deg,#87001C 0%,#A9001D 54%,#760018 100%) !important;border:1px solid #A9001D !important;border-radius:13px;padding:.85rem .7rem !important;box-shadow:0 8px 22px #7A00191F}}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.st-key-global-filter-panel) {{height:calc(100vh - 155px);min-height:calc(100vh - 155px);background:linear-gradient(180deg,#87001C 0%,#A9001D 54%,#760018 100%) !important;border:1px solid #A9001D !important;border-radius:13px;padding:.25rem;box-shadow:0 8px 22px #7A00191F}}
.st-key-global-filter-panel h3, .st-key-global-filter-panel p, .st-key-global-filter-panel label {{color:#FFFFFF !important}}
.st-key-global-filter-panel [data-testid="stCaptionContainer"] p {{color:#FFE4E9 !important}}
.st-key-global-filter-panel div[data-baseweb="select"] > div {{background:#FFFFFF;border-color:#FFFFFF}}
.st-key-global-filter-panel div[data-baseweb="select"] *, .st-key-global-filter-panel input {{color:#7A0019 !important}}
.st-key-global-filter-panel div[data-testid="stMultiSelect"] [data-baseweb="tag"] {{background:#FBEAED;color:#7A0019}}
footer {{visibility:hidden}}
</style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner="Loading project data…")
def read_data():
    if not DB.exists(): return None
    with sqlite3.connect(DB) as con:
        u=pd.read_sql_query("""SELECT u.usage_date,u.customer_id,u.data_mb,u.voice_minutes,u.is_roaming,c.connection_type,c.device_type,c.age_band,ci.region,ci.circle_name FROM usage_daily u JOIN customers c USING(customer_id) LEFT JOIN circles ci USING(circle_id)""",con)
        q=pd.read_sql_query("SELECT category,channel,is_resolved,resolution_days,customer_id FROM complaints",con)
        c=pd.read_sql_query("""SELECT c.customer_id,ci.region,ci.circle_name,c.connection_type,c.device_type,c.is_churned FROM customers c LEFT JOIN circles ci USING(circle_id)""",con)
    u["usage_date"]=pd.to_datetime(u.usage_date); u["month"]=u.usage_date.dt.strftime("%b"); u["weekday"]=u.usage_date.dt.day_name()
    return u,q,c

def metric(label,value,note):
    st.markdown(f'<div class="metric"><div class="ml">{label}</div><div class="mv">{value}</div><div class="mn">{note}</div></div>',unsafe_allow_html=True)

def chart(fig,height=205):
    fig.update_layout(height=height,margin=dict(l=12,r=12,t=38,b=10),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(family="DM Sans, Arial",color="#7A0019",size=9),title=dict(font=dict(family="Manrope, Arial",size=12,color="#7A0019"),x=.035,y=.96),legend=dict(orientation="h",y=1.02,x=0,font=dict(size=8,color="#641024")),colorway=[RED,ACCENT_RED,"#8C001A","#E45A6E","#F3A0AC"],hoverlabel=dict(bgcolor="#7A0019",bordercolor="#A80E2B",font=dict(color="#FFFFFF",family="DM Sans")))
    fig.update_xaxes(showgrid=False,linecolor="#E4CFD3",tickfont=dict(color="#70565A",size=9),title_font=dict(color="#641024",size=10),automargin=True); fig.update_yaxes(gridcolor="#F4E7EA",zeroline=False,tickfont=dict(color="#70565A",size=9),title_font=dict(color="#641024",size=10),automargin=True)
    return fig

def filters(df,fields,prefix):
    cols=st.columns(len(fields)); out=df
    for col,field in zip(cols,fields):
        with col: selected=st.multiselect(field.replace("_"," ").title(),sorted(out[field].dropna().unique()),key=prefix+field,placeholder="All")
        if selected: out=out[out[field].isin(selected)]
    return out

def chart_filters(df, fields, prefix, chart_kind):
    """Independent chart filters tucked into a compact popover."""
    result=df
    if not fields:
        return result
    heading,filter_button=st.columns([1,.42])
    with heading:
        st.markdown(f'<span class="chart-kind">{chart_kind}</span>',unsafe_allow_html=True)
    with filter_button:
        with st.popover("Filters",use_container_width=True):
            cols=st.columns(len(fields))
            for col,field in zip(cols,fields):
                with col:
                    selected=st.multiselect(
                        field.replace("_"," ").title(),
                        sorted(df[field].dropna().unique()),
                        key=f"{prefix}_{field}",
                        placeholder="All",
                    )
                if selected:
                    result=result[result[field].isin(selected)]
    return result

data=read_data()
if data is None: st.error("Place airtel.db in data/raw/ and reopen this dashboard."); st.stop()
usage,complaints,customers=data
st.markdown('<div class="airtel-header"><div class="airtel-logo" aria-label="Airtel">airtel</div><div class="airtel-divider"></div><div><div class="airtel-title">Airtel Telecom Analytics</div><div class="airtel-subtitle">Network Usage &amp; Customer Experience</div></div></div>',unsafe_allow_html=True)
filter_panel,dashboard_panel=st.columns([.23,.77],gap="small")
with filter_panel.container(border=True,key="global-filter-panel"):
    st.markdown("### Global filters")
    st.caption("Applied across both tabs")
    global_region=st.multiselect("Region",sorted(usage.region.dropna().unique()),key="global_region",placeholder="All regions")
    global_connection=st.multiselect("Connection type",sorted(usage.connection_type.dropna().unique()),key="global_connection",placeholder="All connection types")
    global_device=st.multiselect("Device type",sorted(usage.device_type.dropna().unique()),key="global_device",placeholder="All devices")

global_usage=usage.copy()
global_customers=customers.copy()
for field,selected in [("region",global_region),("connection_type",global_connection),("device_type",global_device)]:
    if selected:
        global_usage=global_usage[global_usage[field].isin(selected)]
        global_customers=global_customers[global_customers[field].isin(selected)]
global_customer_ids=set(global_customers.customer_id)
global_complaints=complaints[complaints.customer_id.isin(global_customer_ids)]

with dashboard_panel:
    tab1,tab2=st.tabs(["01  ·  Usage & demand","02  ·  Service quality"])
    with tab1:
        row1=st.columns([1.25,1])
        with row1[0]:
            um=chart_filters(global_usage,["region","connection_type"],"usage_month","bar + line chart")
            monthly=um.groupby("month",as_index=False).agg(data_tb=("data_mb",lambda s:s.sum()/1e6),active=("customer_id","nunique"))
            monthly["month"]=pd.Categorical(monthly.month,categories=["Jan","Feb","Mar","Apr","May","Jun"],ordered=True); monthly=monthly.sort_values("month")
            f=go.Figure(); f.add_trace(go.Bar(x=monthly.month.astype(str),y=monthly.data_tb,name="Data (TB)",marker_color=RED)); f.add_trace(go.Scatter(x=monthly.month.astype(str),y=monthly.active,name="Active subscribers",yaxis="y2",mode="lines+markers",line=dict(color=ACCENT_RED,width=3)))
            f.update_layout(title="Monthly data traffic and active subscribers",yaxis_title="Data (TB)",yaxis2=dict(title="Subscribers",overlaying="y",side="right",showgrid=False,color="#70565A"))
            st.plotly_chart(chart(f,205),use_container_width=True,config={"displayModeBar":False})
        with row1[1]:
            ud=chart_filters(global_usage,["region","device_type"],"usage_weekday","polar line chart")
            day=ud.groupby("weekday",as_index=False).agg(gb=("data_mb",lambda x:x.mean()/1024)); order=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]; day["weekday"]=pd.Categorical(day.weekday,categories=order,ordered=True); day=day.sort_values("weekday")
            f=px.line_polar(day,r="gb",theta="weekday",line_close=True,markers=True,color_discrete_sequence=[RED],title="Weekly data-use rhythm · avg GB per record"); f.update_traces(fill="toself",fillcolor="rgba(227,30,54,.12)")
            st.plotly_chart(chart(f,245),use_container_width=True,config={"displayModeBar":False})
        row2=st.columns([1,1.35])
        with row2[0]:
            uv=chart_filters(global_usage,["region","device_type"],"usage_violin","violin plot")
            sample=uv.sample(min(12000,len(uv)),random_state=7) if len(uv) else uv
            f=px.violin(sample,x="connection_type",y="data_mb",color="connection_type",box=True,points=False,color_discrete_sequence=[RED,"#F3A0AC"],title="Daily data-use spread by connection type")
            f.update_yaxes(title="Data per usage record (MB)",range=[0,uv.data_mb.quantile(.985) if len(uv) else 1]); f.update_xaxes(title="Connection type")
            st.plotly_chart(chart(f,205),use_container_width=True,config={"displayModeBar":False})
        with row2[1]:
            ut=chart_filters(global_usage,["connection_type","device_type"],"usage_treemap","treemap")
            mix=ut.groupby(["region","connection_type"],as_index=False).agg(traffic_tb=("data_mb",lambda x:x.sum()/1e6))
            f=px.treemap(mix,path=["region","connection_type"],values="traffic_tb",color="traffic_tb",color_continuous_scale=[[0,"#FBEAED"],[.45,"#E45A6E"],[1,"#7A0019"]],title="Traffic contribution by region and connection")
            f.update_traces(texttemplate="%{label}<br>%{value:.2f} TB · %{percentParent:.0%} of region")
            st.plotly_chart(chart(f,205),use_container_width=True,config={"displayModeBar":False})

    with tab2:
        qc=global_complaints.merge(global_customers[["customer_id","region","connection_type","device_type"]],on="customer_id",how="left")
        row1=st.columns([1.05,1])
        with row1[0]:
            qh=chart_filters(qc,["region","connection_type"],"service_heat","heatmap")
            h=qh.copy(); h["status"]="Resolved"; h.loc[h.is_resolved.eq(0),"status"]="Unresolved"; hm=h.pivot_table(index="category",columns="status",values="customer_id",aggfunc="count",fill_value=0)
            f=px.imshow(hm,aspect="auto",color_continuous_scale=[[0,"#FBEAED"],[.5,"#E8898F"],[1,"#7A0019"]],text_auto=",",title="Ticket resolution matrix by complaint category")
            f.update_layout(coloraxis_colorbar_title="Tickets"); st.plotly_chart(chart(f,205),use_container_width=True,config={"displayModeBar":False})
        with row1[1]:
            qe=chart_filters(qc,["region","device_type"],"service_ecdf","ecdf")
            r=qe[qe.is_resolved.eq(1)].dropna(subset=["resolution_days"])
            f=px.ecdf(r,x="resolution_days",color="category",color_discrete_sequence=[RED,ACCENT_RED,"#8C001A","#E45A6E","#F3A0AC","#5A0012"],title="Resolution-time accumulation by category")
            f.update_xaxes(title="Days to resolve",range=[0,min(30,float(r.resolution_days.quantile(.99)) if len(r) else 30)]); f.update_yaxes(title="Share resolved by day",tickformat=".0%")
            st.plotly_chart(chart(f,205),use_container_width=True,config={"displayModeBar":False})
        qs=chart_filters(qc,["connection_type","device_type"],"service_scatter","bubble scatter")
        svc=qs.groupby(["region","category"],as_index=False).agg(tickets=("customer_id","size"),avg_days=("resolution_days","mean"))
        f=px.scatter(svc,x="tickets",y="avg_days",size="tickets",color="category",facet_col="region",facet_col_wrap=4,color_discrete_sequence=[RED,ACCENT_RED,"#8C001A","#E45A6E","#F3A0AC","#5A0012"],hover_name="category",title="Ticket volume vs average resolution time · by region")
        f.update_layout(height=210); f.update_xaxes(title="Tickets",matches=None); f.update_yaxes(title="Avg resolution (days)")
        st.plotly_chart(chart(f,210),use_container_width=True,config={"displayModeBar":False})
