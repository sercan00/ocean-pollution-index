"""
OCEAN POLLUTION PROJECT — Step 3: Dashboard
Year toggle: 2026 / 2050 / 2100
Policy scenario slider: 0% / 25% / 50% / 75% / 100% pollution reduction
The slider reduces each region's growth rate live in the browser, so the map,
league table, and chart all update to show "what if we act" scenarios.
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

# Ensure we have a growth rate column (from step2c). Fallback to deriving it.
if 'blended_growth_rate' not in master.columns:
    # derive from 2026 -> 2100 (74 years)
    def derive(row):
        base = row['pollution_index']; future = row.get('pollution_index_2100', base)
        if base and base > 0 and future and future > 0:
            return (future/base)**(1/74) - 1
        return 0.03
    master['blended_growth_rate'] = master.apply(derive, axis=1)

def grade(s):
    if pd.isna(s) or s==0: return 'Minimal'
    if s>=70: return 'Critical'
    elif s>=50: return 'High'
    elif s>=30: return 'Moderate'
    elif s>=10: return 'Low'
    else: return 'Minimal'

# markers carry base index (2026) + growth rate; JS computes the rest live
markers = []
for _, row in master.iterrows():
    def f(v, d=1): return f"{v:.{d}f}" if pd.notna(v) and v!=0 else "No data"
    base = float(row.pollution_index) if pd.notna(row.pollution_index) else 0
    gr   = float(row.blended_growth_rate) if pd.notna(row.blended_growth_rate) else 0.03
    markers.append({
        "region":row.region,"lat":row.lat,"lon":row.lon,
        "base":round(base,2),"growth":round(gr,5),
        "mp":f(row.get('microplastic_mean'),2),
        "port":f(row.get('port_pressure_score'),0),
        "river":f(row.get('river_plastic_kg_total'),0),
        "pop":f(row.get('coastal_pop_10km'),0),
        "ph":f(row.get('ph_mean'),3),
    })

mj = json.dumps(markers)

# Top 5 for chart (by base index)
top5 = master[master['pollution_index']>0].nlargest(5,'pollution_index')
chart_c = ['#e74c3c','#e67e22','#f1c40f','#3498db','#9b59b6']
chart_meta = []
for i,(_,row) in enumerate(top5.iterrows()):
    chart_meta.append({
        "label":row.region,
        "base":round(float(row.pollution_index),2),
        "growth":round(float(row.blended_growth_rate),5),
        "color":chart_c[i],
    })
cmj = json.dumps(chart_meta)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Global Ocean Pollution Index</title>
<link rel="icon" type="image/png" href="favicon.png">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"/>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',sans-serif;background:#0a0e1a;color:#e0e6f0}}
header{{background:linear-gradient(135deg,#0d1b3e,#1a3a6e);padding:13px 22px;border-bottom:1px solid #1e3a6e;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px}}
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
/* Policy scenario slider */
.scenario-box{{background:#0d1b3e;border-bottom:1px solid #1e3a6e;padding:12px 22px}}
.scenario-top{{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}}
.scenario-title{{font-size:0.78rem;color:#7ecfff;font-weight:bold;letter-spacing:0.5px}}
.scenario-val{{font-size:0.8rem;color:#7ecfff;font-weight:bold}}
.scenario-slider{{width:100%;-webkit-appearance:none;height:6px;border-radius:3px;background:linear-gradient(90deg,#8e1010,#e74c3c,#5577aa,#27ae60,#1a7a3a);outline:none}}
.scenario-slider::-webkit-slider-thumb{{-webkit-appearance:none;width:18px;height:18px;border-radius:50%;background:#fff;border:2px solid #3a9bd5;cursor:pointer}}
.scenario-slider::-moz-range-thumb{{width:18px;height:18px;border-radius:50%;background:#fff;border:2px solid #3a9bd5;cursor:pointer}}
.scenario-labels{{display:flex;justify-content:space-between;font-size:0.62rem;color:#5577aa;margin-top:5px}}
.scenario-desc{{font-size:0.7rem;color:#8899bb;margin-top:6px;text-align:center;font-style:italic}}
::-webkit-scrollbar{{width:4px}}
::-webkit-scrollbar-track{{background:#0a0e1a}}
::-webkit-scrollbar-thumb{{background:#1e3a6e;border-radius:3px}}
@media (max-width:768px){{
  .main{{flex-direction:column;height:auto;}}
  #map{{height:55vh;min-height:380px;width:100%;flex:none;}}
  .sidebar{{width:100%;border-left:none;border-top:1px solid #1e3a6e;}}
  header{{flex-direction:column;gap:8px;align-items:flex-start;padding:12px 16px;}}
}}
</style>
</head>
<body>
<header>
  <div>
    <h1>🌊 Global Ocean Pollution Index</h1>
    <p>30 water bodies &nbsp;·&nbsp; 9 data sources &nbsp;·&nbsp; Forecast to 2100</p>
  </div>
  <div class="ytoggle">
    <span class="ylabel">View year:</span>
    <button class="ybtn active" id="b26"  onclick="setY(2026)">2026</button>
    <button class="ybtn"        id="b50"  onclick="setY(2050)">2050</button>
    <button class="ybtn"        id="b100" onclick="setY(2100)">2100</button>
  </div>
</header>

<div class="scenario-box">
  <div class="scenario-top">
    <span class="scenario-title">🌍 Policy Scenario</span>
    <span class="scenario-val" id="scenVal">Current trajectory</span>
  </div>
  <input type="range" min="-100" max="100" step="50" value="0" class="scenario-slider" id="scenSlider" oninput="setScenario(this.value)">
  <div class="scenario-labels">
    <span>⬅ Worse</span><span>-50%</span><span>Now</span><span>+50%</span><span>Better ➡</span>
  </div>
  <div class="scenario-desc" id="scenDesc">Showing the current trajectory — what happens if nothing changes.</div>
</div>

<div class="main">
  <div id="map"><div class="yind" id="yind">📅 2026 — Current</div></div>
  <div class="sidebar">
    <div class="panel">
      <div class="ptitle">Pollution Index Legend</div>
      <div class="lrow"><div class="ldot" style="background:#27ae60"></div>Minimal (0–10)</div>
      <div class="lrow"><div class="ldot" style="background:#f1c40f"></div>Low (10–30)</div>
      <div class="lrow"><div class="ldot" style="background:#e67e22"></div>Moderate (30–50)</div>
      <div class="lrow"><div class="ldot" style="background:#e74c3c"></div>High (50–70)</div>
      <div class="lrow"><div class="ldot" style="background:#8e1010"></div>Critical (70+)</div>
      <p class="hint">Toggle the year above, drag the policy slider, and click a circle for details.</p>
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
      <div class="ptitle" id="ltTitle">League Table — 2026 · 2050 · 2100</div>
      <table id="lt">
        <thead><tr><th>#</th><th>Region</th><th>2026</th><th>2050</th><th>2100</th></tr></thead>
        <tbody id="ltBody"></tbody>
      </table>
    </div>
  </div>
</div>

<script>
const MD = {mj};
const CHART_META = {cmj};
let CY = 2026;
let SCEN = 0;       // policy reduction 0..1
let LM = [];
let chart;

const map = L.map('map',{{center:[20,10],zoom:2,minZoom:2,maxZoom:8}});
setTimeout(function(){{ map.invalidateSize(); }}, 300);
window.addEventListener('resize', function(){{ map.invalidateSize(); }});
L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png',
  {{attribution:'© OpenStreetMap © CARTO',subdomains:'abcd',maxZoom:19}}).addTo(map);

// Compute index for a given region at a year under current scenario.
// SCEN ranges -1 (much worse) .. 0 (now) .. +1 (full action).
// Positive SCEN reduces the growth rate; negative SCEN amplifies it.
function project(base, growth, year){{
  const yrs = year - 2026;
  let effGrowth;
  if(SCEN >= 0){{
    effGrowth = growth * (1 - SCEN);          // improvement: slow/stop growth
  }} else {{
    effGrowth = growth * (1 + Math.abs(SCEN)); // worsening: speed up growth
  }}
  return base * Math.pow(1 + effGrowth, yrs);
}}

function colour(s){{
  if(!s||s<=0) return '#2ecc71';
  if(s<10) return '#27ae60';
  if(s<30) return '#f1c40f';
  if(s<50) return '#e67e22';
  if(s<70) return '#e74c3c';
  return '#8e1010';
}}
function grade(s){{
  if(!s||s<=0) return 'Minimal';
  if(s<10) return 'Minimal'; if(s<30) return 'Low';
  if(s<50) return 'Moderate'; if(s<70) return 'High'; return 'Critical';
}}
function rad(s){{
  if(!s||s<=0) return 7;
  if(s<10) return 9; if(s<30) return 13;
  if(s<50) return 17; if(s<70) return 22; return 29;
}}

function build(){{
  LM.forEach(m=>map.removeLayer(m)); LM=[];
  MD.forEach(m=>{{
    const s = project(m.base, m.growth, CY);
    const c = colour(s), g = grade(s);
    const cm = L.circleMarker([m.lat,m.lon],{{
      radius:rad(s),fillColor:c,color:'#fff',weight:1.5,opacity:.9,fillOpacity:.75
    }}).addTo(map);
    cm.bindTooltip(`<b>${{m.region}}</b><br>${{CY}} Index: ${{s.toFixed(1)}} — ${{g}}`,{{direction:'top'}});
    cm.on('click',()=>{{
      const v2026=project(m.base,m.growth,2026), v2050=project(m.base,m.growth,2050), v2100=project(m.base,m.growth,2100);
      document.getElementById('dp').classList.add('on');
      document.getElementById('dtitle').textContent=m.region;
      document.getElementById('dscore').innerHTML=
        `<span class="sbadge" style="background:${{c}}22;color:${{c}};border:1px solid ${{c}}">`+
        `${{CY}}: ${{s.toFixed(1)}} / 100 — ${{g}}</span>`;
      document.getElementById('dbody').innerHTML=
        `<tr><td>🔬 Microplastics</td><td>${{m.mp}}</td></tr>`+
        `<tr><td>🏭 Port Pressure</td><td>${{m.port}}</td></tr>`+
        `<tr><td>🌊 River Plastic kg/yr</td><td>${{m.river}}</td></tr>`+
        `<tr><td>👥 Coastal Pop (10km)</td><td>${{m.pop}}</td></tr>`+
        `<tr><td>🧪 Ocean pH</td><td>${{m.ph}}</td></tr>`+
        `<tr><td>📅 2026 Index</td><td><b>${{v2026.toFixed(1)}}</b></td></tr>`+
        `<tr><td>📅 2050 Forecast</td><td><b style='color:#e67e22'>${{v2050.toFixed(1)}}</b></td></tr>`+
        `<tr><td>📅 2100 Forecast</td><td><b style='color:#e74c3c'>${{v2100.toFixed(1)}}</b></td></tr>`;
      document.querySelector('.sidebar').scrollTop=0;
    }});
    LM.push(cm);
  }});
}}

function buildLeague(){{
  // sort by current-year projected score
  const rows = MD.map(m=>({{
    region:m.region,
    v26:project(m.base,m.growth,2026),
    v50:project(m.base,m.growth,2050),
    v100:project(m.base,m.growth,2100)
  }})).sort((a,b)=>b.v26-a.v26);
  const gc={{Critical:'#8e1010',High:'#e74c3c',Moderate:'#e67e22',Low:'#f1c40f',Minimal:'#27ae60'}};
  let html='';
  rows.forEach((r,i)=>{{
    html+=`<tr><td style='color:#aaa'>${{i+1}}</td><td>${{r.region}}</td>`+
      `<td style='color:${{gc[grade(r.v26)]}};font-weight:bold'>${{r.v26.toFixed(1)}}</td>`+
      `<td style='color:${{gc[grade(r.v50)]}}'>${{r.v50.toFixed(1)}}</td>`+
      `<td style='color:${{gc[grade(r.v100)]}}'>${{r.v100.toFixed(1)}}</td></tr>`;
  }});
  document.getElementById('ltBody').innerHTML=html;
}}

function setY(y){{
  CY=y;
  ['b26','b50','b100'].forEach(id=>document.getElementById(id).classList.remove('active'));
  document.getElementById(y===2026?'b26':y===2050?'b50':'b100').classList.add('active');
  document.getElementById('yind').textContent=
    y===2026?'📅 2026 — Current':y===2050?'📅 2050 — Forecast':'📅 2100 — Long-term Forecast';
  build();
}}

const SCEN_DESC = {{
  '-100':'Worst case — pollution grows twice as fast as today.',
  '-50':'Things get worse — growth accelerates by half.',
  '0':'Showing the current trajectory — what happens if nothing changes.',
  '50':'Moderate global action — pollution growth cut in half.',
  '100':'Full action — pollution growth halted, and the worst trends reversed.'
}};
const SCEN_LABEL = {{
  '-100':'Worst case (2× growth)','-50':'Worsening (+50%)','0':'Current trajectory',
  '50':'Action (-50% growth)','100':'Full action (growth stopped)'
}};

function setScenario(val){{
  val = parseInt(val);
  SCEN = val/100;
  document.getElementById('scenVal').textContent = SCEN_LABEL[String(val)];
  document.getElementById('scenDesc').textContent = SCEN_DESC[String(val)];
  build();
  buildLeague();
  updateChart();
}}

// Chart
function chartData(){{
  return CHART_META.map(c=>({{
    label:c.label,
    data:[2026,2030,2040,2050,2100].map(y=>+project(c.base,c.growth,y).toFixed(2)),
    borderColor:c.color,backgroundColor:c.color+'22',
    tension:0.4,fill:false,pointRadius:5,borderWidth:2
  }}));
}}
function updateChart(){{
  chart.data.datasets = chartData();
  chart.update();
}}

build();
buildLeague();
chart = new Chart(document.getElementById('fc').getContext('2d'),{{
  type:'line',
  data:{{labels:['2026','2030','2040','2050','2100'],datasets:chartData()}},
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

out = os.path.join(OUT_DIR, "map.html")
with open(out,'w',encoding='utf-8') as fh: fh.write(html)
print(f"✅ Dashboard with policy scenarios saved: {out}")
