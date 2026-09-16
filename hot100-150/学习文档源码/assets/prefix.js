(() => {
  'use strict';
  const sets=[[2,-1,3,4],[0,0,0],[-2,5,-3,4]];
  const foundation=document.getElementById('prefix-foundation');
  if(!foundation)return;
  const sum=values=>values.reduce((total,x)=>total+x,0);
  function prefixOf(values){const p=[0];for(const x of values)p.push(p[p.length-1]+x);return p;}
  // Values are fixed numeric lesson data; labels are defined in this script.
  function cells(values,{active=[],removed=[],changed=-1,labels={}}={}){
    return '<div class="array-scroll" tabindex="0" role="region" aria-label="可横向滚动的数组"><div class="array">'+values.map((x,i)=>`<div class="cell${active.includes(i)?' in':''}${removed.includes(i)?' removed':''}${i===changed?' changed':''}"><div class="index">${i}</div><div class="value">${x}</div><div class="pointer">${labels[i]||''}</div></div>`).join('')+'</div></div>';
  }
  const build=document.getElementById('prefix-build-lab');
  const buildChoice=document.getElementById('prefix-build-example');
  let buildCase=0,step=0;
  function drawBuild(){
    const nums=sets[buildCase],prefix=prefixOf(nums);
    const labels={};if(step>0)labels[step-1]='本次加入';
    const note=step===0?'空前缀已确定为 0；问号表示尚未计算。点击下一步，加入 nums[0]。':`加入 nums[${step-1}]=${nums[step-1]}，前 ${step} 个数的和为 prefix[${step}]=prefix[${step-1}]+nums[${step-1}]=${prefix[step-1]}+(${nums[step-1]})=${prefix[step]}。`;
    build.querySelector('.prefix-build-view').innerHTML='<h5>原数组 nums · 上方是元素下标 i</h5>'+cells(nums,{active:Array.from({length:step},(_,i)=>i),changed:step-1,labels})+'<h5>前缀表 prefix · 上方是已经取了多少个元素 t</h5>'+cells(prefix.map((x,i)=>i<=step?x:'?'),{active:Array.from({length:step+1},(_,i)=>i),changed:step,labels:{[step]:'prefix['+step+']'}})+`<div class="status" role="status" aria-live="polite"><strong>${step===0?'初始化':step===nums.length?'构建完成':'从旧前缀得到新前缀'}</strong><p>${note}</p></div>`;
    build.dataset.step=String(step);build.dataset.example=String(buildCase);
    StudyMath.typeset(build.querySelector('.prefix-build-view'));
    document.getElementById('prefix-build-count').textContent=`已加入 ${step} / ${nums.length} 个元素`;
    build.querySelector('[data-prefix-build=prev]').disabled=step===0;
    build.querySelector('[data-prefix-build=reset]').disabled=step===0;
    build.querySelector('[data-prefix-build=next]').disabled=step===nums.length;
    build.querySelector('[data-prefix-build=last]').disabled=step===nums.length;
  }
  buildChoice.addEventListener('change',()=>{buildCase=Number(buildChoice.value);step=0;drawBuild();});
  build.querySelectorAll('[data-prefix-build]').forEach(button=>button.addEventListener('click',()=>{
    const action=button.dataset.prefixBuild;
    if(action==='reset')step=0;
    else if(action==='last')step=sets[buildCase].length;
    else step+=action==='next'?1:-1;
    step=Math.max(0,Math.min(sets[buildCase].length,step));drawBuild();
  }));
  const query=document.getElementById('prefix-query-lab');
  const queryChoice=document.getElementById('prefix-query-example');
  const leftSelect=document.getElementById('prefix-left'),rightSelect=document.getElementById('prefix-right');
  let queryCase=0,left=1,right=3;
  function drawQuery(){
    const nums=sets[queryCase],prefix=prefixOf(nums),end=right+1;
    const active=Array.from({length:right-left+1},(_,i)=>left+i),removed=Array.from({length:left},(_,i)=>i);
    const labels=left===right?{[left]:'left · right'}:{[left]:'left',[right]:'right'};
    const result=prefix[end]-prefix[left];
    query.querySelector('.prefix-query-view').innerHTML='<h5>原数组：绿色保留，橙色是要减掉的共同前缀</h5>'+cells(nums,{active,removed,labels})+'<h5>前缀表：选择两条边界对应的累计值</h5>'+cells(prefix,{active:[left,end],labels:{[left]:'left',[end]:'right+1'}})+`<div class="equation" data-prefix-result="${result}">prefix[${end}] − prefix[${left}]<br>= ${prefix[end]} − (${prefix[left]}) = <strong>${result}</strong></div><div class="status" role="status" aria-live="polite"><strong>从较长前缀中减掉共同前半段</strong><p>先取前 ${end} 个元素 [${nums.slice(0,end).join(', ')}]，其和为 ${prefix[end]}；再减去前 ${left} 个元素 ${left?'['+nums.slice(0,left).join(', ')+']':'（空前缀）'}，其和为 ${prefix[left]}。留下下标 [${left},${right}] 的 [${nums.slice(left,end).join(', ')}]，直接相加也得到 ${sum(nums.slice(left,end))}。</p></div>`;
    leftSelect.value=String(left);rightSelect.value=String(right);
    query.dataset.left=String(left);query.dataset.right=String(right);query.dataset.example=String(queryCase);
    StudyMath.typeset(query.querySelector('.prefix-query-view'));
  }
  function resetQuery(){
    const n=sets[queryCase].length;
    const options=Array.from({length:n},(_,i)=>`<option value="${i}">${i}</option>`).join('');
    leftSelect.innerHTML=rightSelect.innerHTML=options;left=0;right=n-1;drawQuery();
  }
  leftSelect.addEventListener('change',()=>{left=Number(leftSelect.value);if(left>right)right=left;drawQuery();});
  rightSelect.addEventListener('change',()=>{right=Number(rightSelect.value);if(right<left)left=right;drawQuery();});
  queryChoice.addEventListener('change',()=>{queryCase=Number(queryChoice.value);resetQuery();});
  foundation.querySelectorAll('.prefix-controls').forEach(e=>e.hidden=false);
  drawBuild();drawQuery();
})();
