/**
 * app.js — CivicPath India Frontend Application
 * Google Service #9: Google Analytics 4 (gtag.js frontend events)
 * Google Service #10: Google Fonts (loaded in index.html)
 */

const API_BASE = window.location.origin;
let currentJourneyId = null;
let currentLanguage = 'en';
let journeySteps = [];

// ═══ NAVIGATION ═══
function showSection(sectionId) {
  document.querySelectorAll('main > section').forEach(s => s.style.display = 'none');
  document.querySelectorAll('main > section').forEach(s => s.classList.remove('active'));
  const el = document.getElementById('section-' + sectionId);
  if (el) {
    el.style.display = 'block';
    el.classList.add('active');
  }
  document.querySelectorAll('.nav-links button').forEach(b => b.classList.remove('active'));
  const navMap = { home: 0, journey: 1, chat: 2, myths: 3, maps: 4 };
  const btns = document.querySelectorAll('.nav-links button');
  if (btns[navMap[sectionId]]) btns[navMap[sectionId]].classList.add('active');
  if (sectionId === 'quiz') startQuiz();
  if (el) el.focus({ preventScroll: true });
  trackEvent('page_view', { section: sectionId });
}

// ═══ TOAST NOTIFICATIONS ═══
function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = 'toast ' + type;
  toast.textContent = message;
  toast.setAttribute('role', 'alert');
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}

// ═══ ONBOARDING QUIZ ═══
const quizQuestions = [
  { id: 'state', question: 'Which state do you reside in?', type: 'select',
    options: ['Bihar','Uttar Pradesh','Maharashtra','West Bengal','Tamil Nadu','Karnataka','Gujarat','Delhi','Kerala','Other'] },
  { id: 'registered', question: 'Are you registered as a voter?', type: 'choice',
    options: [{ label: 'Yes, I am registered', value: true }, { label: 'No / Not sure', value: false }] },
  { id: 'first_time', question: 'Is this your first time voting?', type: 'choice',
    options: [{ label: 'Yes, first time', value: true }, { label: 'No, I have voted before', value: false }] },
  { id: 'election_type', question: 'Which election are you preparing for?', type: 'choice',
    options: [{ label: 'Lok Sabha (General)', value: 'general' }, { label: 'Vidhan Sabha (State Assembly)', value: 'assembly' },
              { label: 'Municipal / Panchayat (Local)', value: 'local' }, { label: 'By-Election', value: 'bypoll' }] },
  { id: 'confirm', question: 'Ready to generate your personalized journey?', type: 'confirm' }
];

let quizStep = 0;
let quizAnswers = {};

function startQuiz() {
  quizStep = 0;
  quizAnswers = {};
  renderQuiz();
}

function renderQuiz() {
  const q = quizQuestions[quizStep];
  const content = document.getElementById('quiz-content');
  for (let i = 1; i <= 5; i++) {
    const dot = document.getElementById('dot-' + i);
    dot.className = 'quiz-dot' + (i === quizStep + 1 ? ' active' : (i < quizStep + 1 ? ' completed' : ''));
  }
  if (q.type === 'select') {
    content.innerHTML = '<h3 class="quiz-question">' + q.question + '</h3>' +
      '<div class="form-group"><select class="form-select" id="quiz-select" aria-label="' + q.question + '">' +
      q.options.map(o => '<option value="' + o.toLowerCase() + '">' + o + '</option>').join('') +
      '</select></div>' +
      '<button class="btn btn-primary" onclick="quizNext()" aria-label="Next question">Next</button>';
  } else if (q.type === 'choice') {
    content.innerHTML = '<h3 class="quiz-question">' + q.question + '</h3>' +
      '<div class="quiz-options">' +
      q.options.map(o => '<div class="quiz-option" tabindex="0" role="button" aria-label="' + o.label +
        '" onclick="selectQuizOption(this, \'' + q.id + '\', ' + (typeof o.value === 'string' ? "'" + o.value + "'" : o.value) + ')" ' +
        'onkeydown="if(event.key===\'Enter\')this.click()">' + o.label + '</div>').join('') +
      '</div>';
  } else if (q.type === 'confirm') {
    const a = quizAnswers;
    content.innerHTML = '<h3 class="quiz-question">' + q.question + '</h3>' +
      '<div class="card" style="text-align:left;margin-bottom:24px;">' +
      '<p><strong>State:</strong> ' + (a.state || 'bihar') + '</p>' +
      '<p><strong>Registered:</strong> ' + (a.registered ? 'Yes' : 'No') + '</p>' +
      '<p><strong>First time:</strong> ' + (a.first_time ? 'Yes' : 'No') + '</p>' +
      '<p><strong>Election:</strong> ' + (a.election_type || 'general') + '</p></div>' +
      '<button class="btn btn-primary btn-lg" onclick="createJourney()" aria-label="Generate my journey">Generate My Journey</button>';
  }
}

function selectQuizOption(el, key, value) {
  document.querySelectorAll('.quiz-option').forEach(o => o.classList.remove('selected'));
  el.classList.add('selected');
  quizAnswers[key] = value;
  setTimeout(() => { quizStep++; renderQuiz(); }, 350);
}

function quizNext() {
  const sel = document.getElementById('quiz-select');
  if (sel) quizAnswers[quizQuestions[quizStep].id] = sel.value;
  quizStep++;
  renderQuiz();
}

// ═══ JOURNEY ═══
async function createJourney() {
  showToast('Generating your personalized journey...', 'success');
  try {
    const res = await fetch(API_BASE + '/journey/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        state: quizAnswers.state || 'bihar',
        is_registered: quizAnswers.registered || false,
        is_first_time: quizAnswers.first_time !== false,
        election_type: quizAnswers.election_type || 'general',
        language: currentLanguage
      })
    });
    const data = await res.json();
    currentJourneyId = data.journey_id;
    journeySteps = data.steps || [];
    renderTimeline();
    showSection('journey');
    showToast('Journey created. Follow each step below.', 'success');
    trackEvent('journey_created', { state: quizAnswers.state });
  } catch (err) {
    console.error('Journey creation failed:', err);
    journeySteps = getDemoSteps();
    currentJourneyId = 'demo-' + Date.now();
    renderTimeline();
    showSection('journey');
    showToast('Using demo journey (API unavailable)', 'error');
  }
}

function getDemoSteps() {
  return [
    { step_number: 1, title: 'Check Your Name in the Voter List', description: 'Visit the Election Commission of India\'s NVSP portal (voters.eci.gov.in) to verify your name in the electoral roll.', deadline: 'Before nomination filing ends', status: 'pending', is_critical: true, category: 'registration' },
    { step_number: 2, title: 'Register as a New Voter', description: 'If not registered, submit Form 6 online via NVSP or offline to your BLO.', deadline: '10 days before nomination', status: 'pending', is_critical: true, category: 'registration' },
    { step_number: 3, title: 'Prepare Your Voter ID (EPIC)', description: 'Ensure you have your EPIC or one of the 12 accepted alternate IDs like Aadhaar or PAN.', deadline: '1 week before election', status: 'pending', is_critical: true, category: 'preparation' },
    { step_number: 4, title: 'Know Your Candidates', description: 'Review the candidates contesting from your constituency using the ECI KYC app.', deadline: '1 week before election', status: 'pending', is_critical: false, category: 'research' },
    { step_number: 5, title: 'Download Voter Information Slip', description: 'Download your slip from the Voter Helpline App to find your Part Number and Serial Number.', deadline: '3 days before election', status: 'pending', is_critical: false, category: 'logistics' },
    { step_number: 6, title: 'Find Your Polling Booth', description: 'Check your Voter Information Slip or the ECI portal for your assigned polling booth location.', deadline: '1 day before election', status: 'pending', is_critical: true, category: 'logistics' },
    { step_number: 7, title: 'Cast Your Vote', description: 'Go to your polling booth, present your EPIC/ID, and cast your vote using the EVM. Verify your slip on the VVPAT.', deadline: 'Election Day', status: 'pending', is_critical: true, category: 'voting' },
  ];
}

function renderTimeline() {
  const container = document.getElementById('timeline-container');
  container.innerHTML = journeySteps.map((step, i) => {
    const nodeClass = step.status === 'completed' ? 'completed' : (i === 0 ? 'active' : '');
    const criticalClass = step.is_critical ? 'timeline-critical' : '';
    const checkmark = step.status === 'completed' ? '&#10003;' : step.step_number;
    return '<div class="timeline-step" role="listitem" aria-label="Step ' + step.step_number + ': ' + step.title + '">' +
      '<div class="timeline-node ' + nodeClass + '">' + checkmark + '</div>' +
      '<div class="timeline-content ' + criticalClass + '">' +
      '<div class="timeline-title">' + step.title + '</div>' +
      '<div class="timeline-desc">' + step.description + '</div>' +
      '<div class="timeline-deadline">' + (step.deadline || '') + '</div>' +
      '<div class="step-actions">' +
      (step.status !== 'completed' ?
        '<button class="btn btn-primary btn-sm" onclick="completeStep(' + i + ')" aria-label="Mark step ' + step.step_number + ' complete">Complete</button>' : '<span class="badge badge-green">Done</span>') +
      '<button class="btn btn-secondary btn-sm" onclick="readStepAloud(' + i + ')" aria-label="Read step aloud">Read Aloud</button>' +
      '</div></div></div>';
  }).join('');
}

async function completeStep(index) {
  journeySteps[index].status = 'completed';
  renderTimeline();
  showToast('Step ' + journeySteps[index].step_number + ' completed.', 'success');
  trackEvent('step_completed', { step: journeySteps[index].step_number });
  if (currentJourneyId && !currentJourneyId.startsWith('demo')) {
    try {
      await fetch(API_BASE + '/journey/' + currentJourneyId + '/step', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ step_number: journeySteps[index].step_number, status: 'completed' })
      });
    } catch (e) { /* silent */ }
  }
}

async function readStepAloud(index) {
  showToast('Reading step aloud...', 'success');
  const text = journeySteps[index].title + '. ' + journeySteps[index].description;
  if ('speechSynthesis' in window) {
    const u = new SpeechSynthesisUtterance(text);
    u.lang = currentLanguage === 'en' ? 'en-IN' : currentLanguage;
    speechSynthesis.speak(u);
  }
}

// ═══ CHAT ═══
async function sendChat() {
  const input = document.getElementById('chat-input');
  const message = input.value.trim();
  if (!message) return;
  input.value = '';
  appendChatMessage('user', message);
  appendChatMessage('assistant', '<div class="spinner"></div>', true);

  try {
    const res = await fetch(API_BASE + '/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, journey_id: currentJourneyId, language: currentLanguage })
    });
    const data = await res.json();
    removeLastChat();
    appendChatMessage('assistant', data.response || data.detail || 'I encountered an issue. Please try again.');
  } catch (err) {
    removeLastChat();
    appendChatMessage('assistant', "I'm running in demo mode. In production, I'd answer your election questions using Google Gemini AI. Try asking about voter registration (Form 6), EPIC requirements, or EVM procedures.");
  }
  trackEvent('chat_message', { has_journey: !!currentJourneyId });
}

function appendChatMessage(role, content, isHtml) {
  const container = document.getElementById('chat-messages');
  const avatar = role === 'assistant' ? 'CP' : 'You';
  const div = document.createElement('div');
  div.className = 'chat-message ' + role;
  div.innerHTML = '<div class="chat-avatar" aria-hidden="true">' + avatar + '</div>' +
    '<div class="chat-bubble">' + (isHtml ? content : escapeHtml(content)) + '</div>';
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function removeLastChat() {
  const msgs = document.getElementById('chat-messages');
  if (msgs.lastChild) msgs.removeChild(msgs.lastChild);
}

function escapeHtml(str) {
  const d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML.replace(/\n/g, '<br>');
}

// ═══ VOICE INPUT ═══
let mediaRecorder = null;
let audioChunks = [];

function toggleVoice() {
  const btn = document.getElementById('voice-btn');
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.stop();
    btn.classList.remove('recording');
    btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/></svg>';
    return;
  }
  navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];
    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
    mediaRecorder.onstop = async () => {
      stream.getTracks().forEach(t => t.stop());
      const blob = new Blob(audioChunks, { type: 'audio/webm' });
      showToast('Processing voice input...', 'success');
      try {
        const fd = new FormData();
        fd.append('audio', blob, 'voice.webm');
        const res = await fetch(API_BASE + '/chat/voice-input', { method: 'POST', body: fd });
        const data = await res.json();
        if (data.transcript) appendChatMessage('user', data.transcript);
        if (data.ai_response) appendChatMessage('assistant', data.ai_response);
      } catch (e) {
        appendChatMessage('assistant', 'Voice processing requires Google Cloud Speech APIs in production.');
      }
    };
    mediaRecorder.start();
    btn.classList.add('recording');
    btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="4" width="12" height="16" rx="2"/></svg>';
    showToast('Listening... click again to stop.', 'success');
  }).catch(() => showToast('Microphone access denied', 'error'));
}

// ═══ FACT CHECKER ═══
async function checkMyth() {
  const input = document.getElementById('myth-input');
  const text = input.value.trim();
  if (!text || text.length < 5) { showToast('Enter a claim to verify.', 'error'); return; }
  const resultDiv = document.getElementById('myth-result');
  resultDiv.innerHTML = '<div style="text-align:center;padding:20px;"><div class="spinner" style="margin:0 auto;"></div><p style="margin-top:12px;font-size:0.875rem;">Analyzing with Google Gemini AI...</p></div>';

  try {
    const res = await fetch(API_BASE + '/chat/myth-check', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, language: currentLanguage })
    });
    const data = await res.json();
    const verdict = (data.verdict || 'unverifiable').toLowerCase();
    const labels = { myth: 'FALSE', fact: 'TRUE', misleading: 'MISLEADING', unverifiable: 'UNVERIFIABLE' };
    const colors = { myth: 'myth', fact: 'fact', misleading: 'misleading', unverifiable: 'misleading' };
    resultDiv.innerHTML = '<div class="myth-result ' + (colors[verdict] || '') + '">' +
      '<div class="myth-verdict">' + (labels[verdict] || 'UNVERIFIABLE') + '</div>' +
      '<p>' + (data.explanation || 'Unable to verify this claim.') + '</p>' +
      (data.sources && data.sources.length ? '<p style="margin-top:12px;font-size:0.8125rem;color:var(--text-muted);">Sources: ' + data.sources.join(', ') + '</p>' : '') +
      '<p style="margin-top:8px;font-size:0.75rem;color:var(--text-muted);">Powered by ' + (data.google_service || 'Google Gemini') + '</p></div>';
  } catch (e) {
    resultDiv.innerHTML = '<div class="myth-result misleading"><div class="myth-verdict">DEMO MODE</div><p>Fact checking requires Google Gemini API. In production, this would analyze your claim against official election sources.</p></div>';
  }
  trackEvent('myth_check', { verdict_received: true });
}

// ═══ POLLING BOOTHS ═══
async function findPollingPlaces() {
  const address = document.getElementById('address-input').value.trim();
  if (!address) { showToast('Enter an address.', 'error'); return; }
  const resultsDiv = document.getElementById('polling-results');
  resultsDiv.innerHTML = '<div style="text-align:center;padding:20px;"><div class="spinner" style="margin:0 auto;"></div></div>';
  try {
    const res = await fetch(API_BASE + '/maps/polling-places?address=' + encodeURIComponent(address));
    const data = await res.json();
    const places = data.places || [];
    resultsDiv.innerHTML = places.map(p =>
      '<div class="card" style="margin-bottom:12px;">' +
      '<h3 style="font-size:0.9375rem;">' + p.name + '</h3>' +
      '<p style="font-size:0.8125rem;">' + p.address + '</p>' +
      (p.hours ? '<p style="font-size:0.8125rem;color:var(--saffron);margin-top:4px;">' + p.hours + '</p>' : '') +
      (p.distance_miles ? '<p style="font-size:0.75rem;color:var(--text-muted);margin-top:2px;">' + p.distance_miles + ' miles away</p>' : '') +
      '</div>'
    ).join('') || '<p>No polling booths found. Try a different address.</p>';
  } catch (e) {
    resultsDiv.innerHTML = '<p style="color:var(--text-secondary);">Polling booth search requires Google Maps API in production.</p>';
  }
}

function useMyLocation() {
  if (!navigator.geolocation) { showToast('Geolocation not supported.', 'error'); return; }
  navigator.geolocation.getCurrentPosition(async pos => {
    const resultsDiv = document.getElementById('polling-results');
    resultsDiv.innerHTML = '<div style="text-align:center;padding:20px;"><div class="spinner" style="margin:0 auto;"></div></div>';
    try {
      const res = await fetch(API_BASE + '/maps/polling-places?latitude=' + pos.coords.latitude + '&longitude=' + pos.coords.longitude);
      const data = await res.json();
      const places = data.places || [];
      resultsDiv.innerHTML = places.map(p =>
        '<div class="card" style="margin-bottom:12px;"><h3 style="font-size:0.9375rem;">' + p.name + '</h3><p style="font-size:0.8125rem;">' + p.address + '</p></div>'
      ).join('') || '<p>No polling booths found nearby.</p>';
    } catch (e) { resultsDiv.innerHTML = '<p>Could not search. Try entering an address instead.</p>'; }
  }, () => showToast('Location access denied.', 'error'));
}

// ═══ TRANSLATION ═══
async function changeLanguage(lang) {
  currentLanguage = lang;
  document.documentElement.lang = lang;
  showToast('Language set to ' + lang.toUpperCase(), 'success');
  trackEvent('language_changed', { language: lang });
}

// ═══ ANALYTICS (Google Service #9: GA4 gtag.js) ═══
function trackEvent(name, params) {
  if (typeof gtag === 'function') {
    gtag('event', name, params || {});
  }
  console.log('[GA4]', name, params);
}

// ═══ SERVICE WORKER REGISTRATION ═══
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js').catch(() => {});
}

// ═══ KEYBOARD NAVIGATION ═══
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') {
    document.activeElement.blur();
  }
});
