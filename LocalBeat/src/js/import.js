

function openImport(){
  const overlay=document.getElementById("modalOverlay");
  const content=document.getElementById("modalContent");
  content.innerHTML=`<h2 style="color:var(--accent);margin-bottom:var(--space-md)">
    📂 Import</h2>
    <div style="display:flex;flex-direction:column;gap:var(--space-md)">
      <button class="btn btn--export" style="width:100%"
        onclick="importFromDevice()">💾 From Your Device</button>
      <div style="color:var(--text-muted);text-align:center;font-size:0.85em">
        — or from free libraries (needs internet) —</div>
      <button class="btn" style="width:100%"
        onclick="window.open('https://freesound.org','_blank')">
        🌐 Freesound.org</button>
      <button class="btn" style="width:100%"
        onclick="window.open('https://sound-effects.bbcrewind.co.uk','_blank')">
        🌐 BBC Sound Effects</button>
      <button class="btn" style="width:100%"
        onclick="window.open('https://www.nasa.gov/audio-and-ringtones','_blank')">
        🌐 NASA Audio Library</button>
      <button class="btn" style="margin-top:var(--space-sm);width:100%"
        onclick="closeModal()">✕ Cancel</button>
    </div>`;
  overlay.classList.remove("hidden");
}
function importFromDevice(){
  const input=document.createElement("input");
  input.type="file";input.accept="audio/*";
  input.onchange=e=>{
    const file=e.target.files[0];if(!file)return;
    const reader=new FileReader();
    reader.onload=ev=>{
      const ctx=getAudioContext();
      ctx.decodeAudioData(ev.target.result).then(decoded=>{
        if(layers.length===0)addLayer();
        const layer=layers[layers.length-1];
        layer.audioBuffer=decoded;layer.audioFile=file.name;
        drawWaveform(layer.id,decoded);
        closeModal();
      });
    };
    reader.readAsArrayBuffer(file);
  };
  input.click();
}
