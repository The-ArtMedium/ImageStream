

let layers=[];
let layerCount=0;
const MAX_LAYERS=8;
function initLayers(){addLayer();addLayer();}
function addLayer(){
  if(layers.length>=MAX_LAYERS)return;
  layerCount++;
  const id=layerCount;
  const layer={id,name:t("layer")+" "+id,
    audioBuffer:null,audioFile:null,
    volume:1,muted:false,clipStart:0,clipEnd:null};
  layers.push(layer);
  renderLayer(layer);
}
function renderLayer(layer){
  const container=document.getElementById("layersContainer");
  const el=document.createElement("div");
  el.className="layer layer-color-"+layer.id;
  el.id="layer-"+layer.id;
  el.setAttribute("role","region");
  el.setAttribute("aria-label",layer.name);
  el.innerHTML=`
    <span class="layer__icon" aria-hidden="true">🎵</span>
    <span class="layer__name">${layer.name}</span>
    <div class="layer__waveform">
      <canvas class="waveform-canvas" id="canvas-${layer.id}"></canvas>
    </div>
    <div class="layer__controls">
      <input type="range" id="vol-${layer.id}"
        class="volume-slider" min="0" max="1" step="0.01" value="1"
        aria-label="Volume" title="Volume"
        onchange="setVolume(${layer.id},this.value)"/>
      <button class="btn" title="Mute" aria-label="Mute"
        onclick="toggleMute(${layer.id})">
        <span class="icon">🔊</span>
      </button>
      <button class="btn" title="Clip" aria-label="Clip"
        onclick="clipLayer(${layer.id})">
        <span class="icon">✂</span><span>Clip</span>
      </button>
      <button class="btn" title="Remove" aria-label="Remove"
        onclick="confirmRemoveLayer(${layer.id})">
        <span class="icon">🗑</span>
      </button>
    </div>`;
  container.appendChild(el);
}
function setVolume(id,value){
  const layer=layers.find(l=>l.id===id);
  if(layer)layer.volume=parseFloat(value);
}
function toggleMute(id){
  const layer=layers.find(l=>l.id===id);
  if(!layer)return;
  layer.muted=!layer.muted;
  const el=document.getElementById("layer-"+id);
  if(el)el.classList.toggle("layer--muted",layer.muted);
}
function confirmRemoveLayer(id){
  if(confirm(t("confirmRemove")))removeLayer(id);
}
function removeLayer(id){
  layers=layers.filter(l=>l.id!==id);
  const el=document.getElementById("layer-"+id);
  if(el)el.remove();
}
function clipLayer(id){alert("Clip editor coming soon.");}
function drawWaveform(id,audioBuffer){
  const canvas=document.getElementById("canvas-"+id);
  if(!canvas)return;
  const ctx=canvas.getContext("2d");
  const data=audioBuffer.getChannelData(0);
  const width=canvas.offsetWidth||300;
  const height=canvas.offsetHeight||36;
  canvas.width=width;canvas.height=height;
  ctx.clearRect(0,0,width,height);
  ctx.fillStyle="#f5a623";
  const step=Math.ceil(data.length/width);
  const amp=height/2;
  for(let i=0;i<width;i++){
    let min=1,max=-1;
    for(let j=0;j<step;j++){
      const val=data[(i*step)+j]||0;
      if(val<min)min=val;if(val>max)max=val;
    }
    ctx.fillRect(i,(1+min)*amp,1,Math.max(1,(max-min)*amp));
  }
}
document.getElementById("btnAddLayer")?.addEventListener("click",()=>{
  if(layers.length<MAX_LAYERS)addLayer();
});
