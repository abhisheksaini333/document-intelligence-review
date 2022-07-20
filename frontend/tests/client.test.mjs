import assert from 'node:assert/strict';
import { request, filePayload } from '../src/client.js';
const calls=[];
const fetcher=async(path,options)=>{calls.push({path,options});return {ok:true,json:async()=>({version:2})}};
assert.equal((await request('/api/x',{x:1},'abc',fetcher)).version,2);
assert.equal(calls[0].options.headers['X-Review-Token'],'abc');
await assert.rejects(request('/api/x',null,'',async()=>({ok:false,status:409,json:async()=>({error:'changed'})})),/changed/);
assert.throws(()=>filePayload({size:9000000}),/8 MB/);
console.log('client request and upload limits passed');
