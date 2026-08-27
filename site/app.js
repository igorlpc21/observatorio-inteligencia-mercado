const SOURCES = {
  indicators: '../dados/tratados/indicadores_observatorio.csv',
  matches: '../dados/tratados/comparacoes_candidatas_milk_fortali.csv'
};

const state = { indicators: [], matches: [], shown: 10 };

function parseCSV(text) {
  const rows = []; let row = [], value = '', quoted = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i], next = text[i + 1];
    if (c === '"' && quoted && next === '"') { value += '"'; i++; }
    else if (c === '"') quoted = !quoted;
    else if (c === ',' && !quoted) { row.push(value); value = ''; }
    else if ((c === '\n' || c === '\r') && !quoted) {
      if (c === '\r' && next === '\n') i++;
      row.push(value); if (row.some(v => v !== '')) rows.push(row); row = []; value = '';
    } else value += c;
  }
  if (value || row.length) { row.push(value); rows.push(row); }
  const headers = rows.shift().map(h => h.replace(/^\uFEFF/, ''));
  return rows.map(r => Object.fromEntries(headers.map((h, i) => [h, r[i] ?? ''])));
}

const number = value => Number(String(value).replace(',', '.')) || 0;
const fmt = value => new Intl.NumberFormat('pt-BR').format(value);
const clean = value => String(value);

function renderKPIs() {
  const productSources = state.indicators.filter(d => d.nivel_dado === 'PRODUTO');
  const total = state.indicators.reduce((sum, d) => sum + number(d.registros_publicos), 0);
  const unique = state.indicators.reduce((sum, d) => sum + number(d.itens_unicos), 0);
  const high = state.matches.filter(d => number(d.similaridade_percentual) >= 85).length;
  const cards = [
    ['REGISTROS OBSERVADOS', fmt(total), '5 empresas mapeadas'],
    ['ITENS ÚNICOS', fmt(unique), 'Conforme fonte pública'],
    ['CATÁLOGOS EM NÍVEL PRODUTO', productSources.length, 'Milk, Fortali e Casa Garcia'],
    ['PARES DE ALTA SIMILARIDADE', high, 'Ainda sujeitos à validação']
  ];
  document.querySelector('#kpis').innerHTML = cards.map(([label, value, note]) => `<article class="kpi"><span>${label}</span><strong>${value}</strong><small>${note}</small></article>`).join('');
}

function svgEl(name, attrs = {}, text = '') {
  const el = document.createElementNS('http://www.w3.org/2000/svg', name);
  Object.entries(attrs).forEach(([k, v]) => el.setAttribute(k, v)); el.textContent = text; return el;
}

function renderCoverage() {
  const data = [...state.indicators].sort((a,b) => number(b.itens_unicos)-number(a.itens_unicos));
  const width=680, rowH=52, left=180, right=55, max=Math.max(...data.map(d=>number(d.itens_unicos)));
  const svg=svgEl('svg',{viewBox:`0 0 ${width} ${data.length*rowH+28}`});
  data.forEach((d,i)=>{ const y=i*rowH+9, w=(number(d.itens_unicos)/max)*(width-left-right);
    svg.append(svgEl('text',{x:0,y:y+17,class:'bar-label'},clean(d.empresa).replace(' Distribuidora','')));
    svg.append(svgEl('rect',{x:left,y,width:width-left-right,height:24,fill:'#e1e3dc'}));
    svg.append(svgEl('rect',{x:left,y,width:w,height:24,fill:i===0?'#1f5846':'#8ca697'}));
    svg.append(svgEl('text',{x:left+w+8,y:y+17,class:'bar-value'},fmt(number(d.itens_unicos))));
  }); document.querySelector('#coverageChart').replaceChildren(svg);
}

function renderQuality() {
  const data=state.indicators.filter(d=>d.taxa_medida_preenchida_pct).sort((a,b)=>number(b.taxa_medida_preenchida_pct)-number(a.taxa_medida_preenchida_pct));
  const width=500,rowH=76,left=150,right=35,svg=svgEl('svg',{viewBox:`0 0 ${width} ${data.length*rowH+35}`});
  [0,25,50,75,100].forEach(t=>{const x=left+(t/100)*(width-left-right);svg.append(svgEl('line',{x1:x,y1:0,x2:x,y2:data.length*rowH,stroke:'#d7d8d1'}));svg.append(svgEl('text',{x,y:data.length*rowH+18,'text-anchor':'middle',class:'axis-label'},`${t}%`))});
  data.forEach((d,i)=>{const y=i*rowH+29,v=number(d.taxa_medida_preenchida_pct),x=left+(v/100)*(width-left-right);svg.append(svgEl('text',{x:0,y:y+4,class:'bar-label'},clean(d.empresa).replace(' Distribuidora','').replace(' Gourmet','')));svg.append(svgEl('line',{x1:left,y1:y,x2:width-right,y2:y,stroke:'#aeb4ae'}));svg.append(svgEl('circle',{cx:x,cy:y,r:8,fill:'#f07345',stroke:'#fff','stroke-width':3}));svg.append(svgEl('text',{x:x,y:y-14,'text-anchor':'middle',class:'bar-value'},`${v.toFixed(1)}%`))});document.querySelector('#qualityChart').replaceChildren(svg);
}

function renderDistribution() {
  const groups=[['Alta',d=>number(d.similaridade_percentual)>=85,''],['Média',d=>number(d.similaridade_percentual)>=70&&number(d.similaridade_percentual)<85,'medium'],['Exploratória',d=>number(d.similaridade_percentual)<70,'low']];
  document.querySelector('#distribution').innerHTML=groups.map(([label,test,cls])=>{const count=state.matches.filter(test).length;return `<div class="dist-row ${cls}"><span>${label}</span><i class="dist-track"><i class="dist-fill" style="width:${count/state.matches.length*100}%"></i></i><b>${count}</b></div>`}).join('');
  document.querySelector('#candidateCount').textContent=state.matches.length;
  const unique=new Set(state.matches.map(d=>d.id_milk)).size, avg=state.matches.reduce((s,d)=>s+number(d.similaridade_percentual),0)/state.matches.length;
  document.querySelector('#insightText').textContent=`Só 3 pares atingem alta similaridade. Os ${state.matches.length} candidatos cobrem ${unique} produtos Milk, com média de ${avg.toFixed(1).replace('.',',')}%. Priorize validação de marca, sabor e aplicação.`;
}

function filteredMatches(){const cls=document.querySelector('#classFilter').value,q=document.querySelector('#searchInput').value.trim().toLocaleUpperCase('pt-BR');return state.matches.filter(d=>{const score=number(d.similaridade_percentual);const label=score>=85?'Alta':score>=70?'Média':'Baixa';return (cls==='Todas'||cls===label)&&(!q||`${d.produto_milk} ${d.produto_fortali}`.toLocaleUpperCase('pt-BR').includes(q))}).sort((a,b)=>number(b.similaridade_percentual)-number(a.similaridade_percentual))}
function renderTable(){const all=filteredMatches(),rows=all.slice(0,state.shown);document.querySelector('#matchesBody').innerHTML=rows.map(d=>{const score=number(d.similaridade_percentual),label=score>=85?'Alta':score>=70?'Média':'Exploratória',cls=score>=85?'high':score>=70?'medium':'low';return `<tr><td>${clean(d.produto_milk)}</td><td>${clean(d.produto_fortali)}</td><td>${fmt(number(d.quantidade_base))} ${d.unidade_base}</td><td><span class="score">${score.toFixed(1).replace('.',',')}%<i style="--score:${score}%"></i></span></td><td><span class="badge ${cls}">${label}</span></td></tr>`}).join('')||'<tr><td colspan="5">Nenhum par encontrado para este filtro.</td></tr>';document.querySelector('#resultCount').textContent=`${Math.min(rows.length,all.length)} de ${all.length} resultados`;document.querySelector('#loadMore').hidden=rows.length>=all.length}

async function init(){try{const [indicators,matches]=await Promise.all(Object.values(SOURCES).map(url=>fetch(url).then(r=>{if(!r.ok)throw new Error(url);return r.text()})));state.indicators=parseCSV(indicators);state.matches=parseCSV(matches);renderKPIs();renderCoverage();renderQuality();renderDistribution();renderTable()}catch(error){document.querySelector('#kpis').innerHTML='<article class="kpi"><strong>Dados indisponíveis</strong><small>Abra o site por um servidor local para carregar os CSVs.</small></article>';console.error(error)}}
document.querySelector('#classFilter').addEventListener('change',()=>{state.shown=10;renderTable()});document.querySelector('#searchInput').addEventListener('input',()=>{state.shown=10;renderTable()});document.querySelector('#loadMore').addEventListener('click',()=>{state.shown+=10;renderTable()});init();
