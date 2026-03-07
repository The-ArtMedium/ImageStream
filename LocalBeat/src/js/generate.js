

function openGenerate(){
  const overlay=document.getElementById("modalOverlay");
  const content=document.getElementById("modalContent");
  content.innerHTML=`<h2 style="color:var(--accent);margin-bottom:var(--space-md)">
    🎹 Generate Sound</h2>
    <div style="display:flex;flex-direction:column;gap:var(--space-md)">
      <div>
        <label style="color:var(--text-secondary);display:block;margin-bottom:4px">
          Frequency (Hz)</label>
        <input type="range" id="genFreq" min="80" max="1200" value="440"
          style="width:100%;accent-color:var(--accent)"
          oninput="document.getElementById('freqVal').textContent=this.value+'Hz'"/>
        <span id="freqVal" style="color:var(--accent)">440Hz</span>
      </div>
      <div>
        <label style="color:var(--text-secondary);display:block;margin-bottom:4px">
          Duration (seconds)</label>
        <input type="range" id="genDur" min="1" max="10" value="2"
          style="width:100%;accent-color:var(--accent)"
          oninput="document.getElementById('durVal').textContent=this.value+'s'"/>
        <span id="durVal" style="color:var(--accent)">2s</span>
      </div>
      <div>
        <label style="color:var(--text-secondary);display:block;margin-bottom:4px">
          Wave Type</label>
        <select id="genWave" style="background:var(--bg-elevated);
          color:var(--text-primary);border:1px solid var(--border);
          padding:var(--space-sm);border-radius:var(--radius);width:100%">
          <option value="sine">Sine — smooth, gentle</option>
          <option value="square">Square — sharp, buzzy</option>
          <option value="triangle">Triangle — soft, hollow</option>
          <option value="sawtooth">Sawtooth — bright, harsh</option>
        </select>
      </div>
      <button class="btn btn--export" style="width:100%" onclick="generateTone()">
        🎹 Generate and Add to Layer</button>
      <button class="btn" style="width:100%" onclick="closeModal()">✕ Cancel</button>
    </div>`;
  overlay.classList.remove("hidden");
}
function generateTone(){
  const freq=parseFloat(document.getElementById("genFreq").value);
  const dur=parseFloat(document.getElementById("genDur").value);
  const wave=document.getElementById("genWave").value;
  const ctx=getAudioContext();
  const sampleRate=ctx.sampleRate;
  const frameCount=sampleRate*dur;
  const buffer=ctx.createBuffer(1,frameCount,sampleRate);
  const data=buffer.getChannelData(0);
  for(let i=0;i<frameCount;i++){
    const t=i/sampleRate;
    const phase=2*Math.PI*freq*t;
    switch(wave){
      case"sine":data[i]=Math.sin(phase);break;
      case"square":data[i]=Math.sign(Math.sin(phase));break;
      case"triangle":data[i]=(2/Math.PI)*Math.asin(Math.sin(phase));break;
      case"sawtooth":data[i]=2*((freq*t)%1)-1;break;
    }
    const fadeLen=sampleRate*0.01;
    if(i<fadeLen)data[i]*=i/fadeLen;
    if(i>frameCount-fadeLen)data[i]*=(frameCount-i)/fadeLen;
  }
  if(layers.length===0)addLayer();
  const layer=layers[layers.length-1];
  layer.audioBuffer=buffer;
  layer.audioFile="Generated "+wave+" "+freq+"Hz";
  drawWaveform(layer.id,buffer);
  closeModal();
}
