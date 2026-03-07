

const SAMPLE_LIBRARY={
  beats:[
    {name:"Soft Kick",file:"samples/beats/soft-kick.wav",duration:"0:02"},
    {name:"Street Beat",file:"samples/beats/street-beat.wav",duration:"0:04"},
    {name:"Simple Hi-Hat",file:"samples/beats/hihat.wav",duration:"0:01"},
    {name:"Snare Basic",file:"samples/beats/snare.wav",duration:"0:01"}
  ],
  ambient:[
    {name:"Rain Soft",file:"samples/ambient/rain-soft.wav",duration:"0:08"},
    {name:"Wind Gentle",file:"samples/ambient/wind.wav",duration:"0:06"},
    {name:"Forest",file:"samples/ambient/forest.wav",duration:"0:10"}
  ],
  world:[
    {name:"Hand Drum",file:"samples/world/hand-drum.wav",duration:"0:04"},
    {name:"Simple Flute",file:"samples/world/flute.wav",duration:"0:05"},
    {name:"Shaker",file:"samples/world/shaker.wav",duration:"0:03"}
  ],
  tones:[
    {name:"Low Tone",file:"samples/tones/low.wav",duration:"0:03"},
    {name:"Mid Tone",file:"samples/tones/mid.wav",duration:"0:03"},
    {name:"High Tone",file:"samples/tones/high.wav",duration:"0:03"}
  ],
  fx:[
    {name:"Soft Swoosh",file:"samples/fx/swoosh.wav",duration:"0:02"},
    {name:"Bell",file:"samples/fx/bell.wav",duration:"0:02"},
    {name:"Fade In",file:"samples/fx/fadein.wav",duration:"0:03"}
  ]
};
function openSamples(){
  const overlay=document.getElementById("modalOverlay");
  const content=document.getElementById("modalContent");
  content.innerHTML=`<h2 style="color:var(--accent);margin-bottom:var(--space-md)">
    🥁 Sample Library</h2>
    <div style="display:flex;gap:var(--space-sm);flex-wrap:wrap;margin-bottom:var(--space-md)">
      ${["beats","ambient","world","tones","fx"].map(cat=>`
        <button class="btn" onclick="showCategory('${cat}')">
          ${categoryIcon(cat)} ${cat}</button>`).join("")}
    </div>
    <div id="sampleList"></div>
    <button class="btn" style="margin-top:var(--space-md);width:100%"
      onclick="closeModal()">✕ Close</button>`;
  overlay.classList.remove("hidden");
  showCategory("beats");
}
function categoryIcon(cat){
  return{beats:"🥁",ambient:"🌊",world:"🌍",tones:"🎹",fx:"⚡"}[cat]||"🎵";
}
function showCategory(cat){
  const list=document.getElementById("sampleList");
  const samples=SAMPLE_LIBRARY[cat]||[];
  list.innerHTML=samples.map(s=>`
    <div style="display:flex;align-items:center;gap:var(--space-sm);
      padding:var(--space-sm);border-bottom:1px solid var(--border)">
      <span style="flex:1">${s.name}</span>
      <span style="color:var(--text-muted);font-size:0.85em">${s.duration}</span>
      <button class="btn" onclick="previewSample('${s.file}')">▶ Preview</button>
      <button class="btn btn--export"
        onclick="addSampleToLayer('${s.file}','${s.name}')">＋ Add</button>
    </div>`).join("");
}
let previewSource=null;
function previewSample(file){
  if(previewSource){try{previewSource.stop();}catch(e){}}
  const ctx=getAudioContext();
  fetch(file).then(r=>r.arrayBuffer())
    .then(buf=>ctx.decodeAudioData(buf))
    .then(decoded=>{
      previewSource=ctx.createBufferSource();
      previewSource.buffer=decoded;
      previewSource.connect(ctx.destination);
      previewSource.start();
    }).catch(()=>alert("Sample preview not available offline yet."));
}
function addSampleToLayer(file,name){
  const ctx=getAudioContext();
  fetch(file).then(r=>r.arrayBuffer())
    .then(buf=>ctx.decodeAudioData(buf))
    .then(decoded=>{
      if(layers.length===0)addLayer();
      const layer=layers[layers.length-1];
      layer.audioBuffer=decoded;layer.audioFile=name;
      drawWaveform(layer.id,decoded);
      closeModal();
    }).catch(()=>alert("Add .wav files to /samples folder."));
}
function closeModal(){
  document.getElementById("modalOverlay").classList.add("hidden");
}
