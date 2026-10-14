import ipaddr from 'ipaddr.js';
import robotsParser from 'robots-parser';
const AGENT='LearningTableExtractor/1.0';
const LIMIT=8_000_000;
export function publicUrl(input:string){
 let url:URL;try{url=new URL(input)}catch{throw Error('La URL tiene un formato inválido.')}
 if(!['http:','https:'].includes(url.protocol)||url.username||url.password||!url.hostname||url.port&&!['80','443'].includes(url.port))throw Error('Introduce una URL http o https pública, sin credenciales, con puerto 80 o 443.');
 const host=url.hostname.replace(/^\[|\]$/g,'');
 if(!host.includes('.')&&!host.includes(':')||/\.(local|localhost|internal|test|invalid)$/i.test(host)||host==='localhost')throw Error('La dirección debe pertenecer a una web pública.');
 if(ipaddr.isValid(host)&&ipaddr.process(host).range()!=='unicast')throw Error('La dirección debe pertenecer a una web pública.');
 return url;
}
async function validateHost(url:URL){
 const host=url.hostname.replace(/^\[|\]$/g,'');if(ipaddr.isValid(host))return;
 const addresses=await Promise.all(['A','AAAA'].map(async type=>{
  const response=await fetch('https://cloudflare-dns.com/dns-query?name='+encodeURIComponent(host)+'&type='+type,{headers:{accept:'application/dns-json'},signal:AbortSignal.timeout(6000)});
  if(!response.ok)throw Error('No se puede resolver la dirección de origen.');
  const data=await response.json() as {Answer?:{type:number;data:string}[]};return(data.Answer||[]).filter(x=>x.type===1||x.type===28).map(x=>x.data);
 }));const ips=addresses.flat();if(!ips.length||ips.some(a=>!ipaddr.isValid(a)||ipaddr.process(a).range()!=='unicast'))throw Error('La dirección debe resolverse a una web pública.');
}
async function readLimited(response:Response){
 if(Number(response.headers.get('content-length')||0)>LIMIT)throw Error('La página supera el límite de 8 MB.');
 const reader=response.body?.getReader();if(!reader)return '';
 const chunks:Uint8Array[]=[];let size=0;
 while(true){const {value,done}=await reader.read();if(done)break;size+=value.length;if(size>LIMIT){await reader.cancel();throw Error('La página supera el límite de 8 MB.')}chunks.push(value)}
 const bytes=new Uint8Array(size);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.length}
 const charset=response.headers.get('content-type')?.match(/charset\s*=\s*["']?([^;"'\s]+)/i)?.[1]||'utf-8';try{return new TextDecoder(charset).decode(bytes)}catch{return new TextDecoder().decode(bytes)}
}
async function request(input:string){const url=publicUrl(input);await validateHost(url);return fetch(url.href,{redirect:'manual',headers:{'User-Agent':AGENT,accept:'text/html,text/plain;q=0.9'},signal:AbortSignal.timeout(20000)})}
async function robotsFile(origin:string){let url=origin+'/robots.txt';for(let i=0;i<4;i++){const r=await request(url);if([301,302,303,307,308].includes(r.status)){const next=r.headers.get('location');await r.body?.cancel();if(!next)throw Error('robots.txt redirige sin destino.');url=new URL(next,url).href;continue}if([404,410].includes(r.status)){await r.body?.cancel();return ''}if(r.status!==200){await r.body?.cancel();throw Error(`No se pudo verificar robots.txt (HTTP ${r.status}).`)}return readLimited(r)}throw Error('Demasiadas redirecciones en robots.txt.')}
export async function fetchPage(input:string){let url=publicUrl(input).href;const checked=new Map<string,string>();
 for(let i=0;i<6;i++){
  const parsed=publicUrl(url);let robots=checked.get(parsed.origin);if(robots===undefined){robots=await robotsFile(parsed.origin);checked.set(parsed.origin,robots)}
  const policy=robotsParser(parsed.origin+'/robots.txt',robots);if(policy.isAllowed(url,AGENT)===false)throw Error('robots.txt no permite extraer esta página.');
  const delay=Math.max(2,policy.getCrawlDelay(AGENT)||0);if(delay>20)throw Error('La fuente requiere un intervalo de acceso superior al permitido por esta consulta.');await new Promise(r=>setTimeout(r,delay*1000));
  const response=await request(url);if([301,302,303,307,308].includes(response.status)){const next=response.headers.get('location');await response.body?.cancel();if(!next)throw Error('Redirección sin destino.');url=new URL(next,url).href;continue}
  if(response.status!==200){await response.body?.cancel();throw Error(`La fuente respondió HTTP ${response.status}. No se intentará eludir el bloqueo.`)}
  if(!response.headers.get('content-type')?.toLowerCase().includes('html')){await response.body?.cancel();throw Error('La respuesta no es una página HTML compatible.')}
  return {html:await readLimited(response),url};
 }throw Error('Demasiadas redirecciones.');
}
