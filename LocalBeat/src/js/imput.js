

```javascript
// PATH: ImageStream/LocalBeat/src/js/input.js
const InputLayer = (() => {
  let mediaRecorder = null;
  let audioChunks = [];
  let audioContext = null;
  let analyser = null;
  let micStream = null;
  let midiAccess = null;
  let midiRecording = [];
  let midiStartTime = null;
  let loopBlob = null;
  let loopChunks = [];
  let loopRecorder = null;
  let loopTimerInterval = null;
  let recordedBlob = null;
  let animFrameId = null;
  let timerInterval = null;
  let timerStart = null;

  function openInputModal() {
    const t = window.LANGUAGES?.[window.currentLang] || {};
    const modal = document.getElementById('modalOverlay');
    const content = document.getElementById('modalContent');
    content.innerHTML = `
      <div class="input-modal">
        <h2 class="input-title">🎙 Record Input</h2>
        <div class="input-device-row">
          <label class="input-label">Input Source</label>
          <select id="inputDeviceSelect" class="select--lang" style="flex:1"></select>
        </div>
        <div class="input-tabs">
          <button class="input-tab active" onclick="InputLayer.switchTab('record',this)">🎤 Record</button>
          <button class="input-tab" onclick="InputLayer.switchTab('loop',this)">🔁 Loop</button>
          <button class="input-tab" onclick="InputLayer.switchTab('midi',this)">🎹 MIDI</button>
        </div>

        <div id="tab-record" class="input-tab-content active">
          <canvas id="inputWaveform" class="input-waveform" width="500" height="80"></canvas>
          <div class="input-timer" id="inputTimer">00:00</div>
          <div class="input-controls">
            <button class="btn btn--record" id="btnRecord" onclick="InputLayer.startRecording()">
              <span class="rec-dot"></span> Record
            </button>
            <button class="btn btn--stop-rec" id="btnStopRec" onclick="InputLayer.stopRecording()" disabled>
              ⏹ Stop
            </button>
          </div>
          <div id="previewSection" class="input-preview hidden">
            <audio id="previewPlayer" controls class="input-audio-preview"></audio>
            <div class="input-preview-actions">
              <button class="btn btn--add" onclick="InputLayer.addToLayer()">✅ Add to Layer</button>
              <button class="btn" onclick="InputLayer.discardRecording()">🗑 Discard</button>
            </div>
          </div>
        </div>

        <div id="tab-loop" class="input-tab-content">
          <canvas id="loopWaveform" class="input-waveform" width="500" height="80"></canvas>
          <div class="input-loop-length">
            <label class="input-label">Loop Length</label>
            <select id="loopLengthSelect" class="select--lang">
              <option value="2000">2s</option>
              <option value="4000" selected>4s</option>
              <option value="8000">8s</option>
              <option value="16000">16s</option>
            </select>
          </div>
          <div class="loop-bar"><div class="loop-progress" id="loopProgress"></div></div>
          <div class="input-controls">
            <button class="btn btn--record" id="btnLoop" onclick="InputLayer.startLoop()">
              <span class="rec-dot"></span> Start Loop
            </button>
            <button class="btn btn--stop-rec" id="btnStopLoop" onclick="InputLayer.stopLoop()" disabled>
              ⏹ Stop Loop
            </button>
          </div>
          <div id="loopPreviewSection" class="input-preview hidden">
            <audio id="loopPreviewPlayer" controls class="input-audio-preview"></audio>
            <div class="input-preview-actions">
              <button class="btn btn--add" onclick="InputLayer.addLoopToLayer()">✅ Add to Layer</button>
              <button class="btn" onclick="InputLayer.discardLoop()">🗑 Discard</button>
            </div>
          </div>
        </div>

        <div id="tab-midi" class="input-tab-content">
          <div class="midi-status"><span id="midiStatusText">🔍 Looking for MIDI devices...</span></div>
          <div id="midiDeviceList" class="midi-device-list"></div>
          <div class="midi-piano" id="midiPiano"></div>
          <div class="input-controls">
            <button class="btn btn--record" id="btnMidiRecord" onclick="InputLayer.startMidiRecord()" disabled>
              <span class="rec-dot"></span> Record
            </button>
            <button class="btn btn--stop-rec" id="btnMidiStop" onclick="InputLayer.stopMidiRecord()" disabled>
              ⏹ Stop
            </button>
          </div>
          <div id="midiPreviewSection" class="input-preview hidden">
            <div class="midi-note-list" id="midiNoteList"></div>
            <div class="input-preview-actions">
              <button class="btn btn--add" onclick="InputLayer.addMidiToLayer()">✅ Add to Layer</button>
              <button class="btn" onclick="InputLayer.discardMidi()">🗑 Discard</button>
            </div>
          </div>
        </div>

        <button class="btn input-close" onclick="InputLayer.close()">✕ Close</button>
      </div>`;
    modal.classList.remove('hidden');
    populateDevices();
    initMidi();
    buildMiniPiano();
    startVisualiser('inputWaveform');
  }

  function switchTab(tab, el) {
    document.querySelectorAll('.input-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.input-tab-content').forEach(t => t.classList.remove('active'));
    el.classList.add('active');
    document.getElementById('tab-' + tab).classList.add('active');
    if (tab === 'record') startVisualiser('inputWaveform');
    if (tab === 'loop') startVisualiser('loopWaveform');
  }

  function close() {
    stopAll();
    document.getElementById('modalOverlay').classList.add('hidden');
  }

  async function populateDevices() {
    const sel = document.getElementById('inputDeviceSelect');
    if (!sel) return;
    try {
      await navigator.mediaDevices.getUserMedia({ audio: true });
      const devices = await navigator.mediaDevices.enumerateDevices();
      const audioIn = devices.filter(d => d.kind === 'audioinput');
      sel.innerHTML = audioIn.map((d, i) =>
        `<option value="${d.deviceId}">${d.label || 'Microphone ' + (i + 1)}</option>`
      ).join('');
    } catch {
      sel.innerHTML = '<option>Default Microphone</option>';
    }
  }

  async function startVisualiser(canvasId) {
    try {
      if (!micStream) {
        const deviceId = document.getElementById('inputDeviceSelect')?.value;
        const constraints = { audio: deviceId ? { deviceId: { exact: deviceId } } : true };
        micStream = await navigator.mediaDevices.getUserMedia(constraints);
      }
      if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;
        const source = audioContext.createMediaStreamSource(micStream);
        source.connect(analyser);
      }
      drawWaveform(canvasId);
    } catch (e) {
      console.warn('Mic access:', e);
    }
  }

  function drawWaveform(canvasId) {
    if (animFrameId) cancelAnimationFrame(animFrameId);
    const canvas = document.getElementById(canvasId);
    if (!canvas || !analyser) return;
    const ctx = canvas.getContext('2d');
    const buf = new Uint8Array(analyser.frequencyBinCount);
    function draw() {
      animFrameId = requestAnimationFrame(draw);
      analyser.getByteTimeDomainData(buf);
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.strokeStyle = '#f5a623';
      ctx.lineWidth = 2;
      ctx.beginPath();
      const sliceW = canvas.width / buf.length;
      let x = 0;
      for (let i = 0; i < buf.length; i++) {
        const y = (buf[i] / 128.0) * canvas.height / 2;
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
        x += sliceW;
      }
      ctx.stroke();
    }
    draw();
  }

  async function startRecording() {
    audioChunks = [];
    if (!micStream) await startVisualiser('inputWaveform');
    if (!micStream) return alert('No microphone found.');
    mediaRecorder = new MediaRecorder(micStream);
    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
    mediaRecorder.onstop = () => {
      recordedBlob = new Blob(audioChunks, { type: 'audio/webm' });
      document.getElementById('previewPlayer').src = URL.createObjectURL(recordedBlob);
      document.getElementById('previewSection').classList.remove('hidden');
    };
    mediaRecorder.start();
    document.getElementById('btnRecord').disabled = true;
    document.getElementById('btnStopRec').disabled = false;
    document.getElementById('previewSection').classList.add('hidden');
    startTimer('inputTimer');
  }

  function stopRecording() {
    if (mediaRecorder) mediaRecorder.stop();
    document.getElementById('btnRecord').disabled = false;
    document.getElementById('btnStopRec').disabled = true;
    stopTimer();
  }

  function addToLayer() {
    if (!recordedBlob) return;
    if (window.addAudioLayer) window.addAudioLayer(URL.createObjectURL(recordedBlob), '🎤 Recording');
    close();
  }

  function discardRecording() {
    recordedBlob = null;
    audioChunks = [];
    document.getElementById('previewSection').classList.add('hidden');
  }

  async function startLoop() {
    loopChunks = [];
    const ms = parseInt(document.getElementById('loopLengthSelect').value);
    if (!micStream) await startVisualiser('loopWaveform');
    if (!micStream) return alert('No microphone found.');
    loopRecorder = new MediaRecorder(micStream);
    loopRecorder.ondataavailable = e => loopChunks.push(e.data);
    loopRecorder.onstop = () => {
      loopBlob = new Blob(loopChunks, { type: 'audio/webm' });
      const player = document.getElementById('loopPreviewPlayer');
      player.src = URL.createObjectURL(loopBlob);
      player.loop = true;
      document.getElementById('loopPreviewSection').classList.remove('hidden');
    };
    loopRecorder.start();
    document.getElementById('btnLoop').disabled = true;
    document.getElementById('btnStopLoop').disabled = false;
    const bar = document.getElementById('loopProgress');
    const start = Date.now();
    loopTimerInterval = setInterval(() => {
      const pct = Math.min(100, ((Date.now() - start) / ms) * 100);
      bar.style.width = pct + '%';
      if (pct >= 100) stopLoop();
    }, 50);
  }

  function stopLoop() {
    clearInterval(loopTimerInterval);
    if (loopRecorder) loopRecorder.stop();
    document.getElementById('btnLoop').disabled = false;
    document.getElementById('btnStopLoop').disabled = true;
  }

  function addLoopToLayer() {
    if (!loopBlob) return;
    if (window.addAudioLayer) window.addAudioLayer(URL.createObjectURL(loopBlob), '🔁 Loop');
    close();
  }

  function discardLoop() {
    loopBlob = null;
    loopChunks = [];
    document.getElementById('loopPreviewSection').classList.add('hidden');
    document.getElementById('loopProgress').style.width = '0%';
  }

  async function initMidi() {
    const statusEl = document.getElementById('midiStatusText');
    const listEl = document.getElementById('midiDeviceList');
    const btn = document.getElementById('btnMidiRecord');
    if (!navigator.requestMIDIAccess) {
      statusEl.textContent = '⚠️ MIDI not supported in this browser.';
      return;
    }
    try {
      midiAccess = await navigator.requestMIDIAccess();
      const inputs = [...midiAccess.inputs.values()];
      if (inputs.length === 0) {
        statusEl.textContent = '🔌 No MIDI devices found.';
      } else {
        statusEl.textContent = `✅ ${inputs.length} MIDI device(s) found`;
        btn.disabled = false;
        listEl.innerHTML = inputs.map(i => `<div class="midi-device-item">🎹 ${i.name}</div>`).join('');
        inputs.forEach(input => { input.onmidimessage = onMidiMessage; });
      }
    } catch {
      statusEl.textContent = '⚠️ MIDI access denied.';
    }
  }

  function onMidiMessage(event) {
    const [status, note, velocity] = event.data;
    const isNoteOn = (status & 0xf0) === 0x90 && velocity > 0;
    highlightPianoKey(note, isNoteOn);
    if (midiStartTime !== null) {
      midiRecording.push({
        time: Date.now() - midiStartTime,
        type: isNoteOn ? 'on' : 'off',
        note, velocity,
        name: noteName(note)
      });
    }
  }

  function startMidiRecord() {
    midiRecording = [];
    midiStartTime = Date.now();
    document.getElementById('btnMidiRecord').disabled = true;
    document.getElementById('btnMidiStop').disabled = false;
    startTimer('inputTimer');
  }

  function stopMidiRecord() {
    midiStartTime = null;
    document.getElementById('btnMidiRecord').disabled = false;
    document.getElementById('btnMidiStop').disabled = true;
    stopTimer();
    const noteOns = midiRecording.filter(e => e.type === 'on');
    document.getElementById('midiNoteList').innerHTML =
      noteOns.slice(0, 20).map(e => `<span class="midi-note-pill">${e.name}</span>`).join('');
    document.getElementById('midiPreviewSection').classList.remove('hidden');
  }

  function addMidiToLayer() {
    if (window.addMidiLayer) window.addMidiLayer(midiRecording);
    close();
  }

  function discardMidi() {
    midiRecording = [];
    document.getElementById('midiPreviewSection').classList.add('hidden');
  }

  function buildMiniPiano() {
    const piano = document.getElementById('midiPiano');
    if (!piano) return;
    const whites = [60,62,64,65,67,69,71,72,74,76,77,79,81,83];
    const blacks = {61:1,63:2,66:4,68:5,70:6,73:8,75:9,78:11,80:12,82:13};
    piano.innerHTML = whites.map(n => `<div class="piano-white" id="key-${n}"></div>`).join('');
    Object.entries(blacks).forEach(([note, pos]) => {
      const key = document.createElement('div');
      key.className = 'piano-black';
      key.id = `key-${note}`;
      key.style.left = (pos * 28 + 18) + 'px';
      piano.appendChild(key);
    });
  }

  function highlightPianoKey(note, on) {
    const key = document.getElementById(`key-${note}`);
    if (key) key.classList.toggle('piano-active', on);
  }

  function noteName(midi) {
    return ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'][midi % 12] + Math.floor(midi / 12 - 1);
  }

  function startTimer(id) {
    timerStart = Date.now();
    timerInterval = setInterval(() => {
      const el = document.getElementById(id);
      if (!el) return;
      const s = Math.floor((Date.now() - timerStart) / 1000);
      el.textContent = String(Math.floor(s/60)).padStart(2,'0') + ':' + String(s%60).padStart(2,'0');
    }, 500);
  }

  function stopTimer() { clearInterval(timerInterval); }

  function stopAll() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop();
    if (loopRecorder && loopRecorder.state !== 'inactive') loopRecorder.stop();
    if (micStream) { micStream.getTracks().forEach(t => t.stop()); micStream = null; }
    if (audioContext) { audioContext.close(); audioContext = null; }
    if (animFrameId) cancelAnimationFrame(animFrameId);
    clearInterval(timerInterval);
    clearInterval(loopTimerInterval);
    midiStartTime = null;
  }

  return {
    openInputModal, switchTab, startRecording, stopRecording,
    addToLayer, discardRecording, startLoop, stopLoop,
    addLoopToLayer, discardLoop, startMidiRecord, stopMidiRecord,
    addMidiToLayer, discardMidi, close
  };
})();

window.openInput = () => InputLayer.openInputModal();


