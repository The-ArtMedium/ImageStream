

let appMode="simple";
function initApp(){
  const savedMode=localStorage.getItem("localbeat_mode")||"simple";
  setMode(savedMode);
  const savedScale=localStorage.getItem("localbeat_scale")||"medium";
  setScale(savedScale);
  const savedContrast=localStorage.getItem("localbeat_contrast")||"normal";
  if(savedContrast==="high")
    document.documentElement.setAttribute("data-contrast","high");
  initLayers();
}
function setMode(mode){
  appMode=mode;
  document.documentElement.setAttribute("data-mode",mode);
  localStorage.setItem("localbeat_mode",mode);
  const label=document.getElementById("modeLabel");
  if(label)label.textContent=mode==="simple"?t("simpleMode"):t("fullMode");
}
function setScale(scale){
  document.documentElement.setAttribute("data-scale",scale);
  localStorage.setItem("localbeat_scale",scale);
}
document.getElementById("modeToggle")?.addEventListener("click",()=>{
  setMode(appMode==="simple"?"full":"simple");
});
document.addEventListener("DOMContentLoaded",initApp);
