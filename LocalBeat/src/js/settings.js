

function openSettings(){
  const overlay=document.getElementById("modalOverlay");
  const content=document.getElementById("modalContent");
  content.innerHTML=`<h2 style="color:var(--accent);margin-bottom:var(--space-md)">
    ⚙ Settings</h2>
    <div style="display:flex;flex-direction:column;gap:var(--space-md)">
      <div>
        <label style="color:var(--text-secondary);display:block;margin-bottom:4px">
          🌐 Language</label>
        <select onchange="setLanguage(this.value)"
          style="width:100%;background:var(--bg-elevated);color:var(--text-primary);
          border:1px solid var(--border);padding:var(--space-sm);
          border-radius:var(--radius);min-height:44px">
          <option value="en">English</option>
          <option value="es">Español</option>
          <option value="fr">Français</option>
          <option value="pt">Português</option>
          <option value="ar">العربية</option>
          <option value="zh">中文</option>
          <option value="hi">हिन्दी</option>
        </select>
      </div>
      <div>
        <label style="color:var(--text-secondary);display:block;margin-bottom:4px">
          🔠 Text Size</label>
        <div style="display:flex;gap:var(--space-sm)">
          <button class="btn" style="flex:1" onclick="setScale('small')">Small</button>
          <button class="btn" style="flex:1" onclick="setScale('medium')">Medium</button>
          <button class="btn" style="flex:1" onclick="setScale('large')">Large</button>
          <button class="btn" style="flex:1" onclick="setScale('xl')">XL</button>
        </div>
      </div>
      <div style="display:flex;align-items:center;
        justify-content:space-between;padding:var(--space-sm) 0">
        <label style="color:var(--text-secondary)">🌑 High Contrast</label>
        <input type="checkbox" id="contrastToggle"
          style="width:24px;height:24px;accent-color:var(--accent);cursor:pointer"
          onchange="toggleContrast(this.checked)"/>
      </div>
      <div style="display:flex;align-items:center;
        justify-content:space-between;padding:var(--space-sm) 0">
        <label style="color:var(--text-secondary)">🤖 AI Plugins (optional)</label>
        <input type="checkbox" id="aiToggle"
          style="width:24px;height:24px;accent-color:var(--accent);cursor:pointer"
          onchange="localStorage.setItem('localbeat_ai',this.checked?'on':'off')"/>
      </div>
      <div style="color:var(--text-muted);font-size:0.8em;
        text-align:center;padding-top:var(--space-sm)">
        🎵 LocalBeat v0.1.0 — Part of ImageStream<br/>
        Free forever. Offline. Private. Yours.
      </div>
      <button class="btn" style="width:100%" onclick="closeModal()">✓ Done</button>
    </div>`;
  overlay.classList.remove("hidden");
  document.getElementById("contrastToggle").checked=
    localStorage.getItem("localbeat_contrast")==="high";
  document.getElementById("aiToggle").checked=
    localStorage.getItem("localbeat_ai")==="on";
}
function toggleContrast(on){
  document.documentElement.setAttribute("data-contrast",on?"high":"normal");
  localStorage.setItem("localbeat_contrast",on?"high":"normal");
}
