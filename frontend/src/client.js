export async function request(path, body=null, token='', fetcher=fetch) {
  const options=body===null?{}:{method:'POST',headers:{'Content-Type':'application/json','X-Review-Token':token},body:JSON.stringify(body)};
  const response=await fetcher(path,options);
  const result=await response.json();
  if(!response.ok){const error=new Error(result.error||'Request failed');error.status=response.status;throw error;}
  return result;
}
export function filePayload(file){
  if(!file||file.size>8*1024*1024)throw new Error('Select an image smaller than 8 MB.');
  return new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve({filename:file.name,image:reader.result.split(',')[1]});reader.onerror=()=>reject(new Error('Could not read image'));reader.readAsDataURL(file);});
}
