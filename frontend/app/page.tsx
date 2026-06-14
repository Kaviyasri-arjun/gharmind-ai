"use client";
import{useEffect,useState,useRef}from"react";
import{getMembers,getTwinState,getPredictions,getRoutines,sendChat,runSimulation}from"@/lib/api";
import{cn}from"@/lib/utils";
import{ENERGY_INSIGHTS,SAFETY_ALERTS,CULTURAL_CONTEXT,ROUTINE_PROFILE,NEXT_HOUR_PREDICTIONS,POWER_CUT_INTEL,FAMILY_ROLES,COMPARISON_DATA,MEMORY_TIMELINE}from"@/lib/intelligence-data";

const HERO="https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=1400&q=80";
const AV={m:"https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=80&q=80",f:"https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=80&q=80",s:"https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=80&q=80",p:"https://images.unsplash.com/photo-1566616213894-2d4e1baee5d8?w=80&q=80"};
const GAL_DATA=[
  {url:"https://images.unsplash.com/photo-1609220136736-443140cffec6?w=400&q=80",cap:"Pongal Celebration",date:"Jan 14",members:"All Family",tag:"Festival",ai:"Remembered by GharMind"},
  {url:"https://images.unsplash.com/photo-1574158622682-e40e69881006?w=400&q=80",cap:"Evening Family Dinner",date:"Weekly",members:"Lakshmi, Venkat, Arjun, Paati",tag:"Routine",ai:"Pattern detected over 90 days"},
  {url:"https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9?w=400&q=80",cap:"Arjun Exam Achievement",date:"Mar 2025",members:"Arjun",tag:"Achievement",ai:"Study routine linked"},
  {url:"https://images.unsplash.com/photo-1542992015-4a0b729b1385?w=400&q=80",cap:"Morning Pooja",date:"Daily",members:"Lakshmi, Paati",tag:"Routine",ai:"Pattern detected over 340 days"},
  {url:"https://images.unsplash.com/photo-1529543544006-1bd3fa44b178?w=400&q=80",cap:"Diwali Celebration",date:"Oct 2024",members:"All Family",tag:"Festival",ai:"Cultural event memory"},
  {url:"https://images.unsplash.com/photo-1511632765486-a01980e01a18?w=400&q=80",cap:"Family Gathering",date:"Dec 2024",members:"Extended Family",tag:"Family",ai:"Guest pattern recorded"},
  {url:"https://images.unsplash.com/photo-1606787366850-de6330128bfc?w=400&q=80",cap:"Evening Chai Time",date:"Daily 5 PM",members:"Lakshmi, Venkat",tag:"Routine",ai:"300+ occurrences detected"},
  {url:"https://images.unsplash.com/photo-1588075592446-265fd1e6e76f?w=400&q=80",cap:"Study Session",date:"Weekdays",members:"Arjun",tag:"Routine",ai:"8-10 PM pattern confirmed"},
  {url:"https://images.unsplash.com/photo-1464820453369-31d2c0b651af?w=400&q=80",cap:"Paati Birthday",date:"Jan 20",members:"All Family",tag:"Family",ai:"Annual reminder set"},
];
const PG=["home","dashboard","family","predictions","memory","howitworks"]as const;
type Pg=typeof PG[number];
const PL:Record<Pg,string>={home:"Home",dashboard:"Dashboard",family:"Family",predictions:"Predictions",memory:"Memory",howitworks:"How It Works"};

export default function App(){
const[pg,sP]=useState<Pg>("home");const[mn,sMn]=useState(false);const[co,sCo]=useState(false);const[hsOpen,setHsOpen]=useState(false);
const[subTab,setSubTab]=useState<string>("");
const[ld,sLd]=useState(true);const[mems,sMs]=useState<any[]>([]);const[tw,sTw]=useState<any>(null);const[pr,sPr]=useState<any[]>([]);const[rt,sRt]=useState<any[]>([]);
const[msgs,sMsg]=useState<{r:string;t:string}[]>([]);const[ci,sCi]=useState("");const[cl,sCl]=useState(false);const[sp,sSp]=useState(false);
const[dm,sDm]=useState(false);const[di,sDi]=useState(0);const dr=useRef<any>(null);
const[fam,sFam]=useState<any[]>([]);const[fm,sFm]=useState(false);const[ff,sff]=useState({name:"",role:"Student",age:"",bday:"",img:""});

// ── Live Clock ──
const[clock,setClock]=useState("");
useEffect(()=>{const tick=()=>{const d=new Date();setClock(d.toLocaleDateString("en-IN",{weekday:"short",timeZone:"Asia/Kolkata"})+" • "+d.toLocaleTimeString("en-IN",{hour:"2-digit",minute:"2-digit",second:"2-digit",hour12:true,timeZone:"Asia/Kolkata"})+" IST");};tick();const t=setInterval(tick,1000);return()=>clearInterval(t);},[]);

// ── Alarm Notification System ──
const[alarm,setAlarm]=useState<{name:string;routine:string;action:string}|null>(null);
const alarmChecked=useRef<Set<string>>(new Set());
const routineAlarms=[
  {member:"Arjun",routine:"School Departure",time:"08:00",action:"Ensure school bag is packed and breakfast is done."},
  {member:"Arjun",routine:"Tuition Class",time:"18:00",action:"Keep study materials ready."},
  {member:"Arjun",routine:"Exam Quiet Mode",time:"20:00",action:"Enforce quiet hours. Turn off TV."},
  {member:"Lakshmi",routine:"Morning Pooja",time:"06:00",action:"Prepare pooja thali and light lamp."},
  {member:"Lakshmi",routine:"Water Motor",time:"06:15",action:"Run water motor. CMWSSB supply window active."},
  {member:"Lakshmi",routine:"Evening Coffee",time:"17:00",action:"Start filter coffee preparation."},
  {member:"Venkat",routine:"Office Departure",time:"09:00",action:"Check traffic and ensure laptop is charged."},
  {member:"Paati",routine:"Morning Aarti",time:"05:30",action:"Pooja room ready for morning prayers."},
  {member:"Paati",routine:"Afternoon Rest",time:"13:00",action:"Minimize household noise."},
];
useEffect(()=>{
  // Request browser notification permission
  if(typeof window!=="undefined"&&"Notification"in window&&Notification.permission==="default"){Notification.requestPermission();}
  const checker=setInterval(()=>{
    const now=new Date();const hhmm=now.toLocaleTimeString("en-IN",{hour:"2-digit",minute:"2-digit",hour12:false,timeZone:"Asia/Kolkata"});
    for(const a of routineAlarms){
      const key=`${a.member}_${a.routine}_${now.toDateString()}`;
      if(a.time===hhmm&&!alarmChecked.current.has(key)){
        alarmChecked.current.add(key);
        setAlarm({name:a.member,routine:a.routine,action:a.action});
        playAlarmTone();
        // Browser notification
        if("Notification"in window&&Notification.permission==="granted"){new Notification(`GharMind AI — ${a.member}`,{body:`${a.routine}: ${a.action}`,icon:"💡"});}
        break;
      }
    }
  },5000);
  return()=>clearInterval(checker);
},[]);
function playAlarmTone(){try{const ctx=new(window.AudioContext||(window as any).webkitAudioContext)();const osc=ctx.createOscillator();const gain=ctx.createGain();osc.connect(gain);gain.connect(ctx.destination);osc.frequency.value=880;osc.type="sine";gain.gain.value=0.15;osc.start();osc.stop(ctx.currentTime+0.2);setTimeout(()=>{const o2=ctx.createOscillator();const g2=ctx.createGain();o2.connect(g2);g2.connect(ctx.destination);o2.frequency.value=1100;o2.type="sine";g2.gain.value=0.12;o2.start();o2.stop(ctx.currentTime+0.15);},250);}catch(e){}}
function dismissAlarm(){setAlarm(null);}
function snoozeAlarm(){const a=alarm;setAlarm(null);if(a)setTimeout(()=>{setAlarm(a);playAlarmTone();},300000);}
const[famDet,sFamDet]=useState<any>(null);
// Member tasks/alarms data
const memberData:Record<string,{tasks:string[];alarms:{time:string;label:string}[]}> = {
  "Lakshmi":{tasks:["Morning pooja preparation","Run water motor at 6:15 AM","Breakfast and lunch cooking","Evening coffee preparation","Coordinate household activities"],alarms:[{time:"05:45",label:"Wake up for pooja"},{time:"06:15",label:"Run water motor"},{time:"11:30",label:"Start lunch preparation"},{time:"16:45",label:"Coffee preparation"}]},
  "Venkat":{tasks:["Office commute by 9:00 AM","Ensure laptop is charged","Check household status before leaving","Evening family coordination"],alarms:[{time:"06:30",label:"Wake up"},{time:"08:45",label:"Leave for office"},{time:"13:30",label:"Charge devices (power cut risk)"}]},
  "Arjun":{tasks:["Study Physics from 8:00 PM","Keep laptop charged before power cut","Follow quiet mode during exam preparation","Complete tuition assignments"],alarms:[{time:"05:30",label:"Wake up"},{time:"13:00",label:"Download study materials (power cut prep)"},{time:"19:00",label:"Revision reminder"},{time:"20:00",label:"Exam quiet mode active"}]},
  "Paati":{tasks:["Morning aarti at 5:30 AM","Temple visit on Tuesday and Friday","Afternoon rest period","Evening prayer"],alarms:[{time:"04:30",label:"Wake up"},{time:"05:30",label:"Morning aarti"},{time:"13:00",label:"Afternoon rest"},{time:"18:00",label:"Evening prayer"}]},
};
const[gal,sGal]=useState(GAL_DATA.map((g,i)=>({id:`g${i}`,url:g.url,cap:g.cap,date:g.date,members:g.members,tag:g.tag,ai:g.ai})));const[gi,sGi]=useState("");const[galFilter,setGalFilter]=useState("All");
const[galFile,setGalFile]=useState<string|null>(null);const[galCap,setGalCap]=useState("");const[galUpOpen,setGalUpOpen]=useState(false);
const galFileRef=useRef<HTMLInputElement>(null);
function handleGalFile(e:React.ChangeEvent<HTMLInputElement>){const f=e.target.files?.[0];if(f&&f.type.startsWith("image/")){const url=URL.createObjectURL(f);setGalFile(url);setGalUpOpen(true);}}
function addGalFromFile(){if(galFile){sGal(p=>[...p,{id:`g${Date.now()}`,url:galFile,cap:galCap||"Uploaded"}]);setGalFile(null);setGalCap("");setGalUpOpen(false);}}
function delGalConfirm(id:string){if(confirm("Delete this image from gallery?")){sGal(p=>p.filter(x=>x.id!==id));}}
const[sr,sSr]=useState<any>(null);const[sl,sSl]=useState(false);const[simSc,setSimSc]=useState<string>("");
const[simP,setSimP]=useState<Record<string,string>>({});
const[cal,sCal]=useState([{i:"🎂",t:"Paati Birthday",d:"2025-01-20"},{i:"🪔",t:"Pongal",d:"2025-01-14"},{i:"📚",t:"Board Exam",d:"2025-01-26"},{i:"💧",t:"Motor",d:"Daily 6:15"},{i:"⚡",t:"Power Cut",d:"Thu 2PM"},{i:"☕",t:"Coffee",d:"Daily 5PM"}]);
const[calEdit,sCalEdit]=useState<{idx:number;t:string;d:string}|null>(null);
function getDaysLeft(d:string):string{if(d.startsWith("Daily")||d.startsWith("Thu"))return"Recurring";try{const diff=Math.ceil((new Date(d).getTime()-Date.now())/(86400000));if(diff<0)return"Passed";if(diff===0)return"Today";if(diff===1)return"Tomorrow";return`${diff} days left`;}catch{return"";}}
function saveCalEdit(){if(calEdit){sCal(p=>p.map((e,i)=>i===calEdit.idx?{...e,t:calEdit.t,d:calEdit.d}:e));sCalEdit(null);}}
// Mood/Energy profile
const moods=["Calm","Busy","Festive","Stressed","Sleeping"];const mood=moods[Math.floor(Date.now()/60000)%5];
const ePro=["Eco-Friendly","Balanced","High Consumption","Night Active"][1];

useEffect(()=>{Promise.all([getMembers(),getTwinState(),getPredictions(),getRoutines()]).then(([m,t,p,r])=>{sMs(m?.members||[]);sTw(t);sPr(p?.predictions||[]);sRt(r?.routines||[]);sFam((m?.members||[]).map((x:any,i:number)=>({...x,img:[AV.m,AV.f,AV.s,AV.p][i]||""})));sLd(false);});},[]);

const urg=tw?.urgency_score??0,tank=tw?.resources?.water?.tank_level_pct??50,pwr=tw?.resources?.power?.cut_probability??0;
const hp=Math.min(100,Math.round((tank>60?25:15)+(pwr<.3?25:10)+(urg<30?25:15)+25));

function nav(p:Pg){sP(p);sMn(false);sCo(false);setSubTab("");}
// Demo
function dStart(){sDm(true);sDi(0);setDemoNote("");}function dPause(){sDm(false);}function dRestart(){sDi(0);sDm(true);setDemoNote("");}
const[demoNote,setDemoNote]=useState("");
useEffect(()=>{if(!dm){if(dr.current)clearInterval(dr.current);return;}dr.current=setInterval(()=>{sDi(i=>{const n=i+1;if(n>=PG.length){sP("home");sDm(false);setDemoNote("Demo Complete — Returning to Home");setTimeout(()=>setDemoNote(""),3000);return 0;}sP(PG[n]);return n;});},2000);return()=>{if(dr.current)clearInterval(dr.current);};},[dm]);
// Chat
async function csend(){if(!ci.trim())return;sMsg(p=>[...p,{r:"u",t:ci.trim()}]);sCi("");sCl(true);const r=await sendChat(ci.trim());sMsg(p=>[...p,{r:"a",t:r.response||"Processing."}]);sCl(false);}
function speak(t:string){if(sp){speechSynthesis.cancel();sSp(false);return;}const u=new SpeechSynthesisUtterance(t);u.lang="en-IN";u.rate=.95;u.onend=()=>sSp(false);speechSynthesis.speak(u);sSp(true);}
const qk=[{l:"Predict Today",t:"Motor 6:15 (96%). Power cut 2 PM (76%). Quiet mode 8 PM (92%). Coffee 5 PM (93%)."},{l:"Home Status",t:"All 4 members home. Tank 42%. Power stable. Exam prep active."},{l:"Power Risk",t:"76% outage 2 PM. Charge devices by 1:30 PM. Download study materials offline."},{l:"Energy Report",t:"18% savings available. Shift washing to off-peak. Limit geyser to 15 min."},{l:"Anomaly Check",t:"Geyser running 18 min (normal 15). Auto-shutoff recommended. No other anomalies."}];
// Family
function addF(){if(!ff.name)return;sFam(p=>[...p,{id:`f${Date.now()}`,name:ff.name,role:ff.role,age:ff.age,birthday:ff.bday,img:ff.img||`https://i.pravatar.cc/60?u=${Date.now()}`}]);sff({name:"",role:"Student",age:"",bday:"",img:""});sFm(false);}
function delF(id:string){if(confirm("Remove?")){sFam(p=>p.filter(f=>f.id!==id));}}
// Sim
async function doSim(k:string){setSimSc(k);sSl(true);sSr(null);const s:any={power:{scenario_name:"Power Cut",hypothesis:"Outage 2PM",perturbations:[{type:"power_cut",params:{start_time:"14:00",duration_hours:1.5}}],sim_duration_hours:6},exam:{scenario_name:"Exam",hypothesis:"Board exam tomorrow",perturbations:[{type:"exam_week",params:{exam_type:"Board",duration_days:1}}],sim_duration_hours:12},guests:{scenario_name:"Guests",hypothesis:"6 guests 7PM",perturbations:[{type:"unexpected_guest",params:{count:6,arrival_time:"19:00",duration_hours:3}}],sim_duration_hours:6}};const r=await runSimulation(s[k]);sSr(r);sSl(false);}

if(ld)return<div className="min-h-screen flex items-center justify-center"><div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin"/></div>;

return(<div className="min-h-screen flex flex-col">
{/* ═══ TOP BAR ═══ */}
<header className="fixed top-0 inset-x-0 z-50 bg-[#080b12]/90 backdrop-blur-xl border-b border-[var(--border)] h-14">
<div className="h-full max-w-[1400px] mx-auto px-4 flex items-center">
  <button onClick={()=>setHsOpen(!hsOpen)} className="mr-2 hover:drop-shadow-[0_0_8px_rgba(34,211,238,0.5)] transition-all flex-shrink-0" title="Household Status"><svg width="30" height="30" viewBox="0 0 512 512" fill="none" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="ng" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stopColor="#22d3ee"/><stop offset="100%" stopColor="#3b82f6"/></linearGradient><linearGradient id="ng2" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stopColor="#0ea5e9"/><stop offset="100%" stopColor="#2563eb"/></linearGradient></defs><rect width="512" height="512" rx="112" fill="#0b0e14"/><path d="M256 100 L420 230 L400 230 L400 400 C400 415 388 426 374 426 L138 426 C124 426 112 415 112 400 L112 230 L92 230 Z" fill="url(#ng)" opacity="0.15"/><path d="M152 250 L152 390 C152 398 158 404 166 404 L346 404 C354 404 360 398 360 390 L360 250" fill="url(#ng)" opacity="0.25"/><path d="M256 120 L400 240" stroke="url(#ng)" strokeWidth="28" strokeLinecap="round"/><path d="M256 120 L112 240" stroke="url(#ng)" strokeWidth="28" strokeLinecap="round"/><path d="M152 240 L152 390 C152 400 160 408 170 408 L342 408 C352 408 360 400 360 390 L360 240" stroke="url(#ng)" strokeWidth="22" strokeLinecap="round" strokeLinejoin="round" fill="none"/><rect x="222" y="308" width="68" height="100" rx="12" fill="url(#ng2)" opacity="0.6"/><rect x="168" y="278" width="42" height="42" rx="8" stroke="url(#ng)" strokeWidth="10" fill="none" opacity="0.7"/><rect x="302" y="278" width="42" height="42" rx="8" stroke="url(#ng)" strokeWidth="10" fill="none" opacity="0.7"/><circle cx="256" cy="120" r="10" fill="#22d3ee"/><circle cx="256" cy="120" r="16" fill="#22d3ee" opacity="0.3"/></svg></button>
  <span className="text-lg font-bold text-grad cursor-pointer mr-4" onClick={()=>nav("home")}>GHARMIND AI</span>
  {/* Live Clock */}
  <span className="hidden sm:inline text-[13px] text-[var(--muted)]/70 font-mono mr-4 whitespace-nowrap">{clock}</span>
  {/* Nav */}
  <nav className="hidden lg:flex items-center gap-1.5 flex-1 justify-end">
    {PG.map(p=><button key={p} onClick={()=>nav(p)} className={cn("btn-g",pg===p&&"text-cyan-400 bg-cyan-500/10")}>{PL[p]}</button>)}
  </nav>
  {/* Demo */}
  <div className="hidden md:flex items-center gap-1.5 ml-4">{dm?<><button onClick={dPause} className="btn-s text-[10px] py-1.5 px-2.5">⏸ Pause</button><button onClick={dRestart} className="btn-s text-[10px] py-1.5 px-2.5">🔄</button></>:<button onClick={dStart} className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-[10px] font-bold text-white bg-gradient-to-r from-cyan-500 to-blue-500 shadow-md shadow-cyan-500/20 hover:scale-105 transition-all animate-[pulse_4s_ease-in-out_infinite]">▶ Demo Tour</button>}</div>
  {/* Hamburger */}
  <button onClick={()=>sMn(!mn)} className="lg:hidden ml-auto p-1.5 rounded hover:bg-white/5"><svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h16"/></svg></button>
</div>
</header>
{mn&&<div className="fixed inset-0 z-40 bg-black/50 lg:hidden" onClick={()=>sMn(false)}/>}
{mn&&<div className="fixed top-14 right-0 z-50 w-56 bg-[var(--card)] border-l border-[var(--border)] h-[calc(100vh-56px)] p-3 space-y-1 overflow-y-auto lg:hidden">{PG.map(p=><button key={p} onClick={()=>nav(p)} className="w-full text-left px-3 py-2.5 rounded-lg text-xs hover:bg-white/5">{PL[p]}</button>)}<div className="pt-2 border-t border-[var(--border)] mt-2">{dm?<button onClick={dPause} className="btn-s w-full text-[10px]">⏸ Pause</button>:<button onClick={dStart} className="btn-p w-full text-[10px]">▶ Demo</button>}</div></div>}

{/* ═══ MAIN ═══ */}
<main className="flex-1 pt-14 af" key={pg}>

{/* HOME */}
{pg==="home"&&<div>
{/* ── HERO ── */}
<section className="min-h-[100vh] relative flex items-center overflow-hidden">
<img src={HERO} alt="" className="absolute inset-0 w-full h-full object-cover"/>
<div className="absolute inset-0 bg-gradient-to-r from-[#080b12]/95 via-[#080b12]/75 to-[#080b12]/40"/>
<div className="absolute inset-0 bg-gradient-to-t from-[#080b12] via-transparent to-transparent opacity-60"/>
<div className="relative z-10 max-w-5xl mx-auto px-6 py-20">
  <div className="flex flex-wrap gap-2 mb-4">
    <span className="badge badge-b">✓ Powered by AWS Bedrock</span>
    <span className="badge badge-g">✓ Amazon HackOn 6.0</span>
  </div>
  <p className="text-cyan-400 text-xs font-bold tracking-[.3em] uppercase mb-3">India's First Household Digital Twin</p>
  <h1 className="text-5xl md:text-7xl font-black text-white leading-[1.05]">GHARMIND<br/><span className="text-grad">AI</span></h1>
  <p className="text-base md:text-lg text-white/60 mt-4 max-w-lg leading-[1.6]">Learns family routines, predicts needs, understands cultural context, and automates household decisions before anyone asks.</p>
  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8 max-w-lg">
    {[{v:"12",l:"Routines Learned"},{v:"89%",l:"Prediction Accuracy"},{v:"7",l:"Actions Automated"},{v:"4",l:"Members Modeled"}].map((m,i)=>(
      <div key={i} className="text-center"><p className="text-2xl md:text-3xl font-black text-cyan-400">{m.v}</p><p className="text-[11px] text-white/40 mt-0.5">{m.l}</p></div>
    ))}
  </div>
  <div className="flex flex-wrap gap-3 mt-10">
    <button onClick={()=>nav("dashboard")} className="inline-flex items-center gap-2 px-7 py-3.5 rounded-xl text-white text-sm font-bold bg-gradient-to-r from-blue-600 to-cyan-500 shadow-lg shadow-cyan-500/25 hover:scale-[1.03] transition-all">View Dashboard</button>
    <button onClick={dStart} className="inline-flex items-center gap-2 px-7 py-3.5 rounded-xl text-sm font-semibold border border-cyan-500/30 text-cyan-300 hover:bg-cyan-500/10 transition-all animate-[pulse_4s_ease-in-out_infinite]">▶ Watch AI Demo</button>
  </div>
</div>
</section>

{/* ── WHY GHARMIND EXISTS ── */}
<section className="max-w-3xl mx-auto px-6 py-20">
<div className="card-glow text-center py-12 px-8 af">
  <h2 className="text-xl md:text-2xl font-bold mb-4 uppercase tracking-wide">Our Mission</h2>
  <p className="text-base md:text-lg text-[var(--fg)]/80 leading-[1.6] max-w-2xl mx-auto">Indian homes run on routines, relationships, culture, and context. Current smart homes wait for commands. GharMind transforms household behavior into intelligence that predicts needs before anyone asks.</p>
  <p className="text-sm text-cyan-400/80 mt-6 max-w-xl mx-auto leading-[1.6] font-medium">Building the world's first AI Household Operating System that understands families, not just devices.</p>
</div>
</section>

{/* ── WHY DIFFERENT ── */}
<section className="max-w-5xl mx-auto px-6 py-20">
<h2 className="text-xl md:text-[28px] font-bold text-center mb-2">Why GharMind is Different</h2>
<p className="text-sm text-[var(--muted)] text-center mb-10">Not another smart home. A household intelligence system built for Indian families.</p>
<div className="grid md:grid-cols-2 gap-5">
  <div className="card-glow border-l-2 border-l-emerald-500/40"><p className="text-xs font-bold text-emerald-400 uppercase mb-4 tracking-wide">GharMind AI</p>{["Learns family behavior automatically","Household focused — whole family view","Predictive — acts before you ask","Indian cultural intelligence (festivals, pooja)","Adapts to your unique household","Improves from every interaction"].map((t,i)=><p key={i} className="text-sm text-emerald-300/80 py-2 border-b border-[var(--border)] last:border-0">✓ {t}</p>)}</div>
  <div className="card border-l-2 border-l-red-500/40"><p className="text-xs font-bold text-red-400 uppercase mb-4 tracking-wide">Traditional Smart Home</p>{["Waits for voice commands","Device focused only","Reactive — acts after the fact","No cultural awareness","Treats every home the same","No learning capability"].map((t,i)=><p key={i} className="text-sm text-[var(--muted)] py-2 border-b border-[var(--border)] last:border-0">✗ {t}</p>)}</div>
</div>
</section>

{/* ── TODAY GHARMIND PREDICTED ── */}
<section className="max-w-5xl mx-auto px-6 py-16">
<h2 className="text-xl md:text-[28px] font-bold text-center mb-2">Today, GharMind Predicted</h2>
<p className="text-sm text-[var(--muted)] text-center mb-8">Live predictions generated from household intelligence.</p>
<div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
  {[{p:"Arjun leaving for school in 15 minutes",c:92,cat:"family"},{p:"Water motor should run at 6:15 AM",c:96,cat:"appliance"},{p:"Evening pooja approaching at 6:00 PM",c:88,cat:"cultural"},{p:"Power outage likely at 2:00 PM",c:76,cat:"power"},{p:"Quiet Study Mode activating at 8 PM",c:91,cat:"study"},{p:"Filter coffee preparation at 5:00 PM",c:93,cat:"routine"}].map((pred,i)=>(
    <div key={i} className="card-glow af" style={{animationDelay:`${i*0.1}s`}}>
      <div className="flex justify-between items-start gap-2 mb-2"><p className="text-sm font-medium flex-1 leading-snug">{pred.p}</p><span className="text-emerald-400 font-bold text-sm">{pred.c}%</span></div>
      <div className="w-full h-1.5 rounded-full bg-[var(--border)]"><div className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-emerald-500" style={{width:`${pred.c}%`}}/></div>
    </div>
  ))}
</div>
</section>

{/* ── SUNDARAM FAMILY STORY ── */}
<section className="max-w-4xl mx-auto px-6 py-16">
<h2 className="text-xl md:text-[28px] font-bold text-center mb-2">Meet The Sundaram Family</h2>
<p className="text-sm text-[var(--muted)] text-center mb-8">A day in the life of a GharMind-powered household in Coimbatore.</p>
<div className="relative pl-7 border-l-2 border-cyan-800/40 space-y-5">
  {[{time:"6:30 AM",event:"GharMind notices Arjun waking up 10 minutes late.",icon:"⏰"},{time:"6:35 AM",event:"Predicts school departure delay risk. Confidence: 87%.",icon:"🔮"},{time:"6:36 AM",event:"Notifies Lakshmi to prepare breakfast faster.",icon:"📲"},{time:"6:45 AM",event:"Adjusts household timeline. Motor delayed 5 minutes.",icon:"⚙️"},{time:"2:00 PM",event:"Power outage detected. Devices already charged at 1:30 PM.",icon:"⚡"},{time:"8:00 PM",event:"Activates Quiet Study Mode. TV turned off. Family notified.",icon:"📚"}].map((s,i)=>(
    <div key={i} className="relative af" style={{animationDelay:`${i*0.08}s`}}>
      <span className="absolute -left-[25px] top-2 w-3.5 h-3.5 rounded-full bg-cyan-500/40 border-2 border-cyan-400"/>
      <div className="card py-3.5 px-4"><div className="flex items-center gap-3"><span className="text-lg">{s.icon}</span><span className="text-xs font-mono text-cyan-400">{s.time}</span></div><p className="text-sm text-[var(--fg)]/80 mt-1.5 leading-[1.6]">{s.event}</p></div>
    </div>
  ))}
</div>
</section>

{/* ── HOW GHARMIND THINKS ── */}
<section className="max-w-3xl mx-auto px-6 py-16">
<h2 className="text-xl md:text-[28px] font-bold text-center mb-8">How GharMind Thinks</h2>
<div className="space-y-0">
  {[{icon:"👨‍👩‍👧‍👦",label:"Family Activity Data",sub:"Schedules, appliances, routines"},{icon:"🧠",label:"Routine Learning Engine",sub:"Detects patterns across days and weeks"},{icon:"🏠",label:"Household Digital Twin",sub:"Real-time simulation of home state"},{icon:"🔮",label:"Prediction Engine",sub:"Forecasts next actions with confidence"},{icon:"💡",label:"Explainable AI Layer",sub:"Shows why every decision was made"},{icon:"⚡",label:"Recommendations & Actions",sub:"Proactive household automation"}].map((s,i)=>(
    <div key={i} className="flex items-center gap-4 py-4 border-b border-[var(--border)] last:border-0">
      <span className="text-2xl w-11 text-center">{s.icon}</span>
      <div className="flex-1"><p className="text-sm font-semibold">{s.label}</p><p className="text-xs text-[var(--muted)] mt-0.5">{s.sub}</p></div>
    </div>
  ))}
</div>
</section>

{/* ── CTA ── */}
<section className="max-w-3xl mx-auto px-6 py-20 pb-24">
<div className="text-center mb-10">
  <h2 className="text-xl md:text-[28px] font-bold mb-3">Experience GharMind AI</h2>
  <p className="text-sm text-[var(--muted)]">Explore the intelligence that powers a smarter household.</p>
</div>
<div className="flex flex-wrap justify-center gap-4">
  <button onClick={()=>nav("dashboard")} className="inline-flex items-center gap-2 px-7 py-3.5 rounded-xl text-white text-sm font-bold bg-gradient-to-r from-blue-600 to-cyan-500 shadow-lg shadow-cyan-500/25 hover:scale-[1.03] transition-all">Explore Dashboard</button>
  <button onClick={()=>nav("predictions")} className="inline-flex items-center gap-2 px-7 py-3.5 rounded-xl text-sm font-semibold border border-cyan-500/30 text-cyan-300 hover:bg-cyan-500/10 transition-all">View Predictions</button>
  <button onClick={()=>nav("howitworks")} className="inline-flex items-center gap-2 px-7 py-3.5 rounded-xl text-sm font-semibold border border-emerald-500/30 text-emerald-300 hover:bg-emerald-500/10 transition-all">See How It Works</button>
</div>
</section>


</div>}

{/* DASHBOARD */}
{pg==="dashboard"&&<div className="max-w-5xl mx-auto px-5 py-8 space-y-6">

{/* ── HIGH IMPACT BANNER ── */}
{pwr>.6&&<div className="rounded-2xl border border-amber-500/30 bg-amber-500/5 px-5 py-4 flex items-center gap-4 shadow-lg shadow-amber-900/10">
  <span className="text-xl">⚠️</span>
  <div className="flex-1"><p className="text-sm font-bold text-amber-400">HIGH IMPACT EVENT TODAY</p><p className="text-xs text-[var(--muted)] mt-0.5">Power outage expected at 2 PM. Recommended actions generated.</p></div>
  <span className="badge badge-a">Action Required</span>
</div>}

{/* ── TOP METRICS ── */}
<div className="grid grid-cols-2 md:grid-cols-4 gap-4">
  <div className="card text-center py-6"><span className="text-2xl">❤️</span><p className="text-3xl font-black text-emerald-400 mt-2">{hp}</p><p className="text-xs text-[var(--muted)] mt-1">Health Score</p></div>
  <div className="card text-center py-6"><span className="text-2xl">💧</span><p className="text-3xl font-black text-cyan-400 mt-2">{tank}%</p><p className="text-xs text-[var(--muted)] mt-1">Water Status</p></div>
  <div className="card text-center py-6"><span className="text-2xl">⚡</span><p className={cn("text-3xl font-black mt-2",pwr>.6?"text-amber-400":"text-emerald-400")}>{Math.round(pwr*100)}%</p><p className="text-xs text-[var(--muted)] mt-1">Power Risk</p></div>
  <div className="card text-center py-6"><span className="text-2xl">📅</span><p className="text-2xl font-black text-purple-400 mt-2">Board Exam</p><p className="text-xs text-[var(--muted)] mt-1">Tomorrow</p></div>
</div>

{/* ── AI RECOMMENDATION HERO CARD ── */}
<div className="card-glow border-l-4 border-l-cyan-500/60 py-6 px-6 shadow-lg shadow-cyan-900/10">
  <p className="text-xs font-bold text-cyan-400 uppercase tracking-wide mb-1">Today's AI Recommendation</p>
  <h3 className="text-lg md:text-xl font-bold mt-2">Power Outage Expected at 2 PM</h3>
  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-5">
    <div><p className="text-[11px] text-[var(--muted)] uppercase tracking-wide font-medium">Recommended Action</p><p className="text-sm font-medium mt-1">Charge Arjun's laptop before 1:30 PM</p></div>
    <div><p className="text-[11px] text-[var(--muted)] uppercase tracking-wide font-medium">Expected Impact</p><p className="text-sm font-medium mt-1 text-emerald-400">Avoid study disruption</p></div>
    <div><p className="text-[11px] text-[var(--muted)] uppercase tracking-wide font-medium">Reason</p><p className="text-sm font-medium mt-1">76% outage probability from learned patterns</p></div>
    <div><p className="text-[11px] text-[var(--muted)] uppercase tracking-wide font-medium">Confidence</p><p className="text-2xl font-black text-cyan-400 mt-1">96%</p></div>
  </div>
</div>

{/* ── THREE-COLUMN INTELLIGENCE ── */}
<div className="grid lg:grid-cols-3 gap-5">
  {/* LEFT — Next Actions */}
  <div className="card">
    <p className="text-xs font-bold text-cyan-400 uppercase tracking-wide mb-4">Next Action Predictions</p>
    <div className="space-y-3">
      {NEXT_HOUR_PREDICTIONS.slice(0,3).map((p,i)=><div key={i} className="flex items-start gap-3 py-2 border-b border-[var(--border)] last:border-0">
        <span className="text-emerald-400 font-bold text-sm w-10 flex-shrink-0 pt-0.5">{Math.round(p.confidence*100)}%</span>
        <div className="flex-1"><p className="text-sm font-medium">{p.action}</p><p className="text-xs text-[var(--muted)] mt-0.5">{p.explanation}</p></div>
      </div>)}
    </div>
    <button onClick={()=>nav("predictions")} className="text-xs text-cyan-400 font-medium mt-4 hover:underline">View All Predictions →</button>
  </div>

  {/* CENTER — Live Digital Twin */}
  <div className="card">
    <div className="flex items-center gap-2 mb-4"><span className="w-2 h-2 bg-emerald-400 rounded-full ap"/><p className="text-xs font-bold uppercase tracking-wide">Live Digital Twin</p></div>
    <div className="space-y-3">
      {[{name:"Lakshmi",loc:"Kitchen",color:"bg-emerald-400",dot:"🟢"},{name:"Venkat",loc:"Bedroom",color:"bg-amber-400",dot:"🟡"},{name:"Arjun",loc:"Study Room",color:"bg-emerald-400",dot:"🟢"},{name:"Paati",loc:"Pooja Room",color:"bg-blue-400",dot:"🔵"}].map((m,i)=><div key={i} className="flex items-center gap-3 py-2.5 border-b border-[var(--border)] last:border-0">
        <img src={fam[i]?.img||""} alt="" className="w-8 h-8 rounded-full object-cover border border-[var(--border)]"/>
        <div className="flex-1"><p className="text-sm font-medium">{m.name}</p></div>
        <div className="flex items-center gap-1.5"><span className={cn("w-2 h-2 rounded-full",m.color)}/><span className="text-xs text-[var(--muted)]">{m.loc}</span></div>
      </div>)}
    </div>
  </div>

  {/* RIGHT — Household Context */}
  <div className="card">
    <p className="text-xs font-bold text-cyan-400 uppercase tracking-wide mb-4">Household Context</p>
    <div className="space-y-4">
      <div className="flex items-center justify-between"><span className="text-sm">⚡ Power Risk</span><span className={cn("text-sm font-bold",pwr>.6?"text-amber-400":"text-emerald-400")}>{POWER_CUT_INTEL.probability}% at {POWER_CUT_INTEL.expectedTime}</span></div>
      <div className="flex items-center justify-between"><span className="text-sm">💡 Savings Opportunity</span><span className="text-sm font-bold text-emerald-400">↓{ENERGY_INSIGHTS.estimatedSavings}%</span></div>
      <div className="pt-3 border-t border-[var(--border)]">
        <p className="text-sm font-medium">🪔 {CULTURAL_CONTEXT.festivalName}</p>
        <p className="text-xs text-[var(--muted)] mt-0.5">{CULTURAL_CONTEXT.daysAway} days away</p>
        <div className="mt-2 space-y-1">
          <p className="text-xs text-emerald-400">✓ Family gathering reminder</p>
          <p className="text-xs text-emerald-400">✓ Traditional cooking preparation</p>
          <p className="text-xs text-emerald-400">✓ Schedule adjustments</p>
        </div>
      </div>
    </div>
  </div>
</div>

{/* ── HOUSEHOLD TIMELINE ── */}
<div className="card">
  <p className="text-xs font-bold text-cyan-400 uppercase tracking-wide mb-4">Today's Household Timeline</p>
  <div className="flex flex-wrap gap-0">
    {[{t:"5:30 AM",e:"Pooja Started",i:"🙏",c:"text-purple-400"},{t:"6:00 AM",e:"Breakfast Prep",i:"🍳",c:"text-emerald-400"},{t:"6:15 AM",e:"Water Motor",i:"💧",c:"text-cyan-400"},{t:"7:15 AM",e:"School Prep",i:"📚",c:"text-amber-400"},{t:"2:00 PM",e:"Power Cut",i:"⚡",c:"text-red-400"},{t:"5:00 PM",e:"Evening Coffee",i:"☕",c:"text-amber-400"},{t:"8:00 PM",e:"Quiet Hours",i:"🤫",c:"text-purple-400"}].map((ev,i)=><div key={i} className="flex-1 min-w-[100px] text-center py-3 border-r border-[var(--border)] last:border-r-0">
      <span className="text-lg">{ev.i}</span>
      <p className={cn("text-xs font-medium mt-1",ev.c)}>{ev.e}</p>
      <p className="text-[11px] text-[var(--muted)] mt-0.5">{ev.t}</p>
    </div>)}
  </div>
</div>

{/* ── SAFETY MONITORING ── */}
<div className="card">
  <p className="text-xs font-bold text-amber-400 uppercase tracking-wide mb-3">Safety Monitoring</p>
  <div className="grid md:grid-cols-3 gap-3">{SAFETY_ALERTS.map(a=><div key={a.id} className="flex flex-col gap-1 py-2 px-3 rounded-lg bg-[var(--bg)]"><p className="text-sm font-medium">{a.appliance}</p><p className="text-xs text-[var(--muted)]">{a.reason}</p><p className="text-xs text-emerald-400 font-medium">→ {a.action}</p></div>)}</div>
</div>

</div>}

{/* FAMILY */}
{pg==="family"&&<div className="max-w-4xl mx-auto px-4 py-6 space-y-4"><div className="flex justify-between items-center"><h2 className="text-base font-bold">Family Members</h2><button onClick={()=>sFm(true)} className="btn-p text-[10px]">+ Add</button></div>
<div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">{fam.map((m:any,i:number)=><div key={m.id||i} onClick={()=>sFamDet(m)} className="card text-center relative group cursor-pointer hover:border-cyan-800/50 transition-all"><img src={m.img||""} alt="" className="w-12 h-12 mx-auto rounded-full object-cover border border-cyan-900/40"/><p className="text-xs font-semibold mt-2">{m.name}</p><p className="text-[10px] text-muted">{m.role}{m.age?` • Age ${m.age}`:""}</p>{m.birthday&&<p className="text-[10px] text-cyan-400 mt-0.5">🎂 {m.birthday}</p>}<button onClick={(e)=>{e.stopPropagation();delF(m.id);}} className="absolute top-2 right-2 w-5 h-5 rounded bg-red-500/20 text-red-400 text-[10px] opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">✕</button></div>)}</div>
<p className="text-[11px] text-muted text-center">Click a member to view their Personal Digital Twin.</p>

{/* ── PERSONAL DIGITAL TWIN PANEL ── */}
{famDet&&<div className="card-glow af space-y-4 mt-2">
  {/* Header */}
  <div className="flex items-center gap-3 pb-3 border-b border-[var(--border)]">
    <img src={famDet.img||""} alt="" className="w-14 h-14 rounded-full object-cover border-2 border-cyan-800/40"/>
    <div className="flex-1">
      <p className="text-base font-bold">{famDet.name}</p>
      <p className="text-xs text-cyan-400">{famDet.role||"Member"}{famDet.age?` • Age ${famDet.age}`:""}</p>
      {famDet.birthday&&<p className="text-[10px] text-muted">Birthday: {famDet.birthday}</p>}
    </div>
    <button onClick={()=>sFamDet(null)} className="btn-s text-[9px] py-1 px-2">Close</button>
  </div>

  {/* Current Status */}
  <div className="card"><p className="text-[9px] font-bold text-cyan-400 uppercase mb-1.5">Current Status</p>
    <p className="text-sm font-medium">{famDet.name==="Lakshmi"?"🟢 Cooking Preparation Active":famDet.name==="Venkat"?"🟡 Leaving for Office Soon":famDet.name==="Arjun"?"📚 Study Session Expected":famDet.name==="Paati"?"🙏 Morning Prayer Routine Active":"🟢 At Home"}</p>
  </div>

  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
    {/* AI Insights */}
    <div className="card"><p className="text-[9px] font-bold text-purple-400 uppercase mb-2">AI Insights</p><div className="space-y-1">
      {(famDet.name==="Arjun"?["Most productive study hours: 8 PM – 10 PM","Average sleep time: 11:15 PM","Exam preparation mode detected","Frequently uses laptop before exams"]:famDet.name==="Lakshmi"?["Breakfast preparation starts around 6 AM","Water motor monitoring routine detected","Grocery planning behavior observed","Evening cooking peaks at 6:30 PM"]:famDet.name==="Venkat"?["Office departure typically at 8:50 AM","Laptop usage peaks during work hours","Meeting readiness pattern detected","Weekend relaxation mode observed"]:["Morning prayer routine at 5:45 AM","Afternoon rest period consistent","Temple visits on Tuesday and Friday","Early sleep pattern maintained"]).map((ins,i)=><p key={i} className="text-[10px] text-emerald-400">✓ {ins}</p>)}
    </div></div>

    {/* Mood Detection */}
    <div className="card"><p className="text-[9px] font-bold text-amber-400 uppercase mb-2">Mood Detection</p>
      <p className="text-lg">{famDet.name==="Arjun"?"📚 Focused":famDet.name==="Lakshmi"?"💼 Busy":famDet.name==="Venkat"?"😊 Calm":"🙏 Peaceful"}</p>
      <p className="text-[10px] text-muted mt-1">Reason: {famDet.name==="Arjun"?"Exam scheduled tomorrow and study activity increased by 35%.":famDet.name==="Lakshmi"?"Multiple household tasks active simultaneously.":famDet.name==="Venkat"?"Regular schedule maintained, no anomalies.":"Daily prayer routine completed on time."}</p>
    </div>
  </div>

  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
    {/* Today's Tasks */}
    <div className="card"><p className="text-[9px] font-bold text-emerald-400 uppercase mb-2">Today's Tasks</p><div className="space-y-1.5">
      {(memberData[famDet.name]?.tasks||["No tasks assigned"]).map((t:string,i:number)=><label key={i} className="flex items-center gap-2 cursor-pointer"><input type="checkbox" className="rounded border-[var(--border)] accent-cyan-500 w-3.5 h-3.5"/><span className="text-[10px]">{t}</span></label>)}
    </div></div>

    {/* Upcoming Alarms */}
    <div className="card"><p className="text-[9px] font-bold text-amber-400 uppercase mb-2">Upcoming Alarms</p><div className="space-y-1.5">
      {(memberData[famDet.name]?.alarms||[{time:"--:--",label:"No alarms"}]).map((a:{time:string;label:string},i:number)=><div key={i} className="flex items-center gap-2 py-1 border-b border-[var(--border)] last:border-0"><span className="text-amber-400 text-[10px]">🔔</span><span className="text-[10px] font-mono text-amber-400 w-12">{a.time}</span><span className="text-[10px] flex-1">{a.label}</span></div>)}
    </div></div>
  </div>

  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
    {/* Routine Adherence */}
    <div className="card text-center"><p className="text-[9px] font-bold text-cyan-400 uppercase mb-2">Routine Adherence</p>
      <p className="text-2xl font-black text-cyan-400">{famDet.name==="Lakshmi"?"92%":famDet.name==="Venkat"?"87%":famDet.name==="Arjun"?"89%":"95%"}</p>
      <p className="text-[9px] text-muted mt-1">Following regular schedule for the past 7 days.</p>
    </div>

    {/* Next Action Predictions */}
    <div className="card"><p className="text-[9px] font-bold text-cyan-400 uppercase mb-2">Predicted Next Actions</p><div className="space-y-1.5">
      {(famDet.name==="Arjun"?[{c:91,a:"Start Study Session",r:"Exam tomorrow, pattern detected on 42 similar days"},{c:85,a:"Prepare School Bag",r:"Usually occurs 20 min before bedtime"}]:famDet.name==="Lakshmi"?[{c:96,a:"Run Water Motor",r:"Tank at 42%, CMWSSB supply window active"},{c:88,a:"Begin Cooking",r:"Evening meal preparation pattern"}]:famDet.name==="Venkat"?[{c:94,a:"Leave for Office",r:"Weekday commute pattern, 8:50 AM avg"},{c:82,a:"Charge Laptop",r:"Low battery detected in similar past scenarios"}]:[{c:97,a:"Morning Aarti",r:"Daily at 5:45 AM, 97% consistency"},{c:90,a:"Afternoon Rest",r:"13:00 rest pattern confirmed"}]).map((p,i)=><div key={i} className="py-1 border-b border-[var(--border)] last:border-0"><div className="flex gap-2"><span className="text-emerald-400 font-bold text-[10px]">{p.c}%</span><span className="text-[10px] font-medium">{p.a}</span></div><p className="text-[9px] text-muted ml-8">{p.r}</p></div>)}
    </div></div>
  </div>

  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
    {/* Memory Insights */}
    <div className="card"><p className="text-[9px] font-bold text-purple-400 uppercase mb-2">30-Day Memory Insights</p><div className="space-y-1">
      {(famDet.name==="Arjun"?["Studies most effectively between 8 PM and 10 PM","Screen time increases before exams","Sleep delay averages 14 min during exam weeks","Prefers quiet environment for revision"]:famDet.name==="Lakshmi"?["Starts breakfast preparation at 6 AM on 92% of days","Water motor usage peaks on weekdays","Grocery planning happens every Sunday","Evening cooking starts at 6:30 PM consistently"]:famDet.name==="Venkat"?["Leaves for work at approximately 8:50 AM","Laptop usage peaks during morning hours","Weekend activity significantly different","Prefers chai at 5 PM daily"]:["Performs pooja daily around 5:45 AM","Afternoon nap from 1 PM to 2:30 PM","Temple visits on Tuesday and Friday","Sleeps by 9 PM consistently"]).map((m,i)=><p key={i} className="text-[10px] text-muted">✓ {m}</p>)}
    </div></div>

    {/* Daily Timeline */}
    <div className="card"><p className="text-[9px] font-bold text-cyan-400 uppercase mb-2">Today's Personal Timeline</p><div className="space-y-1">
      {(famDet.name==="Arjun"?[{t:"6:30 AM",e:"Wake Up"},{t:"7:15 AM",e:"School Prep"},{t:"8:00 AM",e:"School"},{t:"3:30 PM",e:"Return"},{t:"5:00 PM",e:"Tuition"},{t:"8:00 PM",e:"Study Session"},{t:"10:30 PM",e:"Sleep"}]:famDet.name==="Lakshmi"?[{t:"5:45 AM",e:"Wake Up"},{t:"6:00 AM",e:"Pooja"},{t:"6:15 AM",e:"Water Motor"},{t:"6:30 AM",e:"Breakfast"},{t:"11:30 AM",e:"Lunch Prep"},{t:"5:00 PM",e:"Coffee"},{t:"6:30 PM",e:"Dinner Prep"}]:famDet.name==="Venkat"?[{t:"6:30 AM",e:"Wake Up"},{t:"7:30 AM",e:"Ready"},{t:"8:50 AM",e:"Office"},{t:"6:00 PM",e:"Return"},{t:"8:00 PM",e:"Dinner"},{t:"10:00 PM",e:"Relax"},{t:"11:00 PM",e:"Sleep"}]:[{t:"4:30 AM",e:"Wake Up"},{t:"5:30 AM",e:"Aarti"},{t:"7:00 AM",e:"Breakfast"},{t:"10:00 AM",e:"Rest"},{t:"1:00 PM",e:"Nap"},{t:"5:00 PM",e:"Evening Prayer"},{t:"9:00 PM",e:"Sleep"}]).map((ev,i)=><div key={i} className="flex gap-2 py-0.5"><span className="text-[9px] font-mono text-cyan-400 w-14">{ev.t}</span><span className="text-[10px]">{ev.e}</span></div>)}
    </div></div>
  </div>

  {/* Household Contribution */}
  <div className="card"><p className="text-[9px] font-bold text-emerald-400 uppercase mb-2">Household Contribution</p>
    <div className="space-y-1.5">{[{n:"Lakshmi",p:35},{n:"Venkat",p:25},{n:"Arjun",p:20},{n:"Paati",p:20}].map((c,i)=><div key={i} className="flex items-center gap-2"><span className="text-[10px] w-16">{c.n}</span><div className="flex-1 h-2 rounded-full bg-[var(--border)] overflow-hidden"><div className={cn("h-full rounded-full",c.n===famDet.name?"bg-cyan-500":"bg-cyan-500/30")} style={{width:`${c.p}%`}}/></div><span className="text-[9px] text-muted w-8 text-right">{c.p}%</span></div>)}</div>
  </div>
</div>}

{/* Add Member Modal */}
{fm&&<div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" onClick={()=>sFm(false)}><div className="bg-[var(--card)] rounded-2xl p-5 w-full max-w-xs md:max-w-sm border border-[var(--border)] space-y-2.5 max-h-[90vh] overflow-y-auto" onClick={e=>e.stopPropagation()}><h3 className="text-sm font-bold">Add Member</h3><input placeholder="Name" value={ff.name} onChange={e=>sff(f=>({...f,name:e.target.value}))} className="w-full px-3 py-2 rounded-lg bg-[var(--bg)] border border-[var(--border)] text-xs"/><select value={ff.role} onChange={e=>sff(f=>({...f,role:e.target.value}))} className="w-full px-3 py-2 rounded-lg bg-[var(--bg)] border border-[var(--border)] text-xs">{["Student","Professional","Homemaker","Elderly","Child"].map(r=><option key={r}>{r}</option>)}</select><div className="grid grid-cols-2 gap-2"><input placeholder="Age" type="number" value={ff.age} onChange={e=>sff(f=>({...f,age:e.target.value}))} className="px-3 py-2 rounded-lg bg-[var(--bg)] border border-[var(--border)] text-xs"/><input type="date" value={ff.bday} onChange={e=>sff(f=>({...f,bday:e.target.value}))} className="px-3 py-2 rounded-lg bg-[var(--bg)] border border-[var(--border)] text-xs"/></div><input placeholder="Image URL" value={ff.img} onChange={e=>sff(f=>({...f,img:e.target.value}))} className="w-full px-3 py-2 rounded-lg bg-[var(--bg)] border border-[var(--border)] text-xs"/><div className="flex gap-2"><button onClick={addF} className="btn-p flex-1 text-[10px]">Save</button><button onClick={()=>sFm(false)} className="btn-s flex-1 text-[10px]">Cancel</button></div></div></div>}

{/* Calendar merged into Family */}
<h3 className="text-sm font-bold mt-4">📅 Family Events & Calendar</h3>
<div className="space-y-2">{cal.map((e,i)=><div key={i} className="card flex items-center gap-3"><span className="text-lg">{e.i}</span><div className="flex-1"><p className="text-xs font-medium">{e.t}</p><p className="text-[10px] text-muted">{e.d}</p></div><span className="text-[9px] text-cyan-400 font-medium">{getDaysLeft(e.d)}</span><button onClick={()=>sCalEdit({idx:i,t:e.t,d:e.d})} className="text-[10px] px-2 py-1 rounded bg-white/5 border border-[var(--border)] hover:bg-white/10 transition-all">✏️</button></div>)}</div>
{calEdit&&<div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" onClick={()=>sCalEdit(null)}><div className="bg-[var(--card)] rounded-2xl p-5 w-full max-w-xs border border-[var(--border)] space-y-3" onClick={ev=>ev.stopPropagation()}><h3 className="text-sm font-bold">Edit Event</h3><div><label className="text-[9px] text-muted">Title</label><input value={calEdit.t} onChange={ev=>sCalEdit({...calEdit,t:ev.target.value})} className="w-full px-3 py-2 rounded-lg bg-[var(--bg)] border border-[var(--border)] text-xs mt-0.5"/></div><div><label className="text-[9px] text-muted">Date / Frequency</label><input value={calEdit.d} onChange={ev=>sCalEdit({...calEdit,d:ev.target.value})} className="w-full px-3 py-2 rounded-lg bg-[var(--bg)] border border-[var(--border)] text-xs mt-0.5" placeholder="2025-01-20 or Daily 6:15"/></div><p className="text-[9px] text-cyan-400">{getDaysLeft(calEdit.d)}</p><div className="flex gap-2"><button onClick={saveCalEdit} className="btn-p flex-1 text-[10px]">Save</button><button onClick={()=>sCalEdit(null)} className="btn-s flex-1 text-[10px]">Cancel</button></div></div></div>}
</div>}

{/* PREDICTIONS */}
{pg==="predictions"&&(subTab===""||subTab==="predictions")&&<div className="max-w-4xl mx-auto px-4 py-6 space-y-4">

{/* Tabs */}
<div className="flex gap-2 mb-2">{[{k:"predictions",l:"🔮 Predictions"},{k:"whatif",l:"🧪 What-If Simulator"}].map(t=><button key={t.k} onClick={()=>setSubTab(t.k)} className={cn("btn-g px-3 py-1.5",(!subTab||subTab===t.k)&&t.k==="predictions"?"text-cyan-400 bg-cyan-500/10":subTab===t.k?"text-cyan-400 bg-cyan-500/10":"")}>{t.l}</button>)}</div>

{/* ── 10. AI BUTLER NARRATIVE ── */}
<div className="card-glow border-l-2 border-l-cyan-500/50 py-3">
  <p className="text-[10px] text-cyan-400 font-medium">Good Evening.</p>
  <p className="text-xs mt-1">GharMind has detected elevated household activity due to tomorrow's exam. The most important action today is charging devices before the predicted 2 PM outage. Three routine events and one risk event require attention.</p>
</div>

{/* ── 4. DIGITAL TWIN SUMMARY ── */}
<div className="card"><p className="text-[9px] font-bold text-cyan-400 uppercase mb-2">Current Household State</p>
<div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2 text-center">{[{l:"Mood",v:"Focused",c:"text-purple-400"},{l:"Energy",v:"Moderate",c:"text-amber-400"},{l:"Water",v:"42%",c:"text-cyan-400"},{l:"Power Risk",v:"76%",c:"text-red-400"},{l:"Events Today",v:"5",c:"text-emerald-400"},{l:"Harmony",v:"92%",c:"text-cyan-400"}].map((s,i)=><div key={i}><p className={cn("text-sm font-bold",s.c)}>{s.v}</p><p className="text-[8px] text-muted">{s.l}</p></div>)}</div>
<p className="text-[9px] text-muted mt-2">Reason: Board exam tomorrow. Study activity elevated.</p>
</div>

{/* ── 3. NEXT 12 HOURS TIMELINE ── */}
<div className="card"><p className="text-[9px] font-bold text-cyan-400 uppercase mb-2">Next 12 Hours</p>
<div className="flex gap-1.5 overflow-x-auto pb-1">{[{t:"6:15",e:"💧 Motor"},{t:"8:00",e:"🎒 School"},{t:"14:00",e:"⚡ Outage"},{t:"17:00",e:"☕ Coffee"},{t:"18:00",e:"📚 Tuition"},{t:"20:00",e:"🔇 Quiet"},{t:"22:00",e:"😴 Rest"}].map((x,i)=><div key={i} className="flex-shrink-0 text-center"><div className="w-10 h-10 rounded-full border border-cyan-800/40 flex items-center justify-center text-sm bg-cyan-500/5">{x.e.split(" ")[0]}</div><p className="text-[8px] text-muted mt-1">{x.t}</p><p className="text-[7px]">{x.e.split(" ")[1]}</p></div>)}</div>
</div>

{/* ── 6. PREDICTION ENGINE PERFORMANCE ── */}
<div className="grid grid-cols-2 md:grid-cols-4 gap-2">
  {[{v:"89%",l:"Accuracy (30d)",c:"text-emerald-400"},{v:"267",l:"Successful",c:"text-cyan-400"},{v:"31",l:"Missed",c:"text-amber-400"},{v:"+12%",l:"Improvement",c:"text-emerald-400"}].map((s,i)=><div key={i} className="card text-center py-2"><p className={cn("text-base font-bold",s.c)}>{s.v}</p><p className="text-[8px] text-muted">{s.l}</p></div>)}
</div>

<h2 className="text-base font-bold">Predictions</h2>

{/* ── PREDICTION CARDS (enhanced) ── */}
{pr.map((p:any,i:number)=><div key={i} className="card-glow space-y-2">
  {/* Existing: title + suggestion + badge */}
  <div className="flex gap-2"><div className="flex-1"><p className="text-xs font-semibold">{p.title}</p><p className="text-[11px] text-muted mt-0.5">{p.action_suggestion}</p></div><span className={cn("badge",p.priority==="critical"?"badge-r":p.priority==="high"?"badge-a":"badge-b")}>{Math.round(p.confidence*100)}%</span></div>

  {/* 5. Confidence Bar */}
  <div className="w-full h-1.5 rounded-full bg-[var(--border)]"><div className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-emerald-500 transition-all" style={{width:`${Math.round(p.confidence*100)}%`}}/></div>

  {/* 1. Explainable AI (enhanced) */}
  <details className="mt-1"><summary className="text-[10px] text-cyan-400 cursor-pointer">Explainable AI — View reasoning</summary><div className="mt-2 pl-2 border-l border-cyan-800/40 space-y-2">
    <div><p className="text-[9px] font-bold text-cyan-400 uppercase">Evidence</p><div className="space-y-0.5 mt-1">{(p.category==="water"?["Tank level reached 42%","Municipal supply window closes at 6:45 AM","Similar action occurred on 31 of last 35 days","Household consumption indicates shortage before noon"]:p.category==="power"?["TNEB Thursday load-shedding pattern","Confirmed in 5 of last 7 weeks","Zone C2 historical outage data","Duration: 60-90 minutes typical"]:["Historical routine detected on similar days","Calendar context: exam tomorrow","Behavioral consistency score: high","Time-of-day pattern match"]).map((e,j)=><p key={j} className="text-[10px] text-emerald-400">✓ {e}</p>)}</div></div>
    <div><p className="text-[9px] font-bold text-purple-400 uppercase">Contributing Factors</p><p className="text-[10px] text-muted mt-0.5">Time Context • Historical Routine • Resource Availability • Household Behavior Pattern</p></div>
    <div><p className="text-[9px] font-bold text-emerald-400 uppercase">Expected Outcome</p><p className="text-[10px] text-muted mt-0.5">{p.category==="water"?"Avoid water shortage and emergency motor usage.":p.category==="power"?"Minimize disruption from power outage.":"Maintain optimal household schedule."}</p></div>
  </div></details>

  {/* 2. Impact Analysis */}
  <details><summary className="text-[10px] text-amber-400 cursor-pointer">Impact Analysis</summary><div className="mt-2 pl-2 border-l border-amber-800/40">
    <p className="text-[9px]">Severity: <span className={cn("font-bold",p.priority==="critical"?"text-red-400":"text-amber-400")}>{p.priority==="critical"?"HIGH":"MEDIUM"}</span></p>
    <div className="mt-1"><p className="text-[9px] text-emerald-400">Benefits:</p>{(p.category==="water"?["Prevents water shortage","Avoids emergency appliance usage","Improves household efficiency"]:p.category==="power"?["Protects devices from damage","Ensures study continuity","Reduces stress"]:["Maintains routine consistency","Supports exam preparation","Reduces household disruption"]).map((b,j)=><p key={j} className="text-[10px] text-muted">✓ {b}</p>)}</div>
    <p className="text-[9px] text-muted mt-1">Affected: {p.category==="water"?"Water System • Schedule • Energy":p.category==="power"?"Power • Devices • Study":"Routine • Family • Comfort"}</p>
  </div></details>

  {/* 8. What Happens If Ignored */}
  <details><summary className="text-[10px] text-red-400 cursor-pointer">What happens if ignored?</summary><div className="mt-2 pl-2 border-l border-red-800/40">
    <p className="text-[10px] text-muted">{p.category==="water"?"Water level likely drops below 20%. Emergency motor activation required. Higher electricity usage.":p.category==="power"?"Devices may lose charge mid-use. Study session interrupted. WiFi disconnection.":"Routine disruption cascade. Schedule delays propagate to next events."}</p>
    <p className="text-[10px] text-red-400 mt-1 font-medium">Risk Increase: {p.category==="water"?"+67%":p.category==="power"?"+54%":"+38%"}</p>
  </div></details>

  {/* 11. Workflow (compact) */}
  <div className="flex items-center gap-1 text-[8px] text-muted pt-1 border-t border-[var(--border)]">
    <span className="text-cyan-400">Prediction</span><span>→</span><span>Reason</span><span>→</span><span>Impact</span><span>→</span><span className="text-red-400">If Ignored</span><span>→</span><span className="text-emerald-400">{Math.round(p.confidence*100)}%</span>
  </div>
</div>)}

{/* ── 9. PREDICTION RELATIONSHIP GRAPH ── */}
<div className="card"><p className="text-[9px] font-bold text-cyan-400 uppercase mb-2">Prediction Dependencies</p>
<div className="space-y-1">{[{from:"Power Cut at 2 PM",to:"Charge Devices by 1:30 PM"},{from:"Charge Devices",to:"Exam Quiet Mode at 8 PM"},{from:"Exam Quiet Mode",to:"Study Session Continuity"},{from:"Water Motor at 6:15",to:"Morning Routine Stability"}].map((r,i)=><div key={i} className="flex items-center gap-2 text-[10px]"><span className="text-cyan-400">{r.from}</span><span className="text-muted">→</span><span className="text-emerald-400">{r.to}</span></div>)}</div>
</div>

{/* ── 7. SELF-LEARNING AI ── */}
<div className="card"><p className="text-[9px] font-bold text-purple-400 uppercase mb-2">Adaptive Learning</p>
<div className="space-y-1.5">
  <div className="py-1.5 border-b border-[var(--border)]"><p className="text-[10px] text-muted">Yesterday: Prediction <span className="text-red-400">Rejected</span></p><p className="text-[10px]">AI shifted water motor recommendation from 6:00 AM to 6:15 AM</p></div>
  <div className="py-1.5"><p className="text-[10px] text-muted">Today: Recommendation <span className="text-emerald-400">Accepted</span></p><p className="text-[10px] text-emerald-400">✓ Successfully Adapted</p></div>
</div>
</div>

</div>}

{/* WHAT-IF (merged into predictions page via tab) */}
{pg==="predictions"&&subTab==="whatif"&&<div className="max-w-4xl mx-auto px-4 py-6 space-y-4">

{/* Tabs */}
<div className="flex gap-2 mb-2">{[{k:"predictions",l:"🔮 Predictions"},{k:"whatif",l:"🧪 What-If Simulator"}].map(t=><button key={t.k} onClick={()=>setSubTab(t.k==="predictions"?"":t.k)} className={cn("btn-g px-3 py-1.5",subTab===t.k?"text-cyan-400 bg-cyan-500/10":"")}>{t.l}</button>)}</div>

{/* ── 12. AI BUTLER SUMMARY ── */}
<div className="card-glow border-l-2 border-l-cyan-500/50 py-3">
  <p className="text-[10px] text-cyan-400 font-medium">Household Butler AI</p>
  <p className="text-xs mt-1">A 2 PM power outage is expected. If preventive actions are taken, disruption can be reduced by 58%. The most affected activity will be Arjun's study session. Recommended actions have been generated.</p>
</div>

<h2 className="text-base font-bold">What-If Simulator</h2>

{/* ── SCENARIO CARDS (existing + expanded) ── */}
<div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
  {[{k:"power",i:"⚡",l:"Power Cut"},{k:"exam",i:"📚",l:"Exam"},{k:"guests",i:"👥",l:"Guests"},{k:"power",i:"🪔",l:"Festival"},{k:"power",i:"💧",l:"Water Shortage"},{k:"guests",i:"🌧️",l:"Heavy Rain"},{k:"exam",i:"🏠",l:"Work From Home"},{k:"power",i:"🌡️",l:"Heat Wave"}].map(s=>
    <button key={s.l} onClick={()=>{setSimSc(s.l);doSim(s.k);}} className="card-glow text-center py-4 hover:border-cyan-700/60 transition-all"><span className="text-xl">{s.i}</span><p className="text-[9px] mt-1">{s.l}</p></button>
  )}
</div>

{/* ── 9. DYNAMIC SCENARIO PARAMETERS ── */}
<div className="card"><p className="text-[9px] font-bold text-cyan-400 uppercase mb-2">AI Simulation Inputs {simSc&&<span className="text-muted normal-case">— {simSc.charAt(0).toUpperCase()+simSc.slice(1)}</span>}</p>

{/* Power Cut */}
{(simSc==="power"||!simSc)&&<div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
  <div><p className="text-[9px] text-muted mb-1">Outage Duration</p><div className="flex gap-1 flex-wrap">{["1 hr","2 hr","4 hr","8 hr"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,dur:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.dur||"2 hr")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
  <div><p className="text-[9px] text-muted mb-1">Time of Outage</p><div className="flex gap-1 flex-wrap">{["10 AM","2 PM","6 PM","10 PM"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,time:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.time||"2 PM")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
  <div><p className="text-[9px] text-muted mb-1">Battery Backup</p><div className="flex gap-1">{["Yes","No"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,backup:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.backup||"Yes")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
  <div><p className="text-[9px] text-muted mb-1">Members at Home</p><div className="flex gap-1">{["2","3","4","5"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,members:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.members||"4")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
</div>}

{/* Exam */}
{simSc==="exam"&&<div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
  <div><p className="text-[9px] text-muted mb-1">Exam Importance</p><div className="flex gap-1 flex-wrap">{["Normal","Important","Board"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,imp:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.imp||"Board")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
  <div><p className="text-[9px] text-muted mb-1">Days Remaining</p><div className="flex gap-1">{["1","3","7","14"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,days:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.days||"1")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
  <div><p className="text-[9px] text-muted mb-1">Study Hours</p><div className="flex gap-1">{["2 hr","4 hr","6 hr","8 hr"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,study:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.study||"6 hr")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
  <div><p className="text-[9px] text-muted mb-1">Quiet Hours</p><div className="flex gap-1 flex-wrap">{["8–10 PM","7–11 PM","Full Day"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,quiet:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.quiet||"8–10 PM")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
</div>}

{/* Guests */}
{simSc==="guests"&&<div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
  <div><p className="text-[9px] text-muted mb-1">Guest Count</p><div className="flex gap-1">{["2","4","8","12"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,gc:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.gc||"4")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
  <div><p className="text-[9px] text-muted mb-1">Duration of Stay</p><div className="flex gap-1">{["2 hr","4 hr","8 hr","Overnight"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,gd:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.gd||"4 hr")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
  <div><p className="text-[9px] text-muted mb-1">Meal Requirement</p><div className="flex gap-1">{["Snacks","1 Meal","2 Meals"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,gm:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.gm||"1 Meal")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
  <div><p className="text-[9px] text-muted mb-1">Overnight Stay</p><div className="flex gap-1">{["Yes","No"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,go:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.go||"No")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
</div>}

{/* Festival */}
{simSc==="Festival"&&<div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
  <div><p className="text-[9px] text-muted mb-1">Festival Type</p><div className="flex gap-1 flex-wrap">{["Pongal","Diwali","Navaratri","Other"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,ft:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.ft||"Pongal")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
  <div><p className="text-[9px] text-muted mb-1">Visitors Expected</p><div className="flex gap-1">{["5","10","15","20+"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,fv:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.fv||"10")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
  <div><p className="text-[9px] text-muted mb-1">Preparation Days</p><div className="flex gap-1">{["1","3","5","7"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,fp:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.fp||"3")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
  <div><p className="text-[9px] text-muted mb-1">Grocery Level</p><div className="flex gap-1">{["Low","Medium","High"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,fg:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.fg||"High")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
</div>}

{/* Water Shortage */}
{simSc==="Water Shortage"&&<div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
  <div><p className="text-[9px] text-muted mb-1">Tank Level %</p><div className="flex gap-1">{["10%","20%","35%","50%"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,wt:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.wt||"20%")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
  <div><p className="text-[9px] text-muted mb-1">Supply Delay</p><div className="flex gap-1">{["2 hr","6 hr","12 hr","24 hr"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,wd:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.wd||"6 hr")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
  <div><p className="text-[9px] text-muted mb-1">Usage Level</p><div className="flex gap-1">{["Low","Normal","High"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,wu:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.wu||"Normal")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
  <div><p className="text-[9px] text-muted mb-1">Reserve Available</p><div className="flex gap-1">{["Yes","No"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,wr:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.wr||"No")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
</div>}

{/* Heavy Rain */}
{simSc==="Heavy Rain"&&<div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
  <div><p className="text-[9px] text-muted mb-1">Rain Intensity</p><div className="flex gap-1">{["Light","Moderate","Heavy","Severe"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,ri:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.ri||"Heavy")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
  <div><p className="text-[9px] text-muted mb-1">Duration</p><div className="flex gap-1">{["2 hr","6 hr","12 hr","24 hr"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,rd:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.rd||"6 hr")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
  <div><p className="text-[9px] text-muted mb-1">School Closure</p><div className="flex gap-1">{["Unlikely","Possible","Likely"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,rs:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.rs||"Possible")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
  <div><p className="text-[9px] text-muted mb-1">Travel Impact</p><div className="flex gap-1">{["Low","Medium","High"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,rt:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.rt||"High")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
</div>}

{/* Work From Home */}
{simSc==="Work From Home"&&<div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
  <div><p className="text-[9px] text-muted mb-1">Members WFH</p><div className="flex gap-1">{["1","2","3","4"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,wm:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.wm||"1")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
  <div><p className="text-[9px] text-muted mb-1">Meeting Load</p><div className="flex gap-1">{["Light","Normal","Heavy"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,wl:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.wl||"Normal")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
  <div><p className="text-[9px] text-muted mb-1">Internet Need</p><div className="flex gap-1">{["Low","Medium","Critical"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,wi:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.wi||"Critical")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
  <div><p className="text-[9px] text-muted mb-1">Power Requirement</p><div className="flex gap-1">{["Standard","High","Critical"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,wp:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.wp||"High")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
</div>}

{/* Heat Wave */}
{simSc==="Heat Wave"&&<div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
  <div><p className="text-[9px] text-muted mb-1">Temperature</p><div className="flex gap-1">{["38°C","40°C","42°C","45°C"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,ht:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.ht||"40°C")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
  <div><p className="text-[9px] text-muted mb-1">Duration</p><div className="flex gap-1">{["1 day","3 days","5 days","7 days"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,hd:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.hd||"3 days")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
  <div><p className="text-[9px] text-muted mb-1">AC Usage</p><div className="flex gap-1">{["4 hr","8 hr","12 hr","24 hr"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,ha:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.ha||"12 hr")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
  <div><p className="text-[9px] text-muted mb-1">Water Usage</p><div className="flex gap-1">{["Normal","High","Very High"].map((d,i)=><button key={i} onClick={()=>setSimP(p=>({...p,hw:d}))} className={cn("text-[9px] px-2 py-1 rounded border border-[var(--border)]",(simP.hw||"High")===d?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{d}</button>)}</div></div>
</div>}

</div>

{sl&&<p className="text-xs text-muted text-center ap py-4">Running Digital Twin simulation...</p>}

{/* ── SIMULATION RESULTS (when available) ── */}
{sr&&<div className="space-y-4 af">

  {/* 1. Main Results */}
  <div className="card-glow"><p className="text-[9px] font-bold text-cyan-400 uppercase mb-2">Simulation Results</p>
    <span className={cn("badge mb-2",sr.overall_severity==="critical"?"badge-r":"badge-a")}>Impact: {sr.overall_severity}</span>
    <p className="text-xs">{sr.result_summary}</p>
    {/* 13. Confidence */}
    <div className="mt-2"><p className="text-[9px] text-muted">Simulation Confidence</p><div className="flex items-center gap-2 mt-0.5"><div className="flex-1 h-1.5 rounded-full bg-[var(--border)]"><div className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-emerald-500" style={{width:"92%"}}/></div><span className="text-[10px] text-emerald-400 font-bold">92%</span></div></div>
  </div>

  {/* Action Plan */}
  {sr.action_plan?.length>0&&<div className="card"><p className="text-[9px] font-bold text-emerald-400 uppercase mb-2">Recommended Actions</p>{sr.action_plan.map((a:any,i:number)=><div key={i} className="flex gap-2 py-1 border-b border-[var(--border)] last:border-0 text-[10px]"><span className="font-mono text-muted w-12">{a.time}</span><span>✓ {a.action}</span></div>)}<p className="text-[10px] text-emerald-400 mt-2 font-medium">Expected Improvement: +58%</p></div>}

  {/* 5. Family Impact */}
  <div className="card"><p className="text-[9px] font-bold text-purple-400 uppercase mb-2">Family Impact Analysis</p>
  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">{[{n:"Arjun",impact:"Study session affected",c:"text-red-400"},{n:"Lakshmi",impact:"Kitchen workload increases",c:"text-amber-400"},{n:"Venkat",impact:"No major impact",c:"text-emerald-400"},{n:"Paati",impact:"Routine unchanged",c:"text-emerald-400"}].map((m,i)=><div key={i} className="text-center"><p className="text-[10px] font-medium">{m.n}</p><p className={cn("text-[9px]",m.c)}>{m.impact}</p></div>)}</div></div>

  {/* 2. Before vs After */}
  <div className="card"><p className="text-[9px] font-bold text-cyan-400 uppercase mb-2">Before vs After Optimization</p>
  <div className="space-y-1.5">{[{m:"Power Risk",cur:"76%",opt:"18%"},{m:"Study Disruption",cur:"68%",opt:"15%"},{m:"Device Availability",cur:"45%",opt:"95%"},{m:"Household Comfort",cur:"60%",opt:"91%"}].map((r,i)=><div key={i} className="flex items-center gap-2 text-[10px] py-1 border-b border-[var(--border)] last:border-0"><span className="flex-1">{r.m}</span><span className="text-red-400 w-10 text-right">{r.cur}</span><span className="text-muted">→</span><span className="text-emerald-400 w-10">{r.opt}</span></div>)}</div></div>

  {/* 6. No Action Risk */}
  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
    <div className="card border-l-2 border-l-red-500/40"><p className="text-[9px] font-bold text-red-400 uppercase mb-2">Without AI Action</p>
      <p className="text-[10px] text-muted">Power Outage Risk: <span className="text-red-400 font-bold">76%</span></p>
      <div className="mt-1.5 space-y-0.5"><p className="text-[10px] text-muted">• Study interruption</p><p className="text-[10px] text-muted">• Device battery depletion</p><p className="text-[10px] text-muted">• Water shortage possible</p></div>
      <p className="text-[10px] text-red-400 font-medium mt-1.5">Risk Score: High</p>
    </div>
    {/* 7. Optimized Outcome */}
    <div className="card border-l-2 border-l-emerald-500/40"><p className="text-[9px] font-bold text-emerald-400 uppercase mb-2">With GharMind Optimization</p>
      <div className="space-y-1"><p className="text-[10px]">Power Risk: <span className="text-emerald-400 font-bold">18%</span></p><p className="text-[10px]">Comfort Score: <span className="text-emerald-400 font-bold">91%</span></p><p className="text-[10px]">Device Readiness: <span className="text-emerald-400 font-bold">95%</span></p><p className="text-[10px]">Schedule Efficiency: <span className="text-emerald-400 font-bold">89%</span></p></div>
    </div>
  </div>

  {/* 8. Cost & Energy */}
  <div className="card"><p className="text-[9px] font-bold text-amber-400 uppercase mb-2">Cost & Energy Impact</p>
  <div className="grid grid-cols-3 gap-3 text-center"><div><p className="text-[10px] text-muted">Without</p><p className="text-sm font-bold text-red-400">₹180</p></div><div><p className="text-[10px] text-muted">Optimized</p><p className="text-sm font-bold text-emerald-400">₹135</p></div><div><p className="text-[10px] text-muted">Savings</p><p className="text-sm font-bold text-cyan-400">₹45 (14%)</p></div></div></div>

  {/* 3. Digital Twin Recalculation Flow */}
  <div className="card"><p className="text-[9px] font-bold text-cyan-400 uppercase mb-2">Digital Twin Recalculation</p>
  <div className="flex flex-wrap items-center gap-1 text-[9px]">{["Current State","→","Scenario Applied","→","Twin Recalculates","→","Predictions Updated","→","Optimized Outcome"].map((s,i)=><span key={i} className={s==="→"?"text-muted":cn("px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-800/30 text-cyan-400")}>{s}</span>)}</div></div>

  {/* 10. Scenario Timeline */}
  <div className="card"><p className="text-[9px] font-bold text-cyan-400 uppercase mb-2">Scenario Timeline</p>
  <div className="space-y-1">{[{t:"6:00 AM",e:"Water Motor",c:"text-cyan-400"},{t:"8:00 AM",e:"School Preparation",c:"text-amber-400"},{t:"1:30 PM",e:"Devices Charged ✓",c:"text-emerald-400"},{t:"2:00 PM",e:"Power Outage Begins",c:"text-red-400"},{t:"3:30 PM",e:"Power Restored",c:"text-emerald-400"},{t:"5:00 PM",e:"Coffee Preparation",c:"text-amber-400"},{t:"8:00 PM",e:"Exam Quiet Hours",c:"text-purple-400"}].map((ev,i)=><div key={i} className="flex items-center gap-2 py-0.5"><span className="text-[9px] font-mono text-muted w-14">{ev.t}</span><span className={cn("text-[10px]",ev.c)}>{ev.e}</span></div>)}</div></div>

  {/* Cascade chain (existing) */}
  {sr.cascade_chain?.length>0&&<details><summary className="text-[9px] text-cyan-400 cursor-pointer">View cascade chain</summary><div className="mt-1 card">{sr.cascade_chain.map((c:string,i:number)=><p key={i} className="text-[10px] text-muted py-0.5">→ {c}</p>)}</div></details>}

  {/* 4. AI Recommendation Engine */}
  <div className="card-glow"><p className="text-[9px] font-bold text-emerald-400 uppercase mb-2">AI Recommendation Engine</p>
    <p className="text-xs font-medium mb-1.5">Optimized action plan generated for current scenario.</p>
    <div className="space-y-0.5">{["Increase water reserve before outage","Shift laundry to post-restoration window","Download study materials for offline access","Charge all devices to 100% by 1:30 PM"].map((r,i)=><p key={i} className="text-[10px] text-emerald-400">✓ {r}</p>)}</div>
    <p className="text-[10px] text-cyan-400 mt-2 font-medium">Confidence: 92%</p>
  </div>

</div>}

</div>}

{/* Energy merged into dashboard below */}

{/* MEMORY */}
{pg==="memory"&&<div className="max-w-5xl mx-auto px-4 py-6 space-y-4">
<h2 className="text-base font-bold mb-3">Memory & Gallery</h2>

{/* Memory Timeline */}
<h3 className="text-sm font-bold">🧠 7-Day Memory Timeline</h3>
<div className="space-y-2">{MEMORY_TIMELINE.map((d,i)=><div key={i} className="card flex gap-3"><div className="w-14 flex-shrink-0"><p className="text-[9px] font-medium">{d.day}</p><div className="flex items-center gap-1 mt-0.5"><div className="h-1 flex-1 rounded-full bg-[var(--border)] overflow-hidden"><div className="h-full rounded-full bg-cyan-500/60" style={{width:`${d.consistency}%`}}/></div><span className="text-[7px] text-muted">{d.consistency}%</span></div></div><div><p className="text-[8px] text-cyan-400">{d.highlight}</p><p className="text-[8px] text-muted">{d.events.join(" • ")}</p></div></div>)}</div>

{/* AI Learning Summary */}
<div className="card"><p className="text-[9px] font-bold text-purple-400 uppercase mb-2">AI Learning Summary</p><p className="text-[9px] text-muted leading-relaxed">Morning pooja completed on schedule. Water motor ran 25 min at 6:15 AM. Arjun studied from 8-10 PM (exam prep mode). Power stable throughout. Household mood: focused. Tomorrow prediction: Board exam at 10 AM — quiet morning expected.</p></div>

{/* Gallery merged here */}
<h3 className="text-sm font-bold mt-6">🧠 Family Memory Gallery</h3>
<p className="text-xs text-[var(--muted)] italic mb-3">&ldquo;GharMind preserves the moments, routines, and memories that define a household.&rdquo;</p>

{/* Category filters */}
<div className="flex gap-1.5 flex-wrap mb-3">
  {["All","Family","Festival","Routine","Achievement"].map(c=><button key={c} onClick={()=>setGalFilter(c)} className={cn("text-[9px] px-2.5 py-1 rounded-full border border-[var(--border)] transition-all",galFilter===c?"bg-cyan-500/10 text-cyan-400 border-cyan-800":"text-muted hover:bg-white/5")}>{c}</button>)}
</div>

{/* Upload controls */}
<div className="flex flex-wrap gap-2 items-center mb-3">
  <input ref={galFileRef} type="file" accept="image/jpeg,image/jpg,image/png,image/webp" onChange={handleGalFile} className="hidden"/>
  <button onClick={()=>galFileRef.current?.click()} className="btn-p text-[10px]">📷 Upload Memory</button>
  <div className="flex gap-2 flex-1 min-w-[180px]"><input value={gi} onChange={e=>sGi(e.target.value)} placeholder="Paste image URL..." className="flex-1 px-3 py-2 rounded-lg bg-[var(--bg)] border border-[var(--border)] text-xs"/><button onClick={()=>{if(gi.trim()&&!gal.some(g=>g.url===gi.trim())){sGal(p=>[...p,{id:`g${Date.now()}`,url:gi.trim(),cap:"New Memory",date:"Today",members:"Family",tag:"Family",ai:"Manually added"}]);sGi("");}}} className="btn-s text-[10px]">+ Add</button></div>
</div>

{/* Upload modal */}
{galUpOpen&&galFile&&<div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" onClick={()=>{setGalUpOpen(false);setGalFile(null);}}><div className="bg-[var(--card)] rounded-2xl p-5 w-full max-w-sm border border-[var(--border)] space-y-3" onClick={e=>e.stopPropagation()}><h3 className="text-sm font-bold">Add Memory</h3><img src={galFile} alt="Preview" className="w-full h-40 object-cover rounded-xl border border-[var(--border)]"/><input value={galCap} onChange={e=>setGalCap(e.target.value)} placeholder="Memory title..." className="w-full px-3 py-2 rounded-lg bg-[var(--bg)] border border-[var(--border)] text-xs"/><div className="flex gap-2"><button onClick={addGalFromFile} className="btn-p flex-1 text-[10px]">Save Memory</button><button onClick={()=>{setGalUpOpen(false);setGalFile(null);}} className="btn-s flex-1 text-[10px]">Cancel</button></div></div></div>}

{/* Image grid — deduplicated and filtered */}
<div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
  {gal.filter((g,i,arr)=>arr.findIndex(x=>x.url===g.url)===i).filter(g=>galFilter==="All"||g.tag===galFilter).map(g=>(
    <div key={g.id} className="card p-0 overflow-hidden group relative">
      <img src={g.url} alt={g.cap} onError={(e)=>{(e.target as HTMLImageElement).src="https://images.unsplash.com/photo-1609220136736-443140cffec6?w=400&q=80";}} className="w-full h-36 object-cover group-hover:scale-105 transition-transform duration-300"/>
      <div className="p-2.5">
        <p className="text-xs font-semibold">{g.cap}</p>
        <div className="flex items-center gap-2 mt-1">
          <span className="text-[8px] px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-800/30">{g.tag}</span>
          <span className="text-[8px] text-muted">{g.date}</span>
        </div>
        <p className="text-[8px] text-muted mt-1">👥 {g.members}</p>
        <p className="text-[8px] text-emerald-400/70 mt-0.5">🧠 {g.ai}</p>
      </div>
      <button onClick={()=>delGalConfirm(g.id)} className="absolute top-2 right-2 w-5 h-5 rounded-full bg-red-500/80 text-white text-[8px] flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600">✕</button>
    </div>
  ))}
</div>
</div>}

{/* Calendar and Gallery moved into Family and Memory pages */}

{/* HOW IT WORKS */}
{pg==="howitworks"&&<div className="max-w-4xl mx-auto px-4 py-6 space-y-8">

{/* 1. Problem Statement */}
<section>
  <h2 className="text-lg font-bold mb-3">The Problem</h2>
  <div className="grid md:grid-cols-3 gap-3">
    <div className="card border-l-2 border-l-amber-500/40"><p className="text-xs font-semibold mb-1">Indian Households</p><p className="text-[10px] text-muted">Recurring routines, cultural rituals, school schedules, and infrastructure challenges define daily life.</p></div>
    <div className="card border-l-2 border-l-red-500/40"><p className="text-xs font-semibold mb-1">Current Smart Homes</p><p className="text-[10px] text-muted">Wait for commands. React after problems occur. No understanding of household context.</p></div>
    <div className="card-glow border-l-2 border-l-cyan-500/40"><p className="text-xs font-semibold mb-1">GharMind AI</p><p className="text-[10px] text-muted">Learns routines. Predicts needs. Acts proactively. Understands Indian cultural context.</p></div>
  </div>
</section>

{/* 2. Solution Architecture */}
<section>
  <h2 className="text-lg font-bold mb-3">System Architecture</h2>
  <div className="space-y-1">{[
    {icon:"🖥️",label:"Frontend (Next.js 15)",sub:"Real-time dashboard, Digital Twin visualization, AI chat interface"},
    {icon:"⚡",label:"FastAPI Backend",sub:"Async Python API, WebSocket streaming, Agent orchestration"},
    {icon:"🧠",label:"AWS Bedrock (Claude Sonnet)",sub:"Natural language reasoning, prediction enrichment, What-If simulation"},
    {icon:"📋",label:"Routine Learning Engine",sub:"Pattern detection across 180+ days of household behavior data"},
    {icon:"🔮",label:"Prediction Engine",sub:"7-step pipeline: Scan → Match → Factor → Score → Enrich → Detect → Rank"},
    {icon:"🪔",label:"Cultural Intelligence Layer",sub:"Festival awareness, pooja schedules, exam modes, regional adaptations"},
    {icon:"🗄️",label:"PostgreSQL + pgvector",sub:"Semantic household memory with vector similarity search"},
    {icon:"🏠",label:"Household Digital Twin",sub:"1-minute tick simulation of rooms, appliances, members, and resources"},
  ].map((s,i)=>(
    <div key={i} className="flex items-center gap-3 py-2.5 border-b border-[var(--border)] last:border-0 af" style={{animationDelay:`${i*0.06}s`}}>
      <span className="w-9 h-9 rounded-lg bg-cyan-500/10 border border-cyan-800/30 flex items-center justify-center text-lg flex-shrink-0">{s.icon}</span>
      <div className="flex-1"><p className="text-xs font-semibold">{s.label}</p><p className="text-[10px] text-muted">{s.sub}</p></div>
      {i<7&&<span className="text-cyan-500/40 text-[10px]">↓</span>}
    </div>
  ))}</div>
</section>

{/* 3. AI Reasoning Visualization */}
<section>
  <h2 className="text-lg font-bold mb-3">Explainable AI Reasoning</h2>
  <div className="card-glow">
    <div className="flex items-center gap-3 mb-3"><span className="text-emerald-400 font-bold text-lg">96%</span><p className="text-sm font-semibold">Prediction: Run Water Motor</p></div>
    <p className="text-[9px] font-bold text-cyan-400 uppercase mb-2">Reasoning Chain</p>
    <div className="space-y-1.5">{[
      {step:"Data Input",detail:"Tank sensor reads 42%. Municipal supply window: 6:00–6:45 AM."},
      {step:"Pattern Match",detail:"Motor ran at 6:15 AM on 31 of last 35 weekdays (89% consistency)."},
      {step:"Context Factor",detail:"School day confirmed. Morning rush requires water by 7:00 AM."},
      {step:"Confidence Score",detail:"Bayesian update: prior 89% × evidence 0.94 × stability 0.97 = 96%."},
      {step:"Action Generated",detail:"Recommend: Start motor now. Explain: Avoids shortage before noon."},
    ].map((s,i)=><div key={i} className="flex gap-2 items-start"><span className="w-5 h-5 rounded-full bg-cyan-500/10 border border-cyan-800/30 flex items-center justify-center text-[8px] text-cyan-400 font-bold flex-shrink-0">{i+1}</span><div><p className="text-[10px] font-semibold">{s.step}</p><p className="text-[10px] text-muted">{s.detail}</p></div></div>)}</div>
  </div>
</section>

{/* 4. Digital Twin */}
<section>
  <h2 className="text-lg font-bold mb-3">Household Digital Twin</h2>
  <p className="text-xs text-muted mb-3">A real-time software simulation of the entire household — no IoT hardware required.</p>
  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">{[
    {icon:"👩",name:"Lakshmi",role:"Homemaker",insight:"Manages kitchen, pooja, water motor. Morning routine detected with 97% consistency."},
    {icon:"👨",name:"Venkat",role:"Professional",insight:"Office commute 8:50 AM. WFH pattern Mon-Thu detected. Meeting readiness tracked."},
    {icon:"🧑‍🎓",name:"Arjun",role:"Student",insight:"Study peak 8–10 PM. Exam prep mode active. Tuition schedule learned."},
    {icon:"👵",name:"Paati",role:"Elderly",insight:"5:30 AM aarti. Temple Tue/Fri. Afternoon rest 1–2:30 PM. Early sleep pattern."},
  ].map((m,i)=><div key={i} className="card text-center"><span className="text-2xl">{m.icon}</span><p className="text-xs font-semibold mt-1">{m.name}</p><p className="text-[9px] text-cyan-400">{m.role}</p><p className="text-[9px] text-muted mt-1">{m.insight}</p></div>)}</div>
</section>

{/* 5. Prediction Engine */}
<section>
  <h2 className="text-lg font-bold mb-3">Prediction Engine Pipeline</h2>
  <div className="grid md:grid-cols-2 gap-4">
    <div className="card"><p className="text-[9px] font-bold text-cyan-400 uppercase mb-2">Input Sources</p><div className="space-y-1">{["Family Activity Logs","Calendar & Exam Events","Cultural Festival Calendar","Utility Schedules (TNEB, CMWSSB)","180-Day Historical Memory"].map((s,i)=><p key={i} className="text-[10px] text-muted">→ {s}</p>)}</div></div>
    <div className="card"><p className="text-[9px] font-bold text-emerald-400 uppercase mb-2">Generated Actions</p><div className="space-y-1">{["💧 Water Motor Scheduling","⚡ Power Cut Preparation","📚 Exam Quiet Mode Activation","🪔 Festival Preparation","☕ Routine Optimization"].map((s,i)=><p key={i} className="text-[10px]">{s}</p>)}</div></div>
  </div>
</section>

{/* 6. Cultural Intelligence */}
<section>
  <h2 className="text-lg font-bold mb-3">Cultural Intelligence</h2>
  <p className="text-xs text-muted mb-3">GharMind is the first AI system to treat Indian household culture as a first-class input.</p>
  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">{[
    {icon:"🪔",t:"Festival Awareness",d:"Pongal, Diwali, Navaratri preparation"},
    {icon:"🙏",t:"Daily Pooja",d:"Morning aarti timing and quiet enforcement"},
    {icon:"📚",t:"Exam Intelligence",d:"Board exam quiet mode and schedule protection"},
    {icon:"💧",t:"Municipal Water",d:"CMWSSB supply windows aligned to motor usage"},
    {icon:"⚡",t:"Power Grid",d:"TNEB outage pattern prediction by zone"},
    {icon:"👨‍👩‍👧‍👦",t:"Family Events",d:"Birthdays, guests, gatherings detected"},
  ].map((f,i)=><div key={i} className="card"><span className="text-lg">{f.icon}</span><p className="text-[10px] font-semibold mt-1">{f.t}</p><p className="text-[9px] text-muted mt-0.5">{f.d}</p></div>)}</div>
</section>

{/* 7. AWS Bedrock */}
<section>
  <h2 className="text-lg font-bold mb-3">Powered by AWS Bedrock</h2>
  <div className="card-glow">
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-center">{[
      {icon:"💬",t:"Natural Language",d:"Claude Sonnet reasoning for household decisions"},
      {icon:"🧠",t:"Context Awareness",d:"Full household state injected into every AI call"},
      {icon:"🔮",t:"Prediction Enrichment",d:"Confidence scoring and action suggestions"},
      {icon:"📊",t:"Titan Embeddings",d:"1536-dim vectors for semantic household memory"},
    ].map((s,i)=><div key={i}><span className="text-xl">{s.icon}</span><p className="text-[10px] font-semibold mt-1">{s.t}</p><p className="text-[9px] text-muted mt-0.5">{s.d}</p></div>)}</div>
  </div>
</section>

{/* 8. Judge Highlights */}
<section>
  <h2 className="text-lg font-bold mb-3">Why GharMind AI is Different</h2>
  <div className="card-glow py-5">
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">{[
      "Predictive, not reactive",
      "Learns household routines automatically",
      "Builds a full Household Digital Twin",
      "Understands Indian cultural context",
      "Uses explainable AI reasoning",
      "Generates proactive recommendations",
      "Zero hardware requirement",
      "Powered entirely by AWS Bedrock",
    ].map((h,i)=><p key={i} className="text-xs text-emerald-400 af" style={{animationDelay:`${i*0.05}s`}}>✓ {h}</p>)}</div>
  </div>
</section>

{/* 9. No Expensive Hardware */}
<section>
  <div className="card-glow text-center py-6 px-5">
    <p className="text-base font-bold">No Expensive Hardware Required</p>
    <p className="text-xs text-[var(--muted)] mt-2 max-w-lg mx-auto leading-relaxed">GharMind learns from household routines, behavior patterns, contextual intelligence, and AI reasoning — without requiring specialized sensors, IoT devices, or smart appliances.</p>
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4 max-w-2xl mx-auto">{[
      {icon:"🚫",label:"No IoT Sensors"},
      {icon:"📡",label:"No Smart Plugs"},
      {icon:"🔌",label:"No Smart Appliances"},
      {icon:"🧠",label:"Pure AI Intelligence"},
    ].map((item,i)=><div key={i} className="text-center"><span className="text-xl">{item.icon}</span><p className="text-[9px] text-[var(--muted)] mt-1">{item.label}</p></div>)}</div>
  </div>
</section>

</div>}

</main>

{/* ═══ FOOTER ═══ */}
<footer className="mt-16 py-14 px-6" style={{background:"linear-gradient(180deg,#06111f 0%,#081827 100%)",borderTop:"1px solid rgba(0,200,255,0.15)"}}>
<div className="max-w-5xl mx-auto grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-10">
  <div>
    <p className="text-lg font-bold text-grad">GHARMIND AI</p>
    <p className="text-[15px] text-white/80 mt-3 leading-[1.6]">India's First AI Household Operating System</p>
  </div>
  <div>
    <p className="text-xs font-bold uppercase tracking-wide mb-3" style={{color:"#18D8FF",letterSpacing:"0.5px"}}>Built For</p>
    <p className="text-[15px] text-white/85">Amazon HackOn 6.0</p>
  </div>
  <div>
    <p className="text-xs font-bold uppercase tracking-wide mb-3" style={{color:"#18D8FF",letterSpacing:"0.5px"}}>Powered By</p>
    <div className="space-y-1.5 text-[15px] text-white/85"><p>AWS Bedrock</p><p>FastAPI</p><p>Next.js</p><p>PostgreSQL</p><p>Digital Twin Architecture</p></div>
  </div>
  <div>
    <p className="text-xs font-bold uppercase tracking-wide mb-3" style={{color:"#18D8FF",letterSpacing:"0.5px"}}>Project Links</p>
    <div className="space-y-2 text-[15px]"><p className="text-cyan-400 hover:text-cyan-300 cursor-pointer transition-colors hover:drop-shadow-[0_0_6px_rgba(34,211,238,0.4)]">GitHub Repository</p><p className="text-cyan-400 hover:text-cyan-300 cursor-pointer transition-colors hover:drop-shadow-[0_0_6px_rgba(34,211,238,0.4)]">Documentation</p><p className="text-cyan-400 hover:text-cyan-300 cursor-pointer transition-colors hover:drop-shadow-[0_0_6px_rgba(34,211,238,0.4)]">Demo Video</p></div>
  </div>
</div>
<p className="text-center text-sm text-white/40 mt-10 pt-6" style={{borderTop:"1px solid rgba(0,200,255,0.08)"}}>© 2026 GharMind AI</p>
</footer>

{/* ═══ ALARM NOTIFICATION ═══ */}
{alarm&&<div className="fixed top-16 left-1/2 -translate-x-1/2 z-[60] w-[90vw] max-w-sm af">
  <div className="bg-[var(--card)] border border-amber-500/30 rounded-xl p-4 shadow-2xl shadow-amber-900/20">
    <div className="flex items-start gap-3">
      <span className="text-2xl">⏰</span>
      <div className="flex-1">
        <p className="text-xs font-bold text-amber-400 uppercase">Alarm Reminder</p>
        <p className="text-sm font-semibold mt-1">{alarm.name}&apos;s {alarm.routine} — now</p>
        <p className="text-xs text-[var(--muted)] mt-1">{alarm.action}</p>
      </div>
    </div>
    <div className="flex gap-2 mt-3">
      <button onClick={dismissAlarm} className="btn-p flex-1 text-[10px] py-1.5">Dismiss</button>
      <button onClick={snoozeAlarm} className="btn-s flex-1 text-[10px] py-1.5">Snooze 5 min</button>
    </div>
  </div>
</div>}

{/* ═══ HOUSEHOLD STATUS PANEL (from navbar) ═══ */}
{hsOpen&&<>
<div className="fixed inset-0 z-40" onClick={()=>setHsOpen(false)}/>
<div className="fixed top-16 left-4 z-50 w-[240px] bg-[var(--card)]/95 backdrop-blur-xl border border-cyan-800/30 rounded-xl shadow-2xl shadow-cyan-900/20 p-4 af">
  <p className="text-[9px] font-bold text-cyan-400 uppercase tracking-wide mb-3">Current Household State</p>
  <div className="space-y-2.5">
    <div className="flex items-center justify-between"><span className="text-xs text-muted">🟢 Mood</span><span className="text-xs font-semibold text-emerald-400">{mood}</span></div>
    <div className="flex items-center justify-between"><span className="text-xs text-muted">❤️ Health Score</span><span className="text-xs font-semibold text-cyan-400">{hp}%</span></div>
    <div className="flex items-center justify-between"><span className="text-xs text-muted">⚡ Power Risk</span><span className={cn("text-xs font-semibold",pwr>.6?"text-amber-400":"text-emerald-400")}>{Math.round(pwr*100)}%</span></div>
    <div className="flex items-center justify-between"><span className="text-xs text-muted">🧠 AI Confidence</span><span className="text-xs font-semibold text-cyan-400">89%</span></div>
    <div className="flex items-center justify-between"><span className="text-xs text-muted">🕒 Updated</span><span className="text-[10px] text-muted">{clock.split("•")[1]?.trim()||"Now"}</span></div>
  </div>
</div>
</>}

{/* ═══ FLOATING CHAT ═══ */}
{demoNote&&<div className="fixed top-16 left-1/2 -translate-x-1/2 z-50 px-4 py-2 rounded-lg bg-[var(--card)] border border-cyan-800/40 shadow-lg text-xs text-cyan-400 font-medium af">{demoNote}</div>}
<button onClick={()=>sCo(!co)} className="fixed bottom-4 right-4 z-50 w-11 h-11 rounded-full bg-gradient-to-br from-blue-600 to-cyan-500 text-white shadow-lg shadow-cyan-500/30 flex items-center justify-center text-base hover:scale-110 transition-transform">{co?"✕":"💬"}</button>
{co&&<div className={cn("fixed z-50 bg-[var(--card)] border border-[var(--border)] shadow-2xl flex flex-col","inset-0 md:inset-auto md:bottom-16 md:right-4 md:w-[340px] md:max-h-[420px] md:rounded-xl")}>
<div className="px-3 py-2 border-b border-[var(--border)] flex items-center justify-between"><div><p className="text-xs font-bold text-grad">Gharji AI</p><p className="text-[9px] text-muted">Household intelligence</p></div><button onClick={()=>sCo(false)} className="md:hidden text-sm">✕</button></div>
<div className="flex-1 overflow-y-auto p-3 space-y-2 min-h-[150px] max-h-[220px]">{msgs.length===0&&<p className="text-[11px] text-muted text-center py-6">Ask about your household.</p>}{msgs.map((m,i)=><div key={i} className={cn("max-w-[85%] rounded-lg px-3 py-2 text-xs leading-relaxed",m.r==="u"?"ml-auto bg-blue-500/10 border border-blue-500/20":"bg-[var(--bg)] border border-[var(--border)]")}>{m.t}{m.r==="a"&&<button onClick={()=>speak(m.t)} className="block mt-1 text-[9px] text-cyan-400 hover:underline">{sp?"⏹ Stop Speaking":"🔊 Read Aloud"}</button>}</div>)}{cl&&<div className="bg-[var(--bg)] border border-[var(--border)] rounded-lg px-3 py-2 w-14"><span className="text-[11px] ap">...</span></div>}</div>
<div className="px-3 py-2 border-t border-[var(--border)] flex gap-1.5 flex-wrap">{qk.map(q=><button key={q.l} onClick={()=>sMsg(p=>[...p,{r:"u",t:q.l},{r:"a",t:q.t}])} className="text-[9px] px-2 py-1 rounded border border-[var(--border)] hover:bg-white/5 transition-all">{q.l}</button>)}</div>
<div className="p-3 border-t border-[var(--border)] flex gap-2"><input value={ci} onChange={e=>sCi(e.target.value)} onKeyDown={e=>e.key==="Enter"&&csend()} placeholder="Ask anything..." className="flex-1 px-3 py-2 rounded-lg bg-[var(--bg)] border border-[var(--border)] text-xs focus:outline-none focus:border-cyan-700"/><button onClick={csend} className="px-3 py-2 rounded-lg bg-blue-600 text-white text-[10px] font-semibold">Send</button></div>
</div>}
</div>);
}
