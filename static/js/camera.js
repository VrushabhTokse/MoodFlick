/**
 * camera.js
 * Handles webcam access, countdown, snapshot capture,
 * and communication with the /detect Flask endpoint.
 */

// ─── State ───────────────────────────────────────────────────────────────────
let stream = null;
let detectedEmotion = null;
let detectedRedirectUrl = null;

// ─── DOM references (resolved after DOMContentLoaded) ────────────────────────
const $ = (id) => document.getElementById(id);

// ─── Start detection flow ────────────────────────────────────────────────────
async function startDetection() {
  const startBtn   = $('start-btn');
  const retryBtn   = $('retry-btn');
  const goBtn      = $('go-movies-btn');
  const result     = $('emotion-result');

  // Hide buttons, reset result
  startBtn.classList.add('hidden');
  retryBtn.classList.add('hidden');
  goBtn.classList.add('hidden');
  result.classList.add('hidden');

  // ── 1. Request camera access ─────────────────────────────────────────────
  showOverlay('cam-overlay-idle');
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' }
    });
    const video = $('webcam');
    video.srcObject = stream;
    await video.play();
  } catch (err) {
    console.error('Camera error:', err);
    showToast('❌ Camera access denied. Please allow camera permissions and try again.', 'error');
    startBtn.classList.remove('hidden');
    showOverlay('cam-overlay-idle');
    return;
  }

  // Hide idle overlay (camera visible now)
  hideAllOverlays();

  // ── 2. Countdown 3 → 2 → 1 ───────────────────────────────────────────────
  await countdown(3);

  // ── 3. Capture frame ─────────────────────────────────────────────────────
  const b64Image = captureFrame();

  // ── 4. Stop camera stream (privacy) ──────────────────────────────────────
  stopCamera();

  // ── 5. Show processing spinner ────────────────────────────────────────────
  showOverlay('cam-overlay-processing');

  // ── 6. Send to Flask /detect ──────────────────────────────────────────────
  try {
    const res = await fetch('/detect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image: b64Image })
    });

    if (!res.ok) throw new Error(`Server error: ${res.status}`);
    const data = await res.json();

    hideAllOverlays();
    displayResult(data);

    detectedEmotion = data.emotion;
    detectedRedirectUrl = data.redirect_url;

    // Update "go movies" button
    goBtn.href = data.redirect_url;
    goBtn.classList.remove('hidden');
    retryBtn.classList.remove('hidden');

    // Auto-redirect after 4 seconds
    setTimeout(() => {
      if (detectedRedirectUrl) window.location.href = detectedRedirectUrl;
    }, 4000);

  } catch (err) {
    console.error('Detection error:', err);
    hideAllOverlays();
    showToast('⚠️ Detection failed. Please try again.', 'error');
    startBtn.classList.remove('hidden');
    showOverlay('cam-overlay-idle');
  }
}

// ─── Retry ───────────────────────────────────────────────────────────────────
function retryDetection() {
  const result   = $('emotion-result');
  const retryBtn = $('retry-btn');
  const goBtn    = $('go-movies-btn');
  const startBtn = $('start-btn');

  result.classList.add('hidden');
  retryBtn.classList.add('hidden');
  goBtn.classList.add('hidden');
  startBtn.classList.remove('hidden');
  showOverlay('cam-overlay-idle');
}

// ─── Countdown helper ────────────────────────────────────────────────────────
function countdown(seconds) {
  return new Promise((resolve) => {
    showOverlay('cam-overlay-countdown');
    let remaining = seconds;
    $('countdown-num').textContent = remaining;

    const tick = setInterval(() => {
      remaining--;
      const el = $('countdown-num');
      if (el) el.textContent = remaining;

      if (remaining <= 0) {
        clearInterval(tick);
        resolve();
      }
    }, 1000);
  });
}

// ─── Capture a frame from the video element ──────────────────────────────────
function captureFrame() {
  const video  = $('webcam');
  const canvas = $('snapshot-canvas');
  const W = video.videoWidth  || 640;
  const H = video.videoHeight || 480;
  canvas.width  = W;
  canvas.height = H;
  const ctx = canvas.getContext('2d');
  // Draw mirrored (flip back to normal for the model)
  ctx.translate(W, 0);
  ctx.scale(-1, 1);
  ctx.drawImage(video, 0, 0, W, H);
  return canvas.toDataURL('image/jpeg', 0.85);
}

// ─── Stop camera ──────────────────────────────────────────────────────────────
function stopCamera() {
  if (stream) {
    stream.getTracks().forEach((t) => t.stop());
    stream = null;
  }
  const video = $('webcam');
  if (video) video.srcObject = null;
}

// ─── Display detection result ────────────────────────────────────────────────
function displayResult(data) {
  const result    = $('emotion-result');
  const iconEl    = $('result-icon');
  const labelEl   = $('result-label');
  const tipEl     = $('result-tip');
  const barEl     = $('confidence-bar');
  const pctEl     = $('confidence-pct');
  const scoresEl  = $('result-scores');

  iconEl.textContent  = data.icon  || '😐';
  labelEl.textContent = data.label || data.emotion;
  labelEl.style.color = data.color || '#a594ff';
  tipEl.textContent   = data.tip   || '';

  // Confidence bar
  const pct = data.confidence || 0;
  barEl.style.width        = `${pct}%`;
  barEl.style.background   = `linear-gradient(90deg, ${data.color || '#7c6aff'}, #a594ff)`;
  pctEl.textContent        = `${pct}%`;

  // All emotion scores mini grid
  if (data.all_scores && Object.keys(data.all_scores).length) {
    const ICONS = { angry:'😠', disgust:'🤢', fear:'😨', happy:'😄', neutral:'😐', sad:'😢', surprise:'😮' };
    scoresEl.innerHTML = '';
    Object.entries(data.all_scores)
      .sort((a, b) => b[1] - a[1])
      .forEach(([em, v]) => {
        const div = document.createElement('div');
        div.className = 'score-item';
        div.innerHTML = `<span class="score-label">${ICONS[em] || ''} ${em}</span><span class="score-val">${v}%</span>`;
        scoresEl.appendChild(div);
      });
    scoresEl.classList.remove('hidden');
  }

  result.classList.remove('hidden');

  // Toast
  if (!data.face_detected) {
    showToast('⚠️ No face clearly detected. Try better lighting.', 'warning');
  } else {
    showToast(`✅ Detected: ${data.label} (${pct}% confidence)`, 'success');
  }
}

// ─── Overlay helpers ──────────────────────────────────────────────────────────
function showOverlay(id) {
  hideAllOverlays();
  const el = $(id);
  if (el) el.classList.remove('cam-overlay-hidden');
}

function hideAllOverlays() {
  ['cam-overlay-idle','cam-overlay-countdown','cam-overlay-processing'].forEach((id) => {
    const el = $(id);
    if (el) el.classList.add('cam-overlay-hidden');
  });
}

// ─── Toast helper (reuses app.js if available) ────────────────────────────────
function showToast(msg, type) {
  if (window.appShowToast) {
    window.appShowToast(msg, type);
  }
}

// ─── Cleanup on page unload ──────────────────────────────────────────────────
window.addEventListener('beforeunload', stopCamera);
