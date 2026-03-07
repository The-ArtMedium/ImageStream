

let audioContext=null;
let isPlaying=false;
let startTime=0;
let pauseOffset=0;
let activeSources=[];
function getAudioContext(){
  if(!audioContext)
    audioContext=new(window.AudioContext||window.webkitAudioContext)();
  return audioContext;
}
function playAll(){
  if(isPlaying)return;
  const ctx=getAudioContext();
  isPlaying=true;
  startTime=ctx.currentTime-pauseOffset;
  layers.forEach(layer=>{
    if(!layer.audioBuffer||layer.muted)return;
    const source=ctx.createBufferSource();
    source.buffer=layer.audioBuffer;
    const gain=ctx.createGain();
    gain.gain.value=layer.volume;
    source.connect(gain);
    gain.connect(ctx.destination);
    source.start(0,pauseOffset);
    activeSources.push(source);
  });
  requestAnimationFrame(updateTimer);
}
function pauseAll(){
  if(!isPlaying)return;
  pauseOffset=getAudioContext().currentTime-startTime;
  stopSources();isPlaying=false;
}
function stopAll(){
  stopSources();isPlaying=false;pauseOffset=0;
  document.getElementById("currentTime").textContent="00:00";
  document.getElementById("seekBar").value=0;
}
function stopSources(){
  activeSources.forEach(s=>{try{s.stop();}catch(e){}});
  activeSources=[];
}
function updateTimer(){
  if(!isPlaying)return;
  const elapsed=getAudioContext().currentTime-startTime;
  document.getElementById("currentTime").textContent=formatTime(elapsed);
  const maxDuration=Math.max(...layers.map(l=>l.audioBuffer?.duration||0));
  if(maxDuration>0){
    document.getElementById("seekBar").value=(elapsed/maxDuration)*100;
    document.getElementById("totalTime").textContent=formatTime(maxDuration);
  }
  requestAnimationFrame(updateTimer);
}
function formatTime(seconds){
  const m=Math.floor(seconds/60).toString().padStart(2,"0");
  const s=Math.floor(seconds%60).toString().padStart(2,"0");
  return m+":"+s;
}
document.getElementById("btnPlay")?.addEventListener("click",playAll);
document.getElementById("btnPause")?.addEventListener("click",pauseAll);
document.getElementById("btnStop")?.addEventListener("click",stopAll);
