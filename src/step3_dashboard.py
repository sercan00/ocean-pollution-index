"""
OCEAN POLLUTION PROJECT — Step 3: Dashboard
Year toggle: 2026 / 2050 / 2100
"""
import pandas as pd, numpy as np, json, os

OUT_DIR  = r"C:\Users\sercan\Desktop\ocean_pollution_project\output"
master   = pd.read_csv(os.path.join(OUT_DIR, "master_ocean_pollution.csv"))

REGION_CENTRES = {
    "North Atlantic Ocean":(40,-40),"South Atlantic Ocean":(-25,-15),
    "North Pacific Ocean":(35,170),"South Pacific Ocean":(-25,-130),
    "Indian Ocean":(-15,75),"Arctic Ocean":(82,0),"Southern Ocean":(-70,0),
    "Mediterranean Sea":(37,18),"Caribbean Sea":(17,-72),"Gulf of Mexico":(24,-90),
    "North Sea":(56,3),"Baltic Sea":(58,20),"Black Sea":(43,34),
    "Red Sea":(21,38),"Persian Gulf":(26,52),"South China Sea":(12,113),
    "Bay of Bengal":(14,88),"Arabian Sea":(17,65),"Gulf of Guinea":(0,3),
    "Coral Sea":(-18,155),"Tasman Sea":(-40,163),"Bering Sea":(58,-175),
    "Hudson Bay":(60,-86),"Great Lakes":(45,-84),"Caspian Sea":(42,51),
    "Lake Victoria":(-1,33),"Lake Tanganyika":(-6,30),"Lake Baikal":(53,108),
    "Lake Superior":(47,-87),"Lake Huron":(45,-82),
}
master['lat'] = master['region'].map(lambda r: REGION_CENTRES.get(r,(0,0))[0])
master['lon'] = master['region'].map(lambda r: REGION_CENTRES.get(r,(0,0))[1])

def to_col(s):
    if pd.isna(s) or s==0: return '#2ecc71'
    elif s<10:  return '#27ae60'
    elif s<30:  return '#f1c40f'
    elif s<50:  return '#e67e22'
    elif s<70:  return '#e74c3c'
    else:       return '#8e1010'

def grade(s):
    if pd.isna(s) or s==0: return 'Minimal'
    if s>=70: return 'Critical'
    elif s>=50: return 'High'
    elif s>=30: return 'Moderate'
    elif s>=10: return 'Low'
    else: return 'Minimal'

for col in ['pollution_index','pollution_index_2050','pollution_index_2100']:
    if col not in master.columns:
        master[col] = 0

markers = []
for _, row in master.iterrows():
    def f(v, d=1): return f"{v:.{d}f}" if pd.notna(v) and v!=0 else "No data"
    s26  = float(row.pollution_index)       if pd.notna(row.pollution_index)       else 0
    s50  = float(row.pollution_index_2050)  if pd.notna(row.pollution_index_2050)  else 0
    s100 = float(row.pollution_index_2100)  if pd.notna(row.pollution_index_2100)  else 0
    markers.append({
        "region":row.region,"lat":row.lat,"lon":row.lon,
        "s26":round(s26,2),"s50":round(s50,2),"s100":round(s100,2),
        "g26":grade(s26),"g50":grade(s50),"g100":grade(s100),
        "c26":to_col(s26),"c50":to_col(s50),"c100":to_col(s100),
        "popup":f"""
          <tr><td>🔬 Microplastics</td><td>{f(row.microplastic_mean,2)}</td></tr>
          <tr><td>🏭 Port Pressure</td><td>{f(row.port_pressure_score,0)}</td></tr>
          <tr><td>🌊 River Plastic kg/yr</td><td>{f(row.river_plastic_kg_total,0)}</td></tr>
          <tr><td>👥 Coastal Pop (10km)</td><td>{f(row.coastal_pop_10km,0)}</td></tr>
          <tr><td>🧪 Ocean pH</td><td>{f(row.ph_mean,3)}</td></tr>
          <tr><td>📅 2026 Index</td><td><b>{f(row.pollution_index)}</b></td></tr>
          <tr><td>📅 2030 Forecast</td><td>{f(row.pollution_index_2030)}</td></tr>
          <tr><td>📅 2040 Forecast</td><td>{f(row.pollution_index_2040)}</td></tr>
          <tr><td>📅 2050 Forecast</td><td><b style='color:#e67e22'>{f(row.pollution_index_2050)}</b></td></tr>
          <tr><td>📅 2100 Forecast</td><td><b style='color:#e74c3c'>{f(row.pollution_index_2100)}</b></td></tr>
        """
    })

# League table
grade_c = {'Critical':'#8e1010','High':'#e74c3c','Moderate':'#e67e22','Low':'#f1c40f','Minimal':'#27ae60'}
league = master[master['pollution_index']>0].sort_values('pollution_index',ascending=False)
rows = ""
for i,(_, row) in enumerate(league.iterrows(),1):
    s26=f"{row.pollution_index:.1f}" if pd.notna(row.pollution_index) else "—"
    s50=f"{row.pollution_index_2050:.1f}" if pd.notna(row.pollution_index_2050) else "—"
    s100=f"{row.pollution_index_2100:.1f}" if pd.notna(row.pollution_index_2100) else "—"
    g26=grade(row.pollution_index); g50=grade(row.pollution_index_2050); g100=grade(row.pollution_index_2100)
    rows += f"<tr><td style='color:#aaa'>{i}</td><td>{row.region}</td><td style='color:{grade_c.get(g26,'#888')};font-weight:bold'>{s26}</td><td style='color:{grade_c.get(g50,'#888')}'>{s50}</td><td style='color:{grade_c.get(g100,'#888')}'>{s100}</td></tr>"

# Forecast chart — top 5
top5 = master[master['pollution_index']>0].nlargest(5,'pollution_index')
chart_c = ['#e74c3c','#e67e22','#f1c40f','#3498db','#9b59b6']
datasets = []
for i,(_,row) in enumerate(top5.iterrows()):
    datasets.append({"label":row.region,"data":[
        round(float(row.pollution_index),2),
        round(float(row.pollution_index_2030),2),
        round(float(row.pollution_index_2040),2),
        round(float(row.pollution_index_2050),2),
        round(float(row.pollution_index_2100),2),
    ],"borderColor":chart_c[i],"backgroundColor":chart_c[i]+"22",
    "tension":0.4,"fill":False,"pointRadius":5,"borderWidth":2})

mj = json.dumps(markers)
cj = json.dumps(datasets)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Global Ocean Pollution Index</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"/>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',sans-serif;background:#0a0e1a;color:#e0e6f0}}
header{{background:linear-gradient(135deg,#0d1b3e,#1a3a6e);padding:13px 22px;border-bottom:1px solid #1e3a6e;display:flex;align-items:center;justify-content:space-between}}
header h1{{font-size:1.25rem;color:#7ecfff;letter-spacing:1px}}
header p{{font-size:0.76rem;color:#8899bb;margin-top:2px}}
.ytoggle{{display:flex;gap:7px;align-items:center}}
.ylabel{{font-size:0.75rem;color:#5577aa;margin-right:3px}}
.ybtn{{background:transparent;border:1px solid #3a6abf;padding:5px 16px;border-radius:20px;font-size:0.82rem;color:#7ecfff;cursor:pointer;transition:all .2s}}
.ybtn.active{{background:#1e3a6e;font-weight:bold;border-color:#7ecfff}}
.ybtn:hover{{background:#1e3a6e}}
.main{{display:flex;height:calc(100vh - 60px)}}
#map{{flex:1;position:relative}}
.yind{{position:absolute;top:12px;left:12px;z-index:1000;background:#0d1b3ecc;border:1px solid #3a6abf;padding:5px 14px;border-radius:20px;font-size:0.82rem;color:#7ecfff;font-weight:bold;backdrop-filter:blur(4px)}}
.sidebar{{width:370px;background:#0d1424;border-left:1px solid #1e3a6e;overflow-y:auto;display:flex;flex-direction:column}}
.panel{{padding:13px;border-bottom:1px solid #1a2a4a}}
.ptitle{{font-size:0.67rem;text-transform:uppercase;letter-spacing:2px;color:#5577aa;margin-bottom:9px}}
.lrow{{display:flex;align-items:center;gap:7px;margin:4px 0;font-size:0.8rem}}
.ldot{{width:12px;height:12px;border-radius:50%;flex-shrink:0}}
#dp{{display:none}} #dp.on{{display:block}}
#dtitle{{font-size:.95rem;color:#7ecfff;margin-bottom:7px;font-weight:600}}
.sbadge{{display:inline-block;padding:3px 11px;border-radius:20px;font-size:.82rem;font-weight:bold;margin-bottom:9px}}
#dtable{{width:100%;border-collapse:collapse;font-size:.79rem}}
#dtable td{{padding:4px 3px;border-bottom:1px solid #1a2a4a}}
#dtable td:first-child{{color:#8899bb;width:54%}}
#lt{{width:100%;border-collapse:collapse;font-size:.74rem}}
#lt th{{padding:5px 3px;text-align:left;color:#5577aa;border-bottom:1px solid #1e3a6e;font-size:.65rem;text-transform:uppercase;letter-spacing:1px}}
#lt td{{padding:4px 3px;border-bottom:1px solid #111d30}}
#lt tr:hover td{{background:#131e35}}
#fc{{max-height:200px}}
.hint{{font-size:.71rem;color:#5577aa;margin-top:5px}}
::-webkit-scrollbar{{width:4px}}
::-webkit-scrollbar-track{{background:#0a0e1a}}
::-webkit-scrollbar-thumb{{background:#1e3a6e;border-radius:3px}}
</style>
</head>
<body>
<header>
  <div>
    <h1>🌊 Global Ocean Pollution Index</h1>
    <p>30 water bodies &nbsp;·&nbsp; 6 data sources &nbsp;·&nbsp; Forecast to 2100</p>
  </div>
  <div class="ytoggle">
    <span class="ylabel">View year:</span>
    <button class="ybtn active" id="b26"  onclick="setY(2026)">2026</button>
    <button class="ybtn"        id="b50"  onclick="setY(2050)">2050</button>
    <button class="ybtn"        id="b100" onclick="setY(2100)">2100</button>
  </div>
</header>

<div class="main">
  <div id="map">
    <div class="yind" id="yind">📅 2026 — Current</div>
  </div>
  <div class="sidebar">

    <div class="panel">
      <div class="ptitle">Pollution Index Legend</div>
      <div class="lrow"><div class="ldot" style="background:#27ae60"></div>Minimal (0–10)</div>
      <div class="lrow"><div class="ldot" style="background:#f1c40f"></div>Low (10–30)</div>
      <div class="lrow"><div class="ldot" style="background:#e67e22"></div>Moderate (30–50)</div>
      <div class="lrow"><div class="ldot" style="background:#e74c3c"></div>High (50–70)</div>
      <div class="lrow"><div class="ldot" style="background:#8e1010"></div>Critical (70+)</div>
      <p class="hint">Toggle 2026 / 2050 / 2100 above. Click a circle for details.</p>
    </div>

    <div class="panel" id="dp">
      <div class="ptitle">Region Detail</div>
      <div id="dtitle"></div>
      <div id="dscore"></div>
      <table id="dtable"><tbody id="dbody"></tbody></table>
    </div>

    <div class="panel">
      <div class="ptitle">Pollution Forecast — Top 5 Regions</div>
      <canvas id="fc"></canvas>
    </div>

    <div class="panel">
      <div class="ptitle">League Table — 2026 · 2050 · 2100</div>
      <table id="lt">
        <thead><tr><th>#</th><th>Region</th><th>2026</th><th>2050</th><th>2100</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>

  </div>
</div>

<script>
const MD = {mj};
let CY = 2026, LM = [];

const map = L.map('map',{{center:[20,10],zoom:2,minZoom:2,maxZoom:8}});
L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png',
  {{attribution:'© OpenStreetMap © CARTO',subdomains:'abcd',maxZoom:19}}).addTo(map);

function rad(s){{
  if(!s||s<=0) return 7;
  if(s<10) return 9; if(s<30) return 13;
  if(s<50) return 17; if(s<70) return 22; return 29;
}}

function build(){{
  LM.forEach(m=>map.removeLayer(m)); LM=[];
  MD.forEach(m=>{{
    const s  = CY===2026?m.s26:CY===2050?m.s50:m.s100;
    const g  = CY===2026?m.g26:CY===2050?m.g50:m.g100;
    const c  = CY===2026?m.c26:CY===2050?m.c50:m.c100;
    const cm = L.circleMarker([m.lat,m.lon],{{
      radius:rad(s),fillColor:c,color:'#fff',weight:1.5,opacity:.9,fillOpacity:.75
    }}).addTo(map);
    cm.bindTooltip(`<b>${{m.region}}</b><br>${{CY}} Index: ${{s}} — ${{g}}`,{{direction:'top'}});
    cm.on('click',()=>{{
      document.getElementById('dp').classList.add('on');
      document.getElementById('dtitle').textContent=m.region;
      document.getElementById('dscore').innerHTML=
        `<span class="sbadge" style="background:${{c}}22;color:${{c}};border:1px solid ${{c}}">`+
        `${{CY}}: ${{s}} / 100 — ${{g}}</span>`;
      document.getElementById('dbody').innerHTML=m.popup;
      document.querySelector('.sidebar').scrollTop=0;
    }});
    LM.push(cm);
  }});
}}

function setY(y){{
  CY=y;
  ['b26','b50','b100'].forEach(id=>document.getElementById(id).classList.remove('active'));
  document.getElementById(y===2026?'b26':y===2050?'b50':'b100').classList.add('active');
  document.getElementById('yind').textContent=
    y===2026?'📅 2026 — Current':y===2050?'📅 2050 — Forecast':'📅 2100 — Long-term Forecast';
  build();
}}

build();

new Chart(document.getElementById('fc').getContext('2d'),{{
  type:'line',
  data:{{labels:['2026','2030','2040','2050','2100'],datasets:{cj}}},
  options:{{
    responsive:true,
    plugins:{{legend:{{labels:{{color:'#8899bb',font:{{size:10}},boxWidth:12}}}}}},
    scales:{{
      x:{{ticks:{{color:'#5577aa'}},grid:{{color:'#1a2a4a'}}}},
      y:{{ticks:{{color:'#5577aa'}},grid:{{color:'#1a2a4a'}},
        title:{{display:true,text:'Pollution Index',color:'#5577aa',font:{{size:10}}}}}}
    }}
  }}
}});
</script>
</body>
</html>"""

out = os.path.join(OUT_DIR, "ocean_pollution_dashboard.html")
with open(out,'w',encoding='utf-8') as fh: fh.write(html)
print(f"✅ Dashboard saved: {out}")
