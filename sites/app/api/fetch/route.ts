import {fetchPage} from '../../../lib/source';
export async function POST(request:Request){
 try{
 if(Number(request.headers.get('content-length')||0)>4096)return Response.json({error:'Solicitud demasiado grande.'},{status:413});
 const data=await request.json() as {url?:unknown;allowed?:unknown};if(typeof data.url!=='string'||data.url.length>2048||data.allowed!==true)return Response.json({error:'Introduce una URL y confirma las condiciones de la fuente.'},{status:400});
 const result=await fetchPage(data.url);return Response.json(result,{headers:{'Cache-Control':'no-store'}});
 }catch(error){const msg=error instanceof Error?error.message:'No se pudo consultar la página.';return Response.json({error:/timeout|abort|fetch failed/i.test(msg)?'No se pudo conectar con la fuente dentro del tiempo permitido.':msg},{status:400,headers:{'Cache-Control':'no-store'}})}
}
