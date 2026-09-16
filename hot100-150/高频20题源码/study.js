(() => {
  'use strict';
  const key='hot100-core20-mastery-v1';
  const checks=[...document.querySelectorAll('[data-mastered]')];
  const list=document.getElementById('problem-nav-list');
  const links=[...list.querySelectorAll('[data-nav-problem]')];
  const valid=new Set(checks.map(e=>e.dataset.mastered));
  let completed=new Set(),storageAvailable=true;
  try{
    const stored=JSON.parse(localStorage.getItem(key)||'[]');
    if(Array.isArray(stored))completed=new Set(stored.map(String).filter(id=>valid.has(id)));
  }catch{storageAvailable=false;}
  function render(){
    checks.forEach(e=>e.checked=completed.has(e.dataset.mastered));
    links.forEach(a=>{
      const done=completed.has(a.dataset.navProblem);
      a.classList.toggle('mastered',done);a.querySelector('.done-mark').hidden=!done;
    });
    document.querySelector('.progress-text').textContent=`已掌握 ${completed.size} / 20`;
    document.getElementById('study-progress').value=completed.size;
    if(!storageAvailable)document.querySelector('.storage-hint').textContent='浏览器未提供可用的本地存储；本次阅读仍可勾选，关闭后可能不保留。';
  }
  checks.forEach(e=>e.addEventListener('change',()=>{
    if(e.checked)completed.add(e.dataset.mastered);else completed.delete(e.dataset.mastered);
    try{localStorage.setItem(key,JSON.stringify([...completed]));}catch{storageAvailable=false;}
    render();
  }));
  document.querySelectorAll('.study-tools,.study-check').forEach(e=>e.hidden=false);
  document.getElementById('nav-search').addEventListener('input',event=>{
    const term=event.target.value.trim().toLowerCase();
    links.forEach(a=>a.hidden=!a.querySelector('.nav-title').textContent.toLowerCase().includes(term));
    document.getElementById('search-empty').hidden=links.some(a=>!a.hidden);
  });
  document.querySelectorAll('[data-order]').forEach(button=>button.addEventListener('click',()=>{
    const field=button.dataset.order;
    [...links].sort((a,b)=>Number(a.dataset[field])-Number(b.dataset[field])).forEach(a=>list.append(a));
    document.querySelectorAll('[data-order]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
  }));
  const drawer=document.querySelector('.nav-drawer');
  const mobile=matchMedia('(max-width:760px)');
  if(mobile.matches)drawer.open=false;
  mobile.addEventListener('change',event=>{drawer.open=!event.matches;});
  links.forEach(a=>a.addEventListener('click',()=>{if(mobile.matches)drawer.open=false;}));
  render();
})();
