const $=s=>document.querySelector(s);
const STAGES=[["Upload","Reading your text and screenshot"],["Extract","Finding organization, deadline, URLs and payment requests"],["Search","Searching for independent sources"],["Compare evidence","Checking each claim against retrieved sources"],["Report","Scoring indicators and writing safe next steps"]];
const DEMO={demo:true,overall:"High risk indicators",risk_score:70,
 extracted:{organization:"National Student Scholarship",deadline:"Before midnight",urls:[],payment:"Rs 499 processing fee"},
 claims:[{id:"C1",text:"A scholarship is available",status:"unverified",reason:"No official notice for this scholarship was found in the retrieved results."},
 {id:"C2",text:"The student must pay Rs 499",status:"suspicious",reason:"An upfront fee is requested before any independent verification. This is a warning sign, not proof of fraud."}],
 evidence:[{title:"Example source title (mockup)",url:"https://example.gov.in/scholarships",snippet:"Illustrative snippet only. Real snippets come from your Tavily results.",retrieved:"Demo data"},
 {title:"Example official notice (mockup)",url:"https://example.org/notice",snippet:"Placeholder text showing where evidence appears.",retrieved:"Demo data"}],
 indicators:[{name:"Unusual upfront payment request",weight:25,max:30},{name:"High-pressure deadline",weight:10,max:30},{name:"Unsupported guaranteed-selection claim",weight:15,max:30},{name:"Suspicious domain mismatch",weight:20,max:30}],
 next:["Do not pay until the offer is independently verified.","Visit the official website by typing its address yourself.","Contact the institution using details you found independently."],
 limits:["Demo data, not a real investigation.","The score is a risk indicator, not a probability of fraud.","No warning signs does not prove a message is legitimate."]};
const stepsEl=$("#steps");
function drawSteps(state){stepsEl.innerHTML=STAGES.map((s,i)=>`<li class="${state[i]||""}"><span class="dot">${state[i]==="done"?"✓":i+1}</span><div><b>${s[0]}</b><small>${s[1]}</small></div></li>`).join("")}
drawSteps([]);
let file=null;
const msg=(t,k="err")=>{const m=$("#msg");m.textContent=t;m.className="msg on "+k};
const clr=()=>$("#msg").className="msg";
function setFile(f){clr();if(!f)return;
 if(!["image/png","image/jpeg","image/webp"].includes(f.type))return msg("Upload a PNG, JPEG or WEBP image.");
 if(f.size>8*1024*1024)return msg("Image must be 8 MB or smaller.");
 file=f;$("#pimg").src=URL.createObjectURL(f);$("#pname").textContent=f.name;$("#psize").textContent=(f.size/1024).toFixed(0)+" KB";$("#prev").classList.add("on")}
$("#file").onchange=e=>setFile(e.target.files[0]);
$("#rm").onclick=()=>{file=null;$("#file").value="";$("#prev").classList.remove("on")};
const drop=$("#drop");
["dragover","dragenter"].forEach(n=>drop.addEventListener(n,e=>{e.preventDefault();drop.classList.add("over")}));
["dragleave","drop"].forEach(n=>drop.addEventListener(n,e=>{e.preventDefault();drop.classList.remove("over")}));
drop.addEventListener("drop",e=>setFile(e.dataTransfer.files[0]));
const loadDemoText=()=>{$("#txt").value="Congratulations! You are selected for the National Student Scholarship. Pay Rs 499 processing fee before midnight to claim your reward.";clr()};
$("#demo").onclick=loadDemoText;
$("#demoTop").onclick=()=>{loadDemoText();$("#useDemo").checked=true;$("#start").scrollIntoView();run()};

async function investigateMessage({text,file}){
 const fd=new FormData();if(text&&text.trim())fd.append("text",text);if(file)fd.append("file",file);
 const r=await fetch($("#api").value,{method:"POST",body:fd});
 if(!r.ok){let d="";try{d=(await r.json()).detail}catch(e){}throw new Error(d||"Could not complete investigation.")}
 return r.json();
}
const wait=ms=>new Promise(r=>setTimeout(r,ms));
async function run(){
 clr();const text=$("#txt").value;
 if(!text.trim()&&!file)return msg("Add some text or upload a screenshot first.");
 const btn=$("#go");btn.disabled=true;btn.textContent="Investigating…";$("#report").className="";
 const st=[];
 try{
  let data;
  if($("#useDemo").checked){
   msg("Demo mode: stages below are simulated and the report uses mockup data.","note");
   for(let i=0;i<5;i++){st[i]="run";drawSteps(st);await wait(650);st[i]="done";drawSteps(st)}
   data=DEMO;
  }else{
   let k=0;st[0]="run";drawSteps(st);
   const tick=setInterval(()=>{if(k<3){st[k]="done";k++;st[k]="run";drawSteps(st)}},2500);
   try{data=await investigateMessage({text,file})}finally{clearInterval(tick)}
   drawSteps(STAGES.map(()=>"done"));
  }
  render(data);
 }catch(e){
  const i=Math.max(0,st.findIndex(x=>x==="run"));st[i]="fail";drawSteps(st);
  msg("Investigation failed: "+(e.message||"check that your backend is running")+".");
 }
 btn.disabled=false;btn.textContent="Investigate";
}
$("#go").onclick=run;

const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const safeUrl=u=>/^https?:\/\//i.test(u)?u:"#";
function render(d){
 const score=Math.max(0,Math.min(100,d.risk_score??0));
 const col=score>=60?"var(--r)":score>=30?"var(--a)":"var(--g)";
 const ex=d.extracted||{};
 const label={verified:"Verified",contradicted:"Contradicted",unverified:"Unverified",suspicious:"Suspicious indicator"};
 const R=$("#report");
 R.innerHTML=`<div class="glass panel">
 ${d.demo?'<div class="banner">DEMO DATA · NOT A REAL INVESTIGATION</div>':""}
 <div class="top"><div class="ring" style="--p:${score};--col:${col}" role="img" aria-label="Risk indicator score ${score} out of 100"><div><strong>${score}</strong><small>/ 100</small></div></div>
 <div><h2 style="font-size:clamp(1.6rem,4vw,2.4rem)">${esc(d.overall||"Assessment")}</h2><p style="color:var(--mute);margin-top:.5rem">This is a risk indicator score, not a probability of fraud. It sums explainable warning signs.</p>
 <div class="legend">${Object.keys(label).map(k=>`<span class="badge ${k}">${label[k]}</span>`).join("")}</div></div></div>
 <div class="facts"><div><small>Organization</small><b>${esc(ex.organization||"Not found")}</b></div><div><small>Deadline</small><b>${esc(ex.deadline||"None")}</b></div><div><small>URLs</small><b>${(ex.urls||[]).length?ex.urls.map(esc).join(", "):"None found"}</b></div><div><small>Payment request</small><b>${esc(ex.payment||"None")}</b></div></div>
 <h3>Claims</h3><div class="grid2">${(d.claims||[]).map(c=>`<article class="claim ${esc(c.status)}"><header><div><span class="id">${esc(c.id)}</span><b style="display:block">${esc(c.text)}</b></div><span class="badge">${label[c.status]||esc(c.status)}</span></header><p>${esc(c.reason)}</p></article>`).join("")}</div>
 <h3>Evidence</h3><div class="grid2">${(d.evidence||[]).length?d.evidence.map(e=>`<a class="ev" href="${esc(safeUrl(e.url))}" target="_blank" rel="noopener noreferrer"><b>${esc(e.title)}</b><span>${esc(e.url)}</span><p>${esc(e.snippet)}</p><small>Retrieved: ${esc(e.retrieved||"unknown")}</small></a>`).join(""):"<p>No evidence retrieved.</p>"}</div>
 <div class="grid2"><div><h3>Risk indicators</h3>${(d.indicators||[]).map(i=>`<div class="bar"><div><span>${esc(i.name)}</span><b>+${esc(i.weight)}</b></div><i style="--w:${Math.min(100,(i.weight/(i.max||30))*100)}%"></i></div>`).join("")}</div>
 <div><h3>Safe next steps</h3><ul class="list">${(d.next||[]).map(n=>`<li>${esc(n)}</li>`).join("")}</ul><h3>Limitations</h3><ul class="list">${(d.limits||[]).map(n=>`<li>${esc(n)}</li>`).join("")}</ul></div></div>
 <div class="row"><button class="btn ghost" onclick="window.print()">Print report</button><button class="btn" onclick="document.querySelector('#start').scrollIntoView()">Check another message</button></div></div>`;
 R.className="on";R.focus({preventScroll:true});R.scrollIntoView({behavior:"smooth"});
}
const root=document.documentElement;
try{const t=localStorage.getItem("dd-theme");if(t)root.dataset.theme=t}catch(e){}
$("#theme").onclick=()=>{const dark=root.dataset.theme?root.dataset.theme==="dark":matchMedia("(prefers-color-scheme:dark)").matches;const n=dark?"light":"dark";root.dataset.theme=n;try{localStorage.setItem("dd-theme",n)}catch(e){}};

// Auto-detect a live backend on the same origin and switch off demo mode.
fetch("/health").then(r=>r.ok?r.json():null).then(h=>{
 if(!h||!h.ok)return;$("#useDemo").checked=false;
 const mode=(h.ai?"AI on":"AI off (rule-based mode)")+" · "+(h.search?"web search on":"web search off");
 msg("Live backend connected — "+mode+".","note");
}).catch(()=>{});
