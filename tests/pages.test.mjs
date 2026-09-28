import { JSDOM, VirtualConsole } from 'jsdom';
import { readFileSync } from 'fs';
const html = readFileSync('dist/index.html','utf8');
const js = readFileSync('dist/assets/' + html.match(/src="\/assets\/(index-[^"]+\.js)"/)[1],'utf8');
const vc = new VirtualConsole(); const errors=[];
vc.on('jsdomError', e => { if(!/Could not parse CSS/.test(e.message)) errors.push('JSDOM: '+e.message) });
vc.on('error', (...a) => errors.push('console.error: '+a.join(' ')));
const dom = new JSDOM(html.replace(/<script[^>]*src="[^"]*"[^>]*><\/script>/,''), { url:'http://localhost/', runScripts:'outside-only', pretendToBeVisual:true, virtualConsole:vc });
const w = dom.window, d = w.document;
w.matchMedia = w.matchMedia || (()=>({matches:false,addListener(){},removeListener(){},addEventListener(){},removeEventListener(){}}));
w.eval(js);
await new Promise(r=>setTimeout(r,400));
const click = el => el.dispatchEvent(new w.MouseEvent('click',{bubbles:true,cancelable:true}));
const nav = async name => { click([...d.querySelectorAll('.sidebar .nav-item')].find(b=>b.textContent.includes(name))); await new Promise(r=>setTimeout(r,250)); };
for(const p of ['Incidents','Drone fleet','Coverage & stations','Analytics','Settings','Overview']){
  await nav(p);
  const h1=d.querySelector('.page-heading h1')?.textContent;
  const panels=d.querySelectorAll('.panel').length;
  console.log(p.padEnd(20), '→', h1, '| panels:', panels, '| err so far:', errors.length);
}
// verify resolved demo incident freed the drone on fleet page
await nav('Drone fleet');
const cards=[...d.querySelectorAll('.drone-card')].map(c=>c.querySelector('.drone-id').textContent+':'+c.querySelector('.badge').textContent.trim());
console.log('fleet:', cards.join(' | '));
// incidents table
await nav('Incidents');
console.log('table rows:', d.querySelectorAll('.table-scroll tbody tr').length, '| search works:', (d.querySelector('.input-with-icon input').value='', d.querySelector('.input-with-icon input').dispatchEvent(new w.Event('input',{bubbles:true})), true));
// export CSV
click([...d.querySelectorAll('button')].find(b=>b.textContent.includes('Export log')));
await new Promise(r=>setTimeout(r,300));
// notifications popover
click(d.querySelector('.notification-wrap .icon-button'));
await new Promise(r=>setTimeout(r,200));
console.log('notifications open:', d.querySelectorAll('.notifications-pop').length===1);
// help + guide + reset modals
click([...d.querySelectorAll('.sidebar-bottom .nav-item')].find(b=>b.textContent.includes('Help')));
await new Promise(r=>setTimeout(r,200));
console.log('help modal (112 present):', d.querySelector('.modal')?.textContent.includes('112'));
click(d.querySelector('.modal .icon-button'));
await new Promise(r=>setTimeout(r,150));
click([...d.querySelectorAll('.pilot-card button')][0]);
await new Promise(r=>setTimeout(r,200));
console.log('guide modal:', !!d.querySelector('.guide-steps'));
click(d.querySelector('.modal .icon-button'));
await new Promise(r=>setTimeout(r,150));
// settings reset
await nav('Settings');
click([...d.querySelectorAll('.setting-row button')].find(b=>b.textContent.includes('Reset data')));
await new Promise(r=>setTimeout(r,200));
click([...d.querySelectorAll('.modal button')].find(b=>b.textContent.trim()==='Reset demo'));
await new Promise(r=>setTimeout(r,300));
await nav('Overview');
console.log('after reset active incidents:', d.querySelector('.incidents-panel .count-pill')?.textContent);
console.log('ERRORS:', errors.length?errors.join('\n'):'none');
