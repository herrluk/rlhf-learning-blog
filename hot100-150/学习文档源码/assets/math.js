/* 动态演示的说明文字沿用静态正文排版，不触碰代码及播放器数据。 */
window.StudyMath=(()=>{
  const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#x27;');
  const run=/[A-Za-z0-9_αβγθλπΣ∞][A-Za-z0-9_αβγθλπΣ∞ \t.\[\](){}+*/=<>!,:^%²³ⁿ−×÷≤≥≠→…-]*|[\[({][A-Za-z0-9_αβγθλπΣ∞ \t.\[\](){}+*/=<>!,:^%²³ⁿ−×÷≤≥≠→…-]+/g;
  function formula(s){
    const ts=s.match(/\d+(?:\.\d+)?|[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)*|<=|>=|!=|==|\*\*|\s+|./gs)||[],out=[];
    for(let i=0;i<ts.length;i++){
      const t=ts[i];
      if(/^\s+$/.test(t)){out.push('<mspace width="0.18em"></mspace>');continue;}
      if((t==='^'||t==='**')&&out.length&&i+1<ts.length){
        while(out.at(-1)?.startsWith('<mspace'))out.pop();
        while(/^\s+$/.test(ts[i+1]||''))i++;
        let exponent=ts[++i];
        if(exponent==='('||exponent==='{'){
          const end=exponent==='('?')':'}',open=exponent,parts=[];let depth=1;
          while(i+1<ts.length&&depth){const item=ts[++i];if(item===open)depth++;if(item===end)depth--;if(depth)parts.push(item);}exponent=parts.join('');
        }
        out[out.length-1]='<msup>'+out.at(-1)+'<mrow>'+formula(exponent)+'</mrow></msup>';
      }else if('²³ⁿ'.includes(t)&&out.length)out[out.length-1]='<msup>'+out.at(-1)+formula({'²':'2','³':'3','ⁿ':'n'}[t])+'</msup>';
      else if(/^\d+(?:\.\d+)?$/.test(t))out.push('<mn>'+t+'</mn>');
      else if(/^[A-Za-z_][A-Za-z_0-9.]*$/.test(t)){
        if(t.length===1)out.push('<mi>'+t+'</mi>');
        else if(['log','min','max','gcd','lcm','abs','sqrt','sin','cos'].includes(t))out.push('<mi mathvariant="normal">'+t+'</mi>');
        else if(['mn','nk','nm'].includes(t))out.push([...t].map(x=>'<mi>'+x+'</mi>').join(''));
        else out.push('<mi class="math-identifier" mathvariant="normal">'+esc(t)+'</mi>');
      }else out.push('<mo>'+esc({'<=':'≤','>=':'≥','!=':'≠','==':'=','*':'×'}[t]||t)+'</mo>');
    }return out.join('');
  }
  function text(s){
    let changed=false,cursor=0,out='';
    for(const m of s.matchAll(run)){
      out+=esc(s.slice(cursor,m.index));cursor=m.index+m[0].length;
      const core=m[0].replace(/[ \t.,:]+$/g,''),tail=m[0].slice(core.length);
      if(!core||/\b(?:Python|Hot|Hot100|LeetCode|API|HTML|PDF|JavaScript|BFS|DFS|LRU|LFU|DP|IP|vs)\b/.test(core)||!/[A-Za-z_αβγθλπΣ∞+*/=<>^²³ⁿ−×÷≤≥≠]/.test(core)){out+=esc(m[0]);continue;}
      const calls=[...core.matchAll(/([A-Za-z_][A-Za-z_0-9.]*)\s*\(/g)].map(m=>m[1]);
      if(calls.some(name=>name.length>1&&!['log','min','max','gcd','lcm','abs','sqrt','floor'].includes(name))||(core.includes('^')&&(s.includes('异或')||core.includes('^=')))){out+='<code class="inline-identifier">'+esc(core)+'</code>'+esc(tail);changed=true;continue;}
      if(/^[A-Za-z_][A-Za-z_0-9.]*$/.test(core)&&core.length>1){out+='<code class="inline-identifier">'+esc(core)+'</code>'+esc(tail);changed=true;continue;}
      if(/^[A-Za-z]+(?:\s+[A-Za-z]+)+$/.test(core)&&!core.split(/\s+/).includes('log')){out+=esc(m[0]);continue;}
      out+='<span class="math-run'+(core.length>48&&/[=≤≥<>]/.test(core)?' math-display':'')+'" data-math-source="'+esc(core)+'"><math xmlns="http://www.w3.org/1998/Math/MathML" aria-label="'+esc(core)+'"><mrow>'+formula(core)+'</mrow></math></span>'+esc(tail);changed=true;
    }
    out+=esc(s.slice(cursor));
    return changed?'<span class="notation-text" data-notation-source="'+esc(s)+'">'+out+'</span>':null;
  }
  function typeset(root){
    const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT),nodes=[];let node;
    while(node=walker.nextNode()){
      const p=node.parentElement;
      if(p&&!p.closest('pre,code,script,style,textarea,button,select,nav,aside,a,math,.notation-text,.math-run')&&p.closest('p,li,td,th,h3,h4,h5,summary,.equation,.status'))nodes.push(node);
    }
    for(const node of nodes){const html=text(node.data);if(html){const template=document.createElement('template');template.innerHTML=html;node.replaceWith(template.content);}}
  }
  return {typeset};
})();
