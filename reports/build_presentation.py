"""Create the editable Airtel analytics viva presentation."""
from pathlib import Path
import sqlite3
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "Airtel_Telecom_Analytics_Presentation.pptx"
DB = ROOT / "data" / "raw" / "airtel.db"

PAPER = "F7F5F2"; WHITE = "FFFFFF"; PLUM = "2B173F"; RED = "E31E36"
GOLD = "C6A15B"; MUTED = "746D77"; PALE = "EEE9ED"; BLUSH = "F3EBDD"
INK2 = "514754"; SOFT_RED = "E8898F"; GREEN = "84958B"

def rgb(h): return RGBColor.from_string(h)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]

def rect(slide,x,y,w,h,fill, radius=False, line=None):
    shape=slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid(); shape.fill.fore_color.rgb=rgb(fill)
    shape.line.fill.background() if not line else None
    if line:
        shape.line.color.rgb=rgb(line); shape.line.width=Pt(0.8)
    if radius:
        try: shape.adjustments[0]=0.12
        except Exception: pass
    return shape

def text(slide,x,y,w,h,value,size=16,color=PLUM,bold=False,font="Aptos",align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.MIDDLE,margin=0):
    box=slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf=box.text_frame; tf.clear(); tf.word_wrap=True
    tf.margin_left=tf.margin_right=Inches(margin); tf.margin_top=tf.margin_bottom=Inches(margin); tf.vertical_anchor=valign
    p=tf.paragraphs[0]; p.alignment=align; p.space_after=Pt(0)
    r=p.add_run(); r.text=str(value); r.font.name=font; r.font.size=Pt(size); r.font.bold=bold; r.font.color.rgb=rgb(color)
    return box

def line(slide,x1,y1,x2,y2,color=PALE,width=1.0):
    sh=slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    sh.line.color.rgb=rgb(color); sh.line.width=Pt(width); return sh

def base(section,title,subtitle=None,dark=False):
    s=prs.slides.add_slide(blank)
    bg=PLUM if dark else PAPER
    s.background.fill.solid(); s.background.fill.fore_color.rgb=rgb(bg)
    accent=GOLD if dark else RED
    rect(s,0.55,0.43,0.12,0.42,accent,True)
    text(s,0.82,0.40,5.5,0.24,section.upper(),9,GOLD if dark else MUTED,True)
    text(s,0.82,0.68,11.6,0.48,title,24,WHITE if dark else PLUM,True,"Aptos Display")
    if subtitle: text(s,0.84,1.18,11.5,0.30,subtitle,10,"D9D0DC" if dark else MUTED)
    line(s,0.82,7.08,12.52,7.08,"5E4A65" if dark else "E4DEE3",0.7)
    text(s,0.82,7.13,8.0,0.18,"AIRTEL  /  NETWORK USAGE & RETENTION",8,"C8BBCD" if dark else MUTED,True)
    text(s,11.9,7.11,0.6,0.20,f"{len(prs.slides):02d}",8,"C8BBCD" if dark else MUTED,True,align=PP_ALIGN.RIGHT)
    return s

def pill(slide,x,y,w,label,fill=BLUSH,color=PLUM):
    rect(slide,x,y,w,.34,fill,True)
    text(slide,x+.06,y+.01,w-.12,.30,label,9,color,True,align=PP_ALIGN.CENTER)

def card(slide,x,y,w,h,label,value,note=None,accent=GOLD):
    rect(slide,x,y,w,h,WHITE,True,"E8E2E7"); rect(slide,x,y,.055,h,accent,True)
    text(slide,x+.22,y+.17,w-.4,.24,label.upper(),9,MUTED,True)
    text(slide,x+.22,y+.49,w-.4,.49,value,25,PLUM,True,"Aptos Display")
    if note: text(slide,x+.22,y+h-.35,w-.4,.20,note,9,MUTED)

def bullet_list(slide,x,y,w,items,size=15,color=INK2,spacing=.54,accent=RED):
    for i,item in enumerate(items):
        yy=y+i*spacing
        rect(slide,x,yy+.105,.09,.09,accent,True)
        text(slide,x+.24,yy,w-.24,spacing-.04,item,size,color,False,valign=MSO_ANCHOR.TOP)

# Database-derived facts.
with sqlite3.connect(DB) as con:
    total, churned = con.execute("select count(*),sum(is_churned) from customers").fetchone()
    tickets = con.execute("select count(*) from complaints").fetchone()[0]
    months = con.execute("select strftime('%m',usage_date),sum(data_mb)/1000000.0 from usage_daily group by 1 order by 1").fetchall()
    cat = con.execute("select category,count(*),sum(case when is_resolved=0 then 1 else 0 end) from complaints group by category order by count(*) desc").fetchall()
churn_rate=churned/total*100

# 1 — cover
s=prs.slides.add_slide(blank); s.background.fill.solid(); s.background.fill.fore_color.rgb=rgb(PLUM)
rect(s,8.72,0,4.62,7.5,"4B2A58")
rect(s,9.15,.55,3.6,6.4,"5E354F",True)
rect(s,9.48,.9,2.94,5.55,"31233B",True)
# decorative signal rings
for idx,col in enumerate(["725761","A97869",GOLD]):
    sh=s.shapes.add_shape(MSO_SHAPE.OVAL,Inches(10.0+idx*.18), Inches(1.56+idx*.18), Inches(1.65-idx*.36), Inches(1.65-idx*.36))
    sh.fill.background(); sh.line.color.rgb=rgb(col); sh.line.width=Pt(2.2)
text(s,10.22,2.12,1.2,.42,"A",35,WHITE,True,"Aptos Display",PP_ALIGN.CENTER)
text(s,9.75,3.72,2.38,.3,"NETWORK SIGNALS",9,"E7D9E5",True,align=PP_ALIGN.CENTER)
text(s,9.75,4.1,2.38,.9,"Use patterns\nthat matter",18,WHITE,True,"Aptos Display",PP_ALIGN.CENTER)
text(s,.82,.7,5.5,.28,"AIRTeL  ·  TELECOM ANALYTICS",10,GOLD,True)
text(s,.82,1.5,7.6,1.25,"From network activity\nto better decisions",31,WHITE,True,"Aptos Display")
text(s,.86,3.1,6.9,.65,"A subscriber-level study of usage, recharge behaviour, complaints, and churn.",16,"E5DCE5")
line(s,.86,4.15,7.6,4.15,"735B6E",1)
pill(s,.86,4.45,1.7,"JAN — JUN 2025",fill="493345",color="F2EAEF")
pill(s,2.73,4.45,1.78,"22,000 CUSTOMERS",fill="493345",color="F2EAEF")
text(s,.86,6.82,6.8,.25,"CLASS PRESENTATION  /  NETWORK USAGE & RETENTION",9,"C8BBCD",True)

# 2 — question and scope
s=base("01 · The question","Which signals should Airtel investigate to reduce churn?","A practical analytics question, framed around patterns the project data can support.")
rect(s,.82,1.78,7.15,4.7,PLUM,True)
text(s,1.18,2.18,6.3,.25,"BUSINESS QUESTION",10,GOLD,True)
text(s,1.18,2.62,6.15,1.35,"We are losing nearly one subscriber in four. Which observable signals can help prioritize retention work?",23,WHITE,True,"Aptos Display",valign=MSO_ANCHOR.TOP)
line(s,1.18,4.4,7.45,4.4,"66516D",1)
text(s,1.18,4.68,2.8,.25,"WHAT WE CAN DO",10,"DCCFE0",True)
text(s,1.18,5.08,5.9,.78,"Find where usage, recharges, customer segments, and service complaints move with churn.",15,"F7F3F7",False,valign=MSO_ANCHOR.TOP)
card(s,8.38,1.86,3.95,1.25,"Customer base",f"{total:,}","One row per subscriber",RED)
card(s,8.38,3.34,3.95,1.25,"Churned",f"{churned:,}  ·  {churn_rate:.2f}%","Observed customer status",GOLD)
card(s,8.38,4.82,3.95,1.25,"Service tickets",f"{tickets:,}","Tickets are a separate grain",RED)

# 3 — dataset and model
s=base("02 · Data foundations","Six linked tables; several different grains","The customer table anchors subscriber-level analysis. Event tables record repeated activity.")
tables=[("CIRCLES","circle_id · region",.8,2.0), ("CUSTOMERS","customer_id · segment · churn",4.4,2.0),("PLANS","plan_id · quota · price",9.2,2.0),
        ("USAGE_DAILY","usage_id · customer_id · date",1.0,4.5),("RECHARGES","recharge_id · customer_id · plan_id",5.05,4.5),("COMPLAINTS","complaint_id · customer_id · status",9.1,4.5)]
for name,detail,x,y in tables:
    w=3.2 if name!="CUSTOMERS" else 4.0
    rect(s,x,y,w,1.15,WHITE,True,"E6DFE5"); rect(s,x,y,.07,1.15,RED if name=="CUSTOMERS" else GOLD,True)
    text(s,x+.2,y+.2,w-.35,.25,name,12,PLUM,True)
    text(s,x+.2,y+.59,w-.35,.34,detail,10,MUTED)
# relationship lines with labels
line(s,3.95,2.58,4.4,2.58,GOLD,1.5); text(s,3.98,2.27,.4,.18,"1:N",8,MUTED,True,align=PP_ALIGN.CENTER)
line(s,8.4,2.58,9.2,2.58,GOLD,1.5); text(s,8.62,2.27,.4,.18,"N:1",8,MUTED,True,align=PP_ALIGN.CENTER)
line(s,5.9,3.15,2.6,4.5,RED,1.2); line(s,6.3,3.15,6.6,4.5,RED,1.2); line(s,6.7,3.15,10.6,4.5,RED,1.2)
text(s,.92,6.1,11.5,.45,"Grain check: customers = subscriber · usage_daily = subscriber-day · recharges = transaction · complaints = ticket",13,PLUM,True)
text(s,.92,6.58,11.3,.27,"Before a join, ask whether a one-to-many relationship will duplicate customer rows.",10,MUTED)

# 4 — usage behaviour
s=base("03 · Network usage","Demand rose toward the end of the observed window","Daily activity records span 1 January to 30 June 2025; volume is not the same as unique subscribers.")
card(s,.82,1.75,3.55,1.2,"Usage records","1.33M","Daily subscriber observations",RED)
card(s,4.61,1.75,3.55,1.2,"Observation window","6 months","Jan–Jun 2025",GOLD)
card(s,8.4,1.75,3.93,1.2,"May / June daily mean","1,768 / 1,790 MB","Per usage record",RED)
rect(s,.82,3.25,7.25,3.25,WHITE,True,"E8E2E7")
text(s,1.12,3.47,6.5,.28,"MONTHLY AVERAGE DATA PER USAGE RECORD  /  MB",10,MUTED,True)
vals=[1460.8,1476.9,1485.6,1497.0,1767.9,1790.0]; labs=["JAN","FEB","MAR","APR","MAY","JUN"]
maxv=1900
for i,(lab,v) in enumerate(zip(labs,vals)):
    x=1.22+i*1.04; bh=1.72*v/maxv
    rect(s,x,5.75-bh,.63,bh,RED if i>=4 else ("C6A15B" if i==3 else "B8A7B5"),True)
    text(s,x-.12,5.82,.87,.23,lab,8,MUTED,True,align=PP_ALIGN.CENTER)
    text(s,x-.2,5.42-bh,.99,.22,f"{v:,.0f}",8,PLUM,True,align=PP_ALIGN.CENTER)
line(s,1.12,5.76,7.75,5.76,"DCD5DB",.8)
rect(s,8.38,3.25,3.95,3.25,BLUSH,True)
text(s,8.7,3.55,3.28,.32,"A question to investigate",15,PLUM,True,"Aptos Display")
text(s,8.7,4.1,3.1,1.45,"The May/June increase is a pattern in the data. These records alone do not explain why it happened.",14,INK2,valign=MSO_ANCHOR.TOP)
pill(s,8.7,5.72,2.7,"DESCRIPTIVE · NOT CAUSAL",fill="FFFFFF",color=PLUM)

# 5 — churn evidence
s=base("04 · Retention signals","Higher recharge spend aligns with lower observed churn","Associations help prioritize investigation. They do not prove that spend changes cause churn.")
card(s,.82,1.76,3.55,1.25,"Overall churn","23.75%","5,226 of 22,000 subscribers",RED)
card(s,4.61,1.76,3.55,1.25,"Never complained","20.03%","6,631 subscribers",GOLD)
card(s,8.4,1.76,3.93,1.25,"At least one complaint","25.36%","15,369 subscribers",RED)
rect(s,.82,3.3,7.1,3.1,WHITE,True,"E8E2E7")
text(s,1.12,3.55,6.45,.25,"CHURN RATE BY RECHARGE-SPEND QUARTILE",10,MUTED,True)
quart=[34.85,24.53,20.65,14.98]; qlabs=["LOWEST","Q2","Q3","HIGHEST"]
for i,(v,lab) in enumerate(zip(quart,qlabs)):
    x=1.35+i*1.52; h=1.76*v/38
    rect(s,x,5.86-h,.83,h,[RED,"C97979","C6A15B",GREEN][i],True)
    text(s,x-.14,5.96,1.1,.23,lab,8,MUTED,True,align=PP_ALIGN.CENTER)
    text(s,x-.14,5.59-h,1.1,.23,f"{v:.2f}%",10,PLUM,True,align=PP_ALIGN.CENTER)
line(s,1.12,5.87,7.48,5.87,"DCD5DB",.8)
rect(s,8.22,3.3,4.1,3.1,PLUM,True)
text(s,8.57,3.62,3.38,.32,"How to read this",15,WHITE,True,"Aptos Display")
bullet_list(s,8.57,4.2,3.3,["Spend quartiles contain equal-sized customer groups.","Complaint comparison uses subscribers, not ticket rows.","Observed differences may reflect other factors."],11,"F4EDF4",.59,GOLD)

# 6 — dashboard tour
s=base("05 · Dashboard","Two tabs turn the analysis into an exploration tool","Each chart has its own filters. Segment choices are independent from chart to chart.")
for x,title,sub,accent in [(0.82,"01 · Usage & demand","Explore traffic patterns",RED),(6.83,"02 · Service quality","Explore complaint experience",GOLD)]:
    rect(s,x,1.8,5.55,4.65,WHITE,True,"E8E2E7"); rect(s,x,1.8,5.55,.12,accent,True)
    text(s,x+.3,2.13,4.9,.3,title,18,PLUM,True,"Aptos Display")
    text(s,x+.3,2.52,4.8,.25,sub,11,MUTED)
if True:
    x=.82
    # Four small preview cards
    cards=[("MONTHLY TRAFFIC","combo trend"),("WEEKDAY RHYTHM","polar line"),("USAGE SPREAD","violin"),("REGIONAL MIX","treemap")]
    for i,(a,b) in enumerate(cards):
        cx=x+.3+(i%2)*2.5; cy=3.0+(i//2)*1.42
        rect(s,cx,cy,2.28,1.12,"F8F6F5",True,"E8E2E7"); text(s,cx+.12,cy+.14,2.05,.22,a,8,MUTED,True); text(s,cx+.12,cy+.46,2.05,.32,b,14,PLUM,True)
        line(s,cx+.14,cy+.91,cx+2.08,cy+.91,accent if False else RED,.8)
    x=6.83
    cards=[("RESOLUTION MATRIX","heatmap"),("CLOSURE TIMING","ECDF"),("REGIONAL SERVICE","bubble scatter")]
    for i,(a,b) in enumerate(cards):
        cx=x+.3+(i%2)*2.5; cy=3.0+(i//2)*1.42
        rect(s,cx,cy,2.28,1.12,"F8F6F5",True,"E8E2E7"); text(s,cx+.12,cy+.14,2.05,.22,a,8,MUTED,True); text(s,cx+.12,cy+.46,2.05,.32,b,14,PLUM,True)
        line(s,cx+.14,cy+.91,cx+2.08,cy+.91,GOLD,.8)
text(s,1.13,6.03,5.0,.24,"Filters: region · connection type · device",10,MUTED,True)
text(s,7.13,6.03,5.0,.24,"Filters: region · connection type · device",10,MUTED,True)

# 7 — method and guardrails
s=base("06 · Method & interpretation","Good analysis starts with the right unit","Keep the comparison aligned to how the data was collected and what the measure represents.")
steps=[("01","Prepare","Join dimensions; aggregate repeated events to customer grain for subscriber comparisons."),("02","Compare","Describe differences by segment, usage intensity, recharge spend, and complaint experience."),("03","Validate","Use customer-level tests where subscribers are the independent units; report context with p-values."),("04","Recommend","Treat observational patterns as hypotheses for retention tests and operational follow-up.")]
for i,(n,title,body) in enumerate(steps):
    y=1.88+i*1.09
    rect(s,.9,y,.58,.58,PLUM if i!=3 else RED,True)
    text(s,.9,y,.58,.58,n,13,WHITE,True,align=PP_ALIGN.CENTER)
    text(s,1.72,y-.02,2.0,.30,title,15,PLUM,True,"Aptos Display")
    text(s,3.7,y-.02,8.3,.57,body,12,INK2,valign=MSO_ANCHOR.TOP)
    if i<3: line(s,1.19,y+.58,1.19,y+1.0,"D5CBD5",1.2)
rect(s,.9,6.3,11.4,.47,BLUSH,True)
text(s,1.12,6.37,11.0,.31,"A small p-value is not effect size, business value, or proof that a hypothesis is true.",11,PLUM,True)

# 8 — close
s=prs.slides.add_slide(blank); s.background.fill.solid(); s.background.fill.fore_color.rgb=rgb(PLUM)
rect(s,9.6,0,3.74,7.5,"432544")
text(s,.95,.62,5.0,.25,"07 · NEXT STEP",10,GOLD,True)
text(s,.95,1.25,7.7,1.1,"Turn signals into\nmeasurable action.",32,WHITE,True,"Aptos Display")
text(s,.98,3.02,7.0,.76,"Use the strongest associations to define targeted retention experiments, then measure customer-level outcomes.",17,"E5DCE5",valign=MSO_ANCHOR.TOP)
line(s,.98,4.3,7.65,4.3,"735B6E",1)
text(s,.98,4.68,6.7,.28,"DISCUSSION",10,GOLD,True)
text(s,.98,5.15,6.6,.55,"Which segment would you investigate first—and what would you test?",19,WHITE,True,"Aptos Display")
for i,(label,val) in enumerate([("USAGE","demand patterns"),("EXPERIENCE","service friction"),("RETENTION","test & learn")]):
    y=1.25+i*1.47
    rect(s,10.0,y,2.72,1.05,"F7F5F2",True)
    text(s,10.23,y+.15,2.2,.2,label,9,MUTED,True)
    text(s,10.23,y+.43,2.2,.34,val,14,PLUM,True,"Aptos Display")
text(s,.98,6.82,6.8,.25,"AIRTEL  /  NETWORK USAGE & RETENTION",9,"C8BBCD",True)

prs.core_properties.title="Airtel Telecom Analytics | Network Usage & Retention"
prs.core_properties.subject="Subscriber usage, complaints, churn, and dashboard findings"
prs.core_properties.author="Airtel Telecom Analytics Project Team"
prs.core_properties.keywords="Airtel, telecom, analytics, churn, network usage"
prs.save(OUT)
print(OUT)
