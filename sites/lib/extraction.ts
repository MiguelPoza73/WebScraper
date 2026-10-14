export type Result = { headers: string[][]; rows: (string | null)[][]; method: string };
export type Field = { name: string; selector: string; attribute: string };
export function tablesIn(doc: Document) { return Array.from(doc.querySelectorAll('table')); }
export function extractTable(table: Element): Result {
 const grid: string[][]=[];let count=0;
 for(const row of Array.from(table.querySelectorAll('tr')).filter(r=>r.closest('table')===table)){
  const cells=Array.from(row.children).filter(c=>['TH','TD'].includes(c.tagName));if(!cells.length)continue;
  if(grid.length===count&&cells.every(c=>c.tagName==='TH'))count++;
  if(cells.some(c=>(c.getAttribute('rowspan')||'1')!=='1'||(c.getAttribute('colspan')||'1')!=='1'))throw Error('Esta tabla tiene celdas combinadas. Usa selectores CSS para conservar los textos sin expandir celdas.');
  grid.push(cells.map(c=>c.textContent??''));
 }
 if(!grid.length)throw Error('La tabla no contiene filas extraíbles.');
 if(grid.some(r=>r.length!==grid[0].length))throw Error('La tabla tiene filas de distinta longitud. Usa selectores CSS.');
 return {headers:count?grid.slice(0,count):[grid[0].map((_,i)=>String(i))],rows:grid.slice(count),method:'Tabla HTML'};
}
export function extractCss(doc: Document, selector: string, fields: Field[]): Result {
 if(!selector.trim()||!fields.length||fields.some(f=>!f.name.trim()))throw Error('Define un selector y un nombre para cada campo.');
 try {
 const records=Array.from(doc.querySelectorAll(selector));if(records.length>100000)throw Error('Hay más de 100.000 registros. Acota el selector.');
 const rows=records.map(row=>fields.map(f=>{
  const matches=f.selector?Array.from(row.querySelectorAll(f.selector)):[row];
  if(matches.length>1)throw Error(`El campo «${f.name}» encuentra varios elementos por fila. Ajusta el selector.`);
  return !matches[0]?null:f.attribute?matches[0].getAttribute(f.attribute):matches[0].textContent??'';
 }));return {headers:[fields.map(f=>f.name)],rows,method:`CSS: ${selector}`};
 }catch(e){if(e instanceof Error&&e.name==='SyntaxError')throw Error('Selector CSS inválido.');throw e}
}
export function csvText(result: Result) {
 const escape=(v:string|null)=>{const s=v??'';return /[",\n\r]/.test(s)?'"'+s.replaceAll('"','""')+'"':s};
 return '\uFEFF'+[...result.headers,...result.rows].map(r=>r.map(escape).join(',')).join('\n')+'\n';
}
export function validateExcel(result: Result){
 if(result.rows.length+result.headers.length>1048576||result.headers[0].length>16384)throw Error('Los datos superan los límites de Excel. Descarga CSV.');
 for(const row of [...result.headers,...result.rows])for(const value of row)if(value!==null){if(value.length>32767)throw Error('Una celda supera 32.767 caracteres. Descarga CSV para conservarla.');if(/[\x00-\x08\x0b\x0c\x0e-\x1f]/.test(value))throw Error('Una celda contiene caracteres no admitidos por Excel. Descarga CSV.');}
}
