"use client";
import{useEffect,useState,useRef}from"react";
import{getMembers,getTwinState,getPredictions,getRoutines,sendChat,runSimulation}from"@/lib/api";
import{cn}from"@/lib/utils";
import{ENERGY_INSIGHTS,SAFETY_ALERTS,CULTURAL_CONTEXT,ROUTINE_PROFILE,NEXT_HOUR_PREDICTIONS,POWER_CUT_INTEL,FAMILY_ROLES,COMPARISON_DATA,MEMORY_TIMELINE}from"@/lib/intelligence-data";

const HERO="https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=1400&q=80";
const AV={m:"https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=80&q=80",f:"https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=80&q=80",s:"https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=80&q=80",p:"https://images.unsplash.com/photo-1566616213894-2d4e1baee5d8?w=80&q=80"};
const GAL=["https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=400&q=80","https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=400&q=80","https://images.unsplash.com/photo-1513694203232-719a280e022f?w=400&q=80","https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&q=80","https://images.unsplash.com/photo-1600607687644-aac4c3eac7f4?w=400&q=80","https://images.unsplash.com/photo-1581579438747-104c53d7fbb4?w=400&q=80"];
const PG=["home","dashboard","family","predictions","whatif","energy","memory","calendar","gallery","why"]as const;
type Pg=typeof PG[number];
const PL:Record<Pg,string>={home:"Home",dashboard:"Dashboard",family:"Family",predictions:"Predictions",whatif:"What-If",energy:"Energy",memory:"Memory",calendar:"Calendar",gallery:"Gallery",why:"Why Us"};

export default function App(){
const[pg,sP]=useState<Pg>("home");const[mn,sMn]=useState(false);const[co,sCo]=useState(false);
const[ld,sLd]=useState(true);const[mems,sMs]=useState<any[]>([]);const[tw,sTw]=useState<any>(null);const[pr,sPr]=useState<any[]>([]);const[rt,sRt]=useState<any[]>([]);
const[msgs,sMsg]=useState<{r:string;t:string}[]>([]);const[ci,sCi]=useState("");const[cl,sCl]=useState(false);const[sp,sSp]=useState(false);
const[dm,sDm]=useState(false);const[di,sDi]=useState(0);const dr=useRef<any>(null);
const[fam,sFam]=useState<any[]>([]);const[fm,sFm]=useState(false);const[ff,sff]=useState({name:"",role:"Student",age:"",bday:"",img:""});
const[famDet,sFamDet]=useState<any>(null);
// Member tasks/alarms data
const memberData:Record<string,{tasks:string[];alarms:{time:string;label:string}[]}> = {
  "Lakshmi":{tasks:["Morning pooja preparation","Run water motor at 6:15 AM","Breakfast and lunch cooking","Evening coffee preparation","Coordinate household activities"],alarms:[{time:"05:45",label:"Wake up for pooja"},{time:"06:15",label:"Run water motor"},{time:"11:30",label:"Start lunch preparation"},{time:"16:45",label:"Coffee preparation"}]},
  "Venkat":{tasks:["Office commute by 9:00 AM","Ensure laptop is charged","Check household status before leaving","Evening family coordination"],alarms:[{time:"06:30",label:"Wake up"},{time:"08:45",label:"Leave for office"},{time:"13:30",label:"Charge devices (power cut risk)"}]},
  "Arjun":{tasks:["Study Physics from 8:00 PM","Keep laptop charged before power cut","Follow quiet mode during exam preparation","Complete tuition assignments"],alarms:[{time:"05:30",label:"Wake up"},{time:"13:00",label:"Download study materials (power cut prep)"},{time:"19:00",label:"Revision reminder"},{time:"20:00",label:"Exam quiet mode active"}]},
  "Paati":{tasks:["Morning aarti at 5:30 AM","Temple visit on Tuesday and Friday","Afternoon rest period","Evening prayer"],alarms:[{time:"04:30",label:"Wake up"},{time:"05:30",label:"Morning aarti"},{time:"13:00",label:"Afternoon rest"},{time:"18:00",label:"Evening prayer"}]},
};
const[gal,sGal]=useState(GAL.map((u,i)=>({id:`g${i}`,url:u})));const[gi,sGi]=useState("");
const[sr,sSr]=useState<any>(null);const[sl,sSl]=useState(false);
const cal=[{i:"🎂",t:"Paati Birthday",d:"Jan 20"},{i:"🪔",t:"Pongal",d:"Jan 14"},{i:"📚",t:"Board Exam",d:"Jan 26"},{i:"💧",t:"Motor",d:"Daily 6:15"},{i:"⚡",t:"Power Cut",d:"Thu 2PM"},{i:"☕",t:"Coffee",d:"Daily 5PM"}];
// Mood/Energy profile
const moods=["Calm","Busy","Festive","Stressed","Sleeping"];const mood=moods[Math.floor(Date.now()/60000)%5];
const ePro=["Eco-Friendly","Balanced","High Consumption","Night Active"][1];

useEffect(()=>{Promise.all([getMembers(),getTwinState(),getPredictions(),getRoutines()]).then(([m,t,p,r])=>{sMs(m?.members||[]);sTw(t);sPr(p?.predictions||[]);sRt(r?.routines||[]);sFam((m?.members||[]).map((x:any,i:number)=>({...x,img:[AV.m,AV.f,AV.s,AV.p][i]||""})));sLd(false);});},[]);

const urg=tw?.urgency_score??0,tank=tw?.resources?.water?.tank_level_pct??50,pwr=tw?.resources?.power?.cut_probability??0;
const hp=Math.min(100,Math.round((tank>60?25:15)+(pwr<.3?25:10)+(urg<30?25:15)+25));

function nav(p:Pg){sP(p);sMn(false);}
// Demo
function dStart(){sDm(true);sDi(0);}function dPause(){sDm(false);}function dRestart(){sDi(0);sDm(true);}
useEffect(()=>{if(!dm){if(dr.current)clearInterval(dr.current);return;}dr.current=setInterval(()=>{sDi(i=>{const n=(i+1)%PG.length;sP(PG[n]);return n;});},500);return()=>{if(dr.current)clearInterval(dr.current);};},[dm]);
// Chat
async function csend(){if(!ci.trim())return;sMsg(p=>[...p,{r:"u",t:ci.trim()}]);sCi("");sCl(true);const r=await sendChat(ci.trim());sMsg(p=>[...p,{r:"a",t:r.response||"Processing."}]);sCl(false);}
function speak(t:string){if(sp){speechSynthesis.cancel();sSp(false);return;}const u=new SpeechSynthesisUtterance(t);u.lang="en-IN";u.rate=.95;u.onend=()=>sSp(false);speechSynthesis.speak(u);sSp(true);}
const qk=[{l:"Predict Today",t:"Motor 6:15 (96%). Power cut 2 PM (76%). Quiet mode 8 PM (92%). Coffee 5 PM (93%)."},{l:"Home Status",t:"All 4 members home. Tank 42%. Power stable. Exam prep active."},{l:"Power Risk",t:"76% outage 2 PM. Charge devices by 1:30 PM. Download study materials offline."},{l:"Energy Report",t:"18% savings available. Shift washing to off-peak. Limit geyser to 15 min."},{l:"Anomaly Check",t:"Geyser running 18 min (normal 15). Auto-shutoff recommended. No other anomalies."}];
// Family
function addF(){if(!ff.name)return;sFam(p=>[...p,{id:`f${Date.now()}`,name:ff.name,role:ff.role,age:ff.age,birthday:ff.bday,img:ff.img||`https://i.pravatar.cc/60?u=${Date.now()}`}]);sff({name:"",role:"Student",age:"",bday:"",img:""});sFm(false);}
function delF(id:string){if(confirm("Remove?")){sFam(p=>p.filter(f=>f.id!==id));}}
// Sim
async function doSim(k:string){sSl(true);sSr(null);const s:any={power:{scenario_name:"Power Cut",hypothesis:"Outage 2PM",perturbations:[{type:"power_cut",params:{start_time:"14:00",duration_hours:1.5}}],sim_duration_hours:6},exam:{scenario_name:"Exam",hypothesis:"Board exam tomorrow",perturbations:[{type:"exam_week",params:{exam_type:"Board",duration_days:1}}],sim_duration_hours:12},guests:{scenario_name:"Guests",hypothesis:"6 guests 7PM",perturbations:[{type:"unexpected_guest",params:{count:6,arrival_time:"19:00",duration_hours:3}}],sim_duration_hours:6}};const r=await runSimulation(s[k]);sSr(r);sSl(false);}

if(ld)return<div className="min-h-screen flex items-center justify-center"><div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin"/></div>;

return(<div className="min-h-screen flex flex-col">
{/* ═══ TOP BAR ═══ */}
<header className="fixed top-0 inset-x-0 z-50 bg-[#080b12]/90 backdrop-blur-xl border-b border-[var(--border)] h-12">
<div className="h-full max-w-[1400px] mx-auto px-3 flex items-center">
  <span className="text-sm font-extrabold text-grad cursor-pointer mr-4" onClick={()=>nav("home")}>GHARMIND AI</span>
  {/* Status pills */}
  <div className="hidden md:flex items-center gap-2 mr-4">
    <span className="badge badge-g">{mood}</span>
    <span className="badge badge-b">Health {hp}%</span>
    {pwr>.6&&<span className="badge badge-a ap">⚡ Power Risk</span>}
  </div>
  {/* Nav */}
  <nav className="hidden lg:flex items-center gap-0.5 flex-1 justify-end">
    {PG.map(p=><button key={p} onClick={()=>nav(p)} className={cn("btn-g",pg===p&&"text-cyan-400 bg-cyan-500/10")}>{PL[p]}</button>)}
  </nav>
  {/* Demo */}
  <div className="hidden md:flex items-center gap-1.5 ml-3">{dm?<><button onClick={dPause} className="btn-s text-[9px] py-1 px-2">⏸</button><button onClick={dRestart} className="btn-s text-[9px] py-1 px-2">🔄</button></>:<button onClick={dStart} className="btn-p text-[9px] py-1 px-2.5">▶ Demo</button>}</div>
  {/* Hamburger */}
  <button onClick={()=>sMn(!mn)} className="lg:hidden ml-auto p-1.5 rounded hover:bg-white/5"><svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h16"/></svg></button>
</div>
</header>
{mn&&<div className="fixed inset-0 z-40 bg-black/50 lg:hidden" onClick={()=>sMn(false)}/>}
{mn&&<div className="fixed top-12 right-0 z-50 w-56 bg-[var(--card)] border-l border-[var(--border)] h-[calc(100vh-48px)] p-3 space-y-1 overflow-y-auto lg:hidden">{PG.map(p=><button key={p} onClick={()=>nav(p)} className="w-full text-left px-3 py-2.5 rounded-lg text-xs hover:bg-white/5">{PL[p]}</button>)}<div className="pt-2 border-t border-[var(--border)] mt-2">{dm?<button onClick={dPause} className="btn-s w-full text-[10px]">⏸ Pause</button>:<button onClick={dStart} className="btn-p w-full text-[10px]">▶ Demo</button>}</div></div>}

{/* ═══ MAIN ═══ */}
<main className="flex-1 pt-12 af" key={pg}>

{/* HOME */}
{pg==="home"&&<section className="h-[100vh] relative flex items-center">
<img src={HERO} alt="" className="absolute inset-0 w-full h-full object-cover"/>
<div className="absolute inset-0 bg-gradient-to-r from-[#080b12]/90 via-[#080b12]/60 to-[#080b12]/30"/>
<div className="relative z-10 max-w-5xl mx-auto px-6">
  <p className="text-cyan-400 text-[9px] font-bold tracking-[.3em] uppercase mb-2">India's First</p>
  <h1 className="text-4xl md:text-6xl font-black text-white leading-[1.05]">GHARMIND<br/><span className="text-grad">AI</span></h1>
  <p className="text-sm text-white/60 mt-3 max-w-sm">AI Household Operating System. Predicting household needs before anyone asks.</p>
  <div className="flex gap-2.5 mt-6"><button onClick={dStart} className="btn-p">▶ Start Demo</button><button onClick={()=>nav("dashboard")} className="btn-s border-white/20 text-white/80">Open Dashboard</button></div>
</div>
</section>}

{/* DASHBOARD */}
{pg==="dashboard"&&<div className="max-w-6xl mx-auto px-4 py-6 grid lg:grid-cols-[200px_1fr_220px] gap-4">
  {/* Left - Roles */}
  <aside className="hidden lg:block space-y-3">
    <div className="card-glow"><p className="text-[9px] font-bold text-cyan-400 uppercase mb-2">Detected Roles</p>{FAMILY_ROLES.map((r,i)=><div key={i} className="py-1.5 border-b border-[var(--border)] last:border-0"><p className="text-[10px] font-medium">{r.icon} {r.name}</p><p className="text-[8px] text-emerald-400">{r.role}</p></div>)}</div>
    <div className="card"><p className="text-[9px] font-bold text-amber-400 uppercase mb-1">Mood</p><p className="text-lg font-bold">{mood}</p><p className="text-[8px] text-muted">Based on activity patterns</p></div>
    <div className="card"><p className="text-[9px] font-bold text-purple-400 uppercase mb-1">Energy Profile</p><p className="text-sm font-bold">{ePro}</p><p className="text-[8px] text-emerald-400">↓18% savings available</p></div>
  </aside>
  {/* Center - Command */}
  <div className="space-y-4">
    {/* Stats */}
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2">{[{v:hp,l:"Health",c:"text-emerald-400"},{v:urg,l:"Urgency",c:urg>60?"text-red-400":"text-amber-400"},{v:`${tank}%`,l:"Water",c:tank<40?"text-red-400":"text-cyan-400"},{v:`${Math.round(pwr*100)}%`,l:"Power",c:pwr>.6?"text-amber-400":"text-emerald-400"},{v:"Tmrw",l:"Exam",c:"text-purple-400"}].map((s,i)=><div key={i} className="card text-center py-3"><p className={cn("text-lg font-bold",s.c)}>{s.v}</p><p className="text-[10px] text-muted mt-0.5">{s.l}</p></div>)}</div>
    {/* Next Actions */}
    <div className="card-glow"><p className="text-[10px] font-bold text-cyan-400 uppercase mb-2">Next Action Predictions</p>{NEXT_HOUR_PREDICTIONS.map((p,i)=><div key={i} className="flex items-center gap-2 py-2 border-b border-[var(--border)] last:border-0"><span className="text-emerald-400 font-bold text-sm w-9">{Math.round(p.confidence*100)}%</span><div className="flex-1"><p className="text-xs font-medium">{p.action}</p><p className="text-[10px] text-muted">{p.explanation.slice(0,80)}...</p></div></div>)}</div>
    {/* Twin */}
    <div className="card"><div className="flex items-center gap-1.5 mb-2"><span className="w-1.5 h-1.5 bg-emerald-400 rounded-full ap"/><p className="text-[9px] font-bold">LIVE TWIN</p></div>{fam.slice(0,4).map((m:any,i:number)=><div key={i} className="flex items-center gap-2 py-1 border-b border-[var(--border)] last:border-0"><img src={m.img} alt="" className="w-5 h-5 rounded-full object-cover"/><span className="text-[10px] flex-1">{m.name}</span><span className="text-[8px] text-muted">{(m.simulated_location||"").replace(/_/g," ")}</span></div>)}</div>
    {/* Predictions */}
    <div className="card"><p className="text-[9px] font-bold uppercase mb-2">AI Predictions</p>{pr.slice(0,3).map((p:any,i:number)=><div key={i} className="flex gap-2 py-1.5 border-b border-[var(--border)] last:border-0"><div className="flex-1"><p className="text-[10px] font-medium">{p.title}</p><p className="text-[8px] text-muted">{p.action_suggestion}</p></div><span className={cn("badge",p.priority==="critical"?"badge-r":"badge-b")}>{Math.round(p.confidence*100)}%</span></div>)}</div>
  </div>
  {/* Right - Intelligence */}
  <aside className="hidden lg:block space-y-3">
    <div className="card"><p className="text-[9px] font-bold text-cyan-400 uppercase mb-2">Power Intelligence</p><div className={cn("badge mb-1.5",POWER_CUT_INTEL.riskLevel==="high"?"badge-r":"badge-a")}>{POWER_CUT_INTEL.riskLevel} risk</div><p className="text-[9px]">{POWER_CUT_INTEL.probability}% at {POWER_CUT_INTEL.expectedTime}</p><div className="mt-2 space-y-0.5">{POWER_CUT_INTEL.recommendations.slice(0,3).map((r,i)=><p key={i} className="text-[8px] text-muted">• {r.action.slice(0,50)}</p>)}</div></div>
    <div className="card"><p className="text-[9px] font-bold text-emerald-400 uppercase mb-2">Energy Optimizer</p><p className="text-xl font-bold text-emerald-400">↓{ENERGY_INSIGHTS.estimatedSavings}%</p><p className="text-[8px] text-muted">savings available</p></div>
    <div className="card"><p className="text-[9px] font-bold text-purple-400 uppercase mb-2">Cultural Intel</p><p className="text-[10px]">🪔 {CULTURAL_CONTEXT.festivalName}</p><p className="text-[8px] text-muted">{CULTURAL_CONTEXT.daysAway} days away</p></div>
    <div className="card"><p className="text-[9px] font-bold text-amber-400 uppercase mb-2">Conflicts</p><p className="text-[9px] text-emerald-400">✓ No active conflicts</p><p className="text-[8px] text-muted">Schedule optimized</p></div>
  </aside>
</div>}

{/* FAMILY */}
{pg==="family"&&<div className="max-w-4xl mx-auto px-4 py-6 space-y-4"><div className="flex justify-between items-center"><h2 className="text-base font-bold">Family Members</h2><button onClick={()=>sFm(true)} className="btn-p text-[10px]">+ Add</button></div>
<div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">{fam.map((m:any,i:number)=><div key={m.id||i} onClick={()=>sFamDet(m)} className="card text-center relative group cursor-pointer hover:border-cyan-800/50 transition-all"><img src={m.img||""} alt="" className="w-12 h-12 mx-auto rounded-full object-cover border border-cyan-900/40"/><p className="text-xs font-semibold mt-2">{m.name}</p><p className="text-[10px] text-muted">{m.role}{m.age?` • Age ${m.age}`:""}</p>{m.birthday&&<p className="text-[10px] text-cyan-400 mt-0.5">🎂 {m.birthday}</p>}<button onClick={(e)=>{e.stopPropagation();delF(m.id);}} className="absolute top-2 right-2 w-5 h-5 rounded bg-red-500/20 text-red-400 text-[10px] opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">✕</button></div>)}</div>
<p className="text-[11px] text-muted text-center">Click a member to view details, tasks, and alarms.</p>
{/* Family Detail Modal */}
{famDet&&<div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4 md:p-6" onClick={()=>sFamDet(null)}><div className="bg-[var(--card)] rounded-2xl p-5 md:p-6 w-full max-w-sm md:max-w-md border border-[var(--border)] max-h-[90vh] overflow-y-auto" onClick={e=>e.stopPropagation()}>
  <div className="flex items-center gap-3 mb-4"><img src={famDet.img||""} alt="" className="w-14 h-14 rounded-full object-cover border border-cyan-900/40"/><div><p className="text-base font-bold">{famDet.name}</p><p className="text-xs text-cyan-400">{famDet.role||"Member"}</p>{famDet.birthday&&<p className="text-[11px] text-muted">Birthday: {famDet.birthday}</p>}{famDet.age&&<p className="text-[11px] text-muted">Age: {famDet.age}</p>}</div></div>
  {/* Tasks */}
  <div className="mb-4"><p className="text-xs font-bold text-emerald-400 uppercase mb-2">Daily Responsibilities</p><div className="space-y-1.5">{(memberData[famDet.name]?.tasks||["No specific tasks assigned yet."]).map((t:string,i:number)=><div key={i} className="flex items-start gap-2"><span className="text-emerald-400 text-[11px] mt-0.5">•</span><p className="text-xs text-[var(--fg)]/80">{t}</p></div>)}</div></div>
  {/* Alarms */}
  <div className="mb-4"><p className="text-xs font-bold text-amber-400 uppercase mb-2">Alarms & Reminders</p><div className="space-y-1.5">{(memberData[famDet.name]?.alarms||[{time:"--:--",label:"No alarms set"}]).map((a:{time:string;label:string},i:number)=><div key={i} className="flex items-center gap-2 py-1 border-b border-[var(--border)] last:border-0"><span className="text-xs font-mono text-amber-400 w-12">{a.time}</span><p className="text-xs">{a.label}</p></div>)}</div></div>
  <button onClick={()=>sFamDet(null)} className="btn-s w-full text-xs mt-2">Close</button>
</div></div>}
{/* Add Member Modal */}
{fm&&<div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" onClick={()=>sFm(false)}><div className="bg-[var(--card)] rounded-2xl p-5 w-full max-w-xs md:max-w-sm border border-[var(--border)] space-y-2.5 max-h-[90vh] overflow-y-auto" onClick={e=>e.stopPropagation()}><h3 className="text-sm font-bold">Add Member</h3><input placeholder="Name" value={ff.name} onChange={e=>sff(f=>({...f,name:e.target.value}))} className="w-full px-3 py-2 rounded-lg bg-[var(--bg)] border border-[var(--border)] text-xs"/><select value={ff.role} onChange={e=>sff(f=>({...f,role:e.target.value}))} className="w-full px-3 py-2 rounded-lg bg-[var(--bg)] border border-[var(--border)] text-xs">{["Student","Professional","Homemaker","Elderly","Child"].map(r=><option key={r}>{r}</option>)}</select><div className="grid grid-cols-2 gap-2"><input placeholder="Age" type="number" value={ff.age} onChange={e=>sff(f=>({...f,age:e.target.value}))} className="px-3 py-2 rounded-lg bg-[var(--bg)] border border-[var(--border)] text-xs"/><input type="date" value={ff.bday} onChange={e=>sff(f=>({...f,bday:e.target.value}))} className="px-3 py-2 rounded-lg bg-[var(--bg)] border border-[var(--border)] text-xs"/></div><input placeholder="Image URL" value={ff.img} onChange={e=>sff(f=>({...f,img:e.target.value}))} className="w-full px-3 py-2 rounded-lg bg-[var(--bg)] border border-[var(--border)] text-xs"/><div className="flex gap-2"><button onClick={addF} className="btn-p flex-1 text-[10px]">Save</button><button onClick={()=>sFm(false)} className="btn-s flex-1 text-[10px]">Cancel</button></div></div></div>}
</div>}

{/* PREDICTIONS */}
{pg==="predictions"&&<div className="max-w-4xl mx-auto px-4 py-6 space-y-3"><h2 className="text-base font-bold mb-3">Predictions</h2>{pr.map((p:any,i:number)=><div key={i} className="card-glow"><div className="flex gap-2"><div className="flex-1"><p className="text-xs font-semibold">{p.title}</p><p className="text-[11px] text-muted mt-0.5">{p.action_suggestion}</p></div><span className={cn("badge",p.priority==="critical"?"badge-r":p.priority==="high"?"badge-a":"badge-b")}>{Math.round(p.confidence*100)}%</span></div><details className="mt-2"><summary className="text-[10px] text-cyan-400 cursor-pointer">Explainable AI — View reasoning</summary><p className="text-[11px] text-muted mt-1 pl-2 border-l border-cyan-800">{p.category==="water"?"14 weekday motor patterns. Tank below 45%. CMWSSB supply window active. Confidence adjusted by seasonal context.":p.category==="power"?"TNEB Thursday 2 PM load-shedding. Confirmed 5 of 7 weeks. Zone C2 historical data.":"Historical routine execution analysis with seasonal and calendar context."}</p></details></div>)}</div>}

{/* WHAT-IF */}
{pg==="whatif"&&<div className="max-w-4xl mx-auto px-4 py-6 space-y-4"><h2 className="text-base font-bold mb-3">What-If Simulator</h2><div className="grid grid-cols-3 gap-3">{[{k:"power",i:"⚡",l:"Power Cut"},{k:"exam",i:"📚",l:"Exam"},{k:"guests",i:"👥",l:"Guests"}].map(s=><button key={s.k} onClick={()=>doSim(s.k)} className="card-glow text-center py-4 hover:border-cyan-700/60 transition-all"><span className="text-xl">{s.i}</span><p className="text-[9px] mt-1">{s.l}</p></button>)}</div>{sl&&<p className="text-[10px] text-muted text-center ap py-4">Simulating...</p>}{sr&&<div className="card space-y-2"><span className="badge badge-a">Impact: {sr.overall_severity}</span><p className="text-[10px]">{sr.result_summary}</p>{sr.action_plan?.map((a:any,i:number)=><div key={i} className="flex gap-2 text-[9px]"><span className="font-mono text-muted w-10">{a.time}</span><span>{a.action}</span></div>)}{sr.cascade_chain?.length>0&&<details><summary className="text-[8px] text-cyan-400 cursor-pointer">Cascade chain</summary><div className="mt-1">{sr.cascade_chain.map((c:string,i:number)=><p key={i} className="text-[8px] text-muted">→ {c}</p>)}</div></details>}</div>}</div>}

{/* ENERGY */}
{pg==="energy"&&<div className="max-w-4xl mx-auto px-4 py-6 space-y-4"><h2 className="text-base font-bold mb-3">Energy & Safety</h2><div className="grid md:grid-cols-2 gap-3"><div className="card-glow text-center"><p className="text-2xl font-bold text-emerald-400">↓{ENERGY_INSIGHTS.estimatedSavings}%</p><p className="text-[8px] text-muted">savings identified</p><div className="mt-2 text-left">{ENERGY_INSIGHTS.topConsumers.slice(0,3).map((c,i)=><p key={i} className="text-[9px] py-1 border-b border-[var(--border)] last:border-0 flex justify-between"><span>{c.appliance}</span><span className="text-muted">{c.usage}</span></p>)}</div></div><div className="card"><p className="text-[9px] font-bold text-amber-400 uppercase mb-2">Safety Monitoring</p>{SAFETY_ALERTS.map(a=><div key={a.id} className="py-1.5 border-b border-[var(--border)] last:border-0"><p className="text-[9px] font-medium">{a.appliance}</p><p className="text-[8px] text-muted">{a.reason}</p><p className="text-[8px] text-emerald-400">→ {a.action}</p></div>)}</div></div></div>}

{/* MEMORY */}
{pg==="memory"&&<div className="max-w-4xl mx-auto px-4 py-6 space-y-3"><h2 className="text-base font-bold mb-3">Memory Timeline — 7 Days</h2>{MEMORY_TIMELINE.map((d,i)=><div key={i} className="card flex gap-3"><div className="w-14 flex-shrink-0"><p className="text-[9px] font-medium">{d.day}</p><div className="flex items-center gap-1 mt-0.5"><div className="h-1 flex-1 rounded-full bg-[var(--border)] overflow-hidden"><div className="h-full rounded-full bg-cyan-500/60" style={{width:`${d.consistency}%`}}/></div><span className="text-[7px] text-muted">{d.consistency}%</span></div></div><div><p className="text-[8px] text-cyan-400">{d.highlight}</p><p className="text-[8px] text-muted">{d.events.join(" • ")}</p></div></div>)}<div className="card"><p className="text-[9px] font-bold text-purple-400 uppercase mb-2">AI Home Diary — Today</p><p className="text-[9px] text-muted leading-relaxed">Morning pooja completed on schedule. Water motor ran 25 min at 6:15 AM. Arjun studied from 8-10 PM (exam prep mode). Power stable throughout. Household mood: focused. Tomorrow prediction: Board exam at 10 AM — quiet morning expected.</p></div></div>}

{/* CALENDAR */}
{pg==="calendar"&&<div className="max-w-3xl mx-auto px-4 py-6 space-y-2"><h2 className="text-base font-bold mb-3">Calendar</h2>{cal.map((e,i)=><div key={i} className="card flex items-center gap-3"><span className="text-lg">{e.i}</span><div><p className="text-[10px] font-medium">{e.t}</p><p className="text-[8px] text-muted">{e.d}</p></div></div>)}</div>}

{/* GALLERY */}
{pg==="gallery"&&<div className="max-w-4xl mx-auto px-4 py-6 space-y-4"><h2 className="text-base font-bold">Gallery</h2><div className="flex gap-2"><input value={gi} onChange={e=>sGi(e.target.value)} placeholder="Image URL..." className="flex-1 px-3 py-1.5 rounded-lg bg-[var(--bg)] border border-[var(--border)] text-xs"/><button onClick={()=>{if(gi.trim()){sGal(p=>[...p,{id:`g${Date.now()}`,url:gi.trim()}]);sGi("");}}} className="btn-p text-[9px]">+ Add</button></div><div className="grid grid-cols-2 md:grid-cols-3 gap-3">{gal.map(g=><div key={g.id} className="relative rounded-xl overflow-hidden group"><img src={g.url} alt="" className="w-full h-32 object-cover group-hover:scale-105 transition-transform duration-300"/><button onClick={()=>sGal(p=>p.filter(x=>x.id!==g.id))} className="absolute top-1.5 right-1.5 w-5 h-5 rounded bg-red-500/80 text-white text-[8px] flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">✕</button></div>)}</div></div>}

{/* WHY */}
{pg==="why"&&<div className="max-w-4xl mx-auto px-4 py-6 space-y-4"><h2 className="text-base font-bold mb-3">Why GharMind AI is Different</h2><div className="grid md:grid-cols-2 gap-4"><div className="card border-l-2 border-l-red-500/50"><p className="text-[9px] font-bold text-red-400 uppercase mb-2">Traditional Smart Home</p>{COMPARISON_DATA.traditional.map((t,i)=><p key={i} className="text-[9px] text-muted py-1 border-b border-[var(--border)] last:border-0">✗ {t.value}</p>)}</div><div className="card-glow border-l-2 border-l-emerald-500/50"><p className="text-[9px] font-bold text-emerald-400 uppercase mb-2">GharMind AI</p>{COMPARISON_DATA.gharmind.map((g,i)=><p key={i} className="text-[9px] text-emerald-300 py-1 border-b border-[var(--border)] last:border-0">✓ {g.value}</p>)}</div></div><div className="card mt-4"><p className="text-[9px] font-bold text-cyan-400 uppercase mb-2">Self-Learning Feedback</p><p className="text-[9px] text-muted">Every prediction can be accepted or rejected. GharMind learns from your feedback to improve future suggestions continuously.</p><div className="flex gap-2 mt-2"><button className="btn-p text-[8px] py-1 px-2">✓ Accept</button><button className="btn-s text-[8px] py-1 px-2">✗ Reject</button><span className="text-[8px] text-emerald-400 self-center ml-2">→ GharMind learned from this feedback.</span></div></div></div>}

</main>

{/* ═══ FLOATING CHAT ═══ */}
<button onClick={()=>sCo(!co)} className="fixed bottom-4 right-4 z-50 w-11 h-11 rounded-full bg-gradient-to-br from-blue-600 to-cyan-500 text-white shadow-lg shadow-cyan-500/30 flex items-center justify-center text-base hover:scale-110 transition-transform">{co?"✕":"💬"}</button>
{co&&<div className={cn("fixed z-50 bg-[var(--card)] border border-[var(--border)] shadow-2xl flex flex-col","inset-0 md:inset-auto md:bottom-16 md:right-4 md:w-[340px] md:max-h-[420px] md:rounded-xl")}>
<div className="px-3 py-2 border-b border-[var(--border)] flex items-center justify-between"><div><p className="text-xs font-bold text-grad">Gharji AI</p><p className="text-[9px] text-muted">Household intelligence</p></div><button onClick={()=>sCo(false)} className="md:hidden text-sm">✕</button></div>
<div className="flex-1 overflow-y-auto p-3 space-y-2 min-h-[150px] max-h-[220px]">{msgs.length===0&&<p className="text-[11px] text-muted text-center py-6">Ask about your household.</p>}{msgs.map((m,i)=><div key={i} className={cn("max-w-[85%] rounded-lg px-3 py-2 text-xs leading-relaxed",m.r==="u"?"ml-auto bg-blue-500/10 border border-blue-500/20":"bg-[var(--bg)] border border-[var(--border)]")}>{m.t}{m.r==="a"&&<button onClick={()=>speak(m.t)} className="block mt-1 text-[9px] text-cyan-400 hover:underline">{sp?"⏹ Stop Speaking":"🔊 Read Aloud"}</button>}</div>)}{cl&&<div className="bg-[var(--bg)] border border-[var(--border)] rounded-lg px-3 py-2 w-14"><span className="text-[11px] ap">...</span></div>}</div>
<div className="px-3 py-2 border-t border-[var(--border)] flex gap-1.5 flex-wrap">{qk.map(q=><button key={q.l} onClick={()=>sMsg(p=>[...p,{r:"u",t:q.l},{r:"a",t:q.t}])} className="text-[9px] px-2 py-1 rounded border border-[var(--border)] hover:bg-white/5 transition-all">{q.l}</button>)}</div>
<div className="p-3 border-t border-[var(--border)] flex gap-2"><input value={ci} onChange={e=>sCi(e.target.value)} onKeyDown={e=>e.key==="Enter"&&csend()} placeholder="Ask anything..." className="flex-1 px-3 py-2 rounded-lg bg-[var(--bg)] border border-[var(--border)] text-xs focus:outline-none focus:border-cyan-700"/><button onClick={csend} className="px-3 py-2 rounded-lg bg-blue-600 text-white text-[10px] font-semibold">Send</button></div>
</div>}
</div>);
}
