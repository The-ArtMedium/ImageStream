

function saveProject(){
  const project={
    version:"1.0",name:"LocalBeat Project",
    created:new Date().toISOString(),
    layers:layers.map(l=>({
      id:l.id,name:l.name,volume:l.volume,muted:l.muted,
      audioFile:l.audioFile,clipStart:l.clipStart,clipEnd:l.clipEnd
    }))
  };
  const blob=new Blob([JSON.stringify(project,null,2)],{type:"application/json"});
  const url=URL.createObjectURL(blob);
  const a=document.createElement("a");
  a.href=url;a.download="localbeat-project.json";a.click();
  URL.revokeObjectURL(url);
}
function exportToLocalEdit(){
  const ctx=getAudioContext();
  const maxDuration=Math.max(...layers.map(l=>l.audioBuffer?.duration||0));
  if(maxDuration===0){alert("No audio to export. Add some sounds first.");return;}
  const sampleRate=ctx.sampleRate;
  const frameCount=Math.ceil(maxDuration*sampleRate);
  const offline=new OfflineAudioContext(2,frameCount,sampleRate);
  layers.forEach(layer=>{
    if(!layer.audioBuffer||layer.muted)return;
    const source=offline.createBufferSource();
    source.buffer=layer.audioBuffer;
    const gain=offline.createGain();
    gain.gain.value=layer.volume;
    source.connect(gain);gain.connect(offline.destination);
    source.start(0,layer.clipStart||0);
  });
  offline.startRendering().then(rendered=>{
    const wav=audioBufferToWav(rendered);
    const blob=new Blob([wav],{type:"audio/wav"});
    const url=URL.createObjectURL(blob);
    const a=document.createElement("a");
    a.href=url;a.download="localbeat-export.wav";a.click();
    URL.revokeObjectURL(url);
    alert("Exported! Import localbeat-export.wav into LocalEdit audio track.");
  });
}
function audioBufferToWav(buffer){
  const numChannels=buffer.numberOfChannels;
  const sampleRate=buffer.sampleRate;
  const bitDepth=16;
  const blockAlign=numChannels*(bitDepth/8);
  const byteRate=sampleRate*blockAlign;
  const dataSize=buffer.length*blockAlign;
  const ab=new ArrayBuffer(44+dataSize);
  const view=new DataView(ab);
  const ws=(o,s)=>{for(let i=0;i<s.length;i++)view.setUint8(o+i,s.charCodeAt(i));};
  ws(0,"RIFF");view.setUint32(4,36+dataSize,true);ws(8,"WAVE");
  ws(12,"fmt ");view.setUint32(16,16,true);view.setUint16(20,1,true);
  view.setUint16(22,numChannels,true);view.setUint32(24,sampleRate,true);
  view.setUint32(28,byteRate,true);view.setUint16(32,blockAlign,true);
  view.setUint16(34,bitDepth,true);ws(36,"data");view.setUint32(40,dataSize,true);
  let offset=44;
  for(let i=0;i<buffer.length;i++){
    for(let ch=0;ch<numChannels;ch++){
      const s=Math.max(-1,Math.min(1,buffer.getChannelData(ch)[i]));
      view.setInt16(offset,s<0?s*0x8000:s*0x7FFF,true);
      offset+=2;
    }
  }
  return ab;
}
