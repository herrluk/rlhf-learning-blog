(() => {
  'use strict';
  const payload=JSON.parse(document.getElementById('book-data').textContent);
  const navFilters=document.querySelector('.nav-filters');
  if(navFilters){
    const links=Array.from(document.querySelectorAll('[data-nav-problem]'));
    const buttons=Array.from(navFilters.querySelectorAll('[data-nav-filter]'));
    const summary=document.querySelector('.nav-summary');
    const hotCount=links.filter(a=>a.dataset.navScope==='hot').length;
    const storageKey='algorithm-study-nav-scope-v1';
    let scope='all';
    try{if(localStorage.getItem(storageKey)==='hot')scope='hot';}catch{}
    function filter(next){
      scope=next;
      links.forEach(a=>{a.hidden=scope==='hot'&&a.dataset.navScope!=='hot';});
      buttons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.navFilter===scope)));
      summary.textContent=scope==='hot'?`导航显示 ${hotCount} 道 Hot100`:`Hot100 ${hotCount} 题 · 非 Hot100 ${links.length-hotCount} 题`;
    }
    buttons.forEach(b=>b.addEventListener('click',()=>{
      filter(b.dataset.navFilter);
      try{localStorage.setItem(storageKey,scope);}catch{}
    }));
    navFilters.hidden=false;summary.hidden=false;filter(scope);
  }
  const players=[];
  for(const problem of payload.problems || []){
    const host=document.getElementById('demo-'+problem.id);
    const view=host.querySelector('.visual'),select=host.querySelector('select');
    const slider=host.querySelector('input[type=range]'),count=host.querySelector('.counter');
    const buttons=Object.fromEntries(Array.from(host.querySelectorAll('[data-action]')).map(b=>[b.dataset.action,b]));
    let example=0,index=0,timer=null;
    const pause=()=>{if(timer!==null)clearInterval(timer);timer=null;buttons.play.textContent='自动播放';buttons.play.setAttribute('aria-pressed','false');};
    function render(){
      const e=problem.examples[example];
      view.innerHTML=e.frames[index];
      const io=host.querySelector('.example-io');io.replaceChildren();
      const input=document.createElement('strong');input.textContent='输入：';
      const output=document.createElement('strong');output.textContent='输出：';
      io.append(input,document.createTextNode(String(e.input)),document.createElement('br'),output,document.createTextNode(String(e.output)));
      slider.max=e.frames.length-1;slider.value=index;
      slider.setAttribute('aria-valuetext',`第 ${index+1} 步，共 ${e.frames.length} 步`);
      count.textContent=`${index+1} / ${e.frames.length} 步`;
      buttons.first.disabled=buttons.prev.disabled=index===0;
      buttons.next.disabled=buttons.last.disabled=index===e.frames.length-1;
      buttons.play.disabled=e.frames.length<2;
      host.dataset.step=index;host.dataset.example=example;
      if(index===e.frames.length-1)pause();
    }
    function go(i){pause();index=Math.max(0,Math.min(problem.examples[example].frames.length-1,i));render();}
    buttons.first.onclick=()=>go(0);buttons.prev.onclick=()=>go(index-1);
    buttons.next.onclick=()=>go(index+1);buttons.last.onclick=()=>go(problem.examples[example].frames.length-1);
    buttons.play.onclick=()=>{if(problem.examples[example].frames.length<2)return;if(timer!==null){pause();return;}players.forEach(p=>p.pause());if(index===problem.examples[example].frames.length-1){index=0;render();}buttons.play.textContent='暂停';buttons.play.setAttribute('aria-pressed','true');timer=setInterval(()=>{index++;render();},1500);};
    slider.oninput=()=>go(Number(slider.value));
    select.onchange=()=>{example=Number(select.value);go(0);};
    players.push({pause});render();
  }
  document.addEventListener('visibilitychange',()=>{if(document.hidden)players.forEach(p=>p.pause());});
  window.addEventListener('beforeprint',()=>{players.forEach(p=>p.pause());document.querySelectorAll('details').forEach(d=>{d.dataset.printOpen=d.open?'1':'0';d.open=true;});});
  window.addEventListener('afterprint',()=>document.querySelectorAll('details').forEach(d=>{if(d.dataset.printOpen==='0')d.open=false;}));
  document.getElementById('print').onclick=()=>window.print();
  if('IntersectionObserver' in window){
    const nav=Array.from(document.querySelectorAll('.sidebar a[href^="#"]'));
    const observer=new IntersectionObserver(entries=>{
      const first=entries.filter(e=>e.isIntersecting).sort((a,b)=>a.boundingClientRect.top-b.boundingClientRect.top)[0];
      if(first)nav.forEach(a=>{const selected=a.hash==='#'+first.target.id;a.classList.toggle('active',selected);if(selected)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');});
    },{rootMargin:'-10% 0px -70% 0px'});
    document.querySelectorAll('main>section').forEach(e=>observer.observe(e));
  }
})();
