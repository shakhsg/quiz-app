// ── question bank ────────────────────────────────────────────────────────────
const CATS=[
  { name:"General Knowledge", icon:"🌍", questions:[
    {q:"What is the capital city of Australia?",        opts:["Sydney","Melbourne","Canberra","Brisbane"],    ans:2},
    {q:"How many continents are there on Earth?",       opts:["5","6","8","7"],                               ans:3},
    {q:"Which language is spoken in Brazil?",           opts:["Spanish","Portuguese","French","English"],     ans:1},
    {q:"Who painted the Mona Lisa?",                    opts:["Michelangelo","Van Gogh","Leonardo da Vinci","Picasso"],ans:2},
    {q:"What is the largest ocean on Earth?",           opts:["Atlantic","Indian","Arctic","Pacific"],         ans:3},
    {q:"In which year did World War II end?",           opts:["1943","1944","1945","1946"],                   ans:2},
    {q:"What is the currency of Japan?",                opts:["Yuan","Won","Ringgit","Yen"],                  ans:3},
  ]},
  { name:"Science", icon:"🔬", questions:[
    {q:"What is the chemical symbol for water?",        opts:["WO","HO","H₂O","W₂O"],                        ans:2},
    {q:"What planet is known as the Red Planet?",       opts:["Saturn","Mars","Jupiter","Venus"],             ans:1},
    {q:"What gas do plants absorb from atmosphere?",    opts:["Oxygen","Nitrogen","Carbon Dioxide","Hydrogen"],ans:2},
    {q:"How many bones in the adult human body?",       opts:["186","206","216","226"],                       ans:1},
    {q:"What is the powerhouse of the cell?",           opts:["Nucleus","Ribosome","Mitochondria","Chloroplast"],ans:2},
    {q:"Speed of light (approx.) in km/s?",             opts:["150,000","200,000","300,000","400,000"],       ans:2},
    {q:"Which element has atomic number 1?",            opts:["Helium","Carbon","Oxygen","Hydrogen"],          ans:3},
  ]},
  { name:"Technology", icon:"💻", questions:[
    {q:"What does 'CPU' stand for?",                    opts:["Central Process Unit","Central Processing Unit","Computer Personal Unit","Core Processing Unit"],ans:1},
    {q:"Who created the Python programming language?",  opts:["Google","Microsoft","Python Software Foundation","Oracle"],ans:2},
    {q:"What does 'HTML' stand for?",                   opts:["Hyper Transfer Markup Language","High Text Markup Language","Hyper Text Markup Language","Hyper Text Modern Language"],ans:2},
    {q:"Which is NOT a programming language?",          opts:["Swift","Kotlin","Photon","Rust"],              ans:2},
    {q:"What does 'RAM' stand for?",                    opts:["Random Access Memory","Read Access Memory","Run Access Module","Random Array Module"],ans:0},
    {q:"Who developed the Android OS?",                 opts:["Apple","Samsung","Google","Microsoft"],         ans:2},
    {q:"Base of the binary number system?",             opts:["8","10","16","2"],                             ans:3},
  ]},
]

const GRADES=[
  {min:100,label:"Perfect Score! 🏆",color:"#fbbf24"},
  {min:80, label:"Excellent! 🥇",    color:"#4ade80"},
  {min:60, label:"Good Job! 🥈",     color:"#22d3ee"},
  {min:40, label:"Needs Improvement 🥉",color:"#f59e0b"},
  {min:0,  label:"Keep Practising 📖",  color:"#f87171"},
]

const KEYS=["A","B","C","D"]
const TIME_LIMIT=15, NUM_Q=5

// ── state ────────────────────────────────────────────────────────────────────
let selCat=null, questions=[]
let qIdx=0, correct=0, wrong=0
let timer=null, tLeft=TIME_LIMIT, answered=false

// ── navigation ────────────────────────────────────────────────────────────────
function goTo(id){
  document.querySelectorAll('.screen').forEach(s=>s.classList.remove('active'))
  document.getElementById(id).classList.add('active')
}

// ── helpers ───────────────────────────────────────────────────────────────────
const shuffle=a=>{ const b=[...a]; for(let i=b.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[b[i],b[j]]=[b[j],b[i]];} return b }

// ── category grid ─────────────────────────────────────────────────────────────
function buildCats(){
  const g=document.getElementById('cat-grid')
  CATS.forEach((c,i)=>{
    const el=document.createElement('div')
    el.className='cat-card'
    el.innerHTML=`<span class="ci">${c.icon}</span><div class="cn">${c.name}</div><div class="cc">${c.questions.length} Q's</div>`
    el.onclick=()=>{
      document.querySelectorAll('.cat-card').forEach(x=>x.classList.remove('active'))
      el.classList.add('active'); selCat=i
      document.getElementById('start-btn').disabled=false
    }
    g.appendChild(el)
  })
}

// ── quiz ──────────────────────────────────────────────────────────────────────
function startQuiz(){
  questions=shuffle(CATS[selCat].questions).slice(0,NUM_Q)
  qIdx=0; correct=0; wrong=0
  document.getElementById('qt').textContent=questions.length
  document.getElementById('clbl').textContent=CATS[selCat].name
  goTo('s-quiz'); renderQ()
}
function renderQ(){
  answered=false
  const q=questions[qIdx]
  document.getElementById('qn').textContent=qIdx+1
  document.getElementById('pfill').style.width=(qIdx/questions.length*100)+'%'
  document.getElementById('qtxt').textContent=q.q
  document.getElementById('ftost').className='ftost'
  document.getElementById('tmo').className='tmo'
  const optsEl=document.getElementById('opts'); optsEl.innerHTML=''
  q.opts.forEach((opt,i)=>{
    const b=document.createElement('button')
    b.className='opt-btn'; b.id=`ob${i}`
    b.innerHTML=`<span class="opt-key">${KEYS[i]}</span><span>${opt}</span>`
    b.onclick=()=>selAns(i); optsEl.appendChild(b)
  })
  startTimer()
}
function startTimer(){
  clearInterval(timer); tLeft=TIME_LIMIT; updTimer(tLeft)
  timer=setInterval(()=>{ tLeft--; updTimer(tLeft); if(tLeft<=0){ clearInterval(timer); onTimeout() } },1000)
}
function updTimer(t){
  const bar=document.getElementById('tbar'),num=document.getElementById('tnum')
  bar.style.strokeDashoffset=138.2*(1-t/TIME_LIMIT)
  bar.style.stroke=t<=5?'var(--danger)':t<=8?'var(--warn)':'var(--accent)'
  num.textContent=t; num.style.color=t<=5?'var(--danger)':t<=8?'var(--warn)':'var(--text)'
}
function onTimeout(){
  if(answered)return; answered=true; wrong++; disOpts()
  document.getElementById(`ob${questions[qIdx].ans}`).classList.add('correct')
  document.getElementById('tmo').classList.add('show')
  setTimeout(nextQ,2000)
}
function selAns(i){
  if(answered)return; answered=true; clearInterval(timer); disOpts()
  const q=questions[qIdx],t=document.getElementById('ftost')
  if(i===q.ans){
    correct++; document.getElementById(`ob${i}`).classList.add('correct')
    t.textContent='✅  Correct! Well done!'; t.className='ftost show ok'
  } else {
    wrong++; document.getElementById(`ob${i}`).classList.add('wrong')
    document.getElementById(`ob${q.ans}`).classList.add('correct')
    t.textContent=`❌  Wrong! Correct answer: ${KEYS[q.ans]}`; t.className='ftost show bad'
  }
  setTimeout(nextQ,1800)
}
function disOpts(){ document.querySelectorAll('.opt-btn').forEach(b=>b.disabled=true) }
function nextQ(){ qIdx++; qIdx>=questions.length?showResults():renderQ() }
function showResults(){
  const total=questions.length, pct=Math.round((correct/total)*100)
  const grade=GRADES.find(g=>pct>=g.min)
  document.getElementById('rpct').textContent=pct+'%'
  document.getElementById('rc').textContent=correct
  document.getElementById('rw').textContent=wrong
  document.getElementById('rtot').textContent=total
  document.getElementById('rgrade').innerHTML=`<span style="color:${grade.color}">${grade.label}</span>`
  goTo('s-results')
  setTimeout(()=>{
    document.getElementById('rring').style.strokeDashoffset=502.4*(1-pct/100)
    document.getElementById('rring').style.stroke=grade.color
  },150)
}

// ── init ──────────────────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', buildCats)
