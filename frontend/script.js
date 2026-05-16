/* =================================================================
   SERENE HEALTH — script.js
   Conectado a la API Flask real (api.py) en http://localhost:5000
   ================================================================= */

const API_URL = 'http://localhost:5000/predict';

/* ---------------------------------------------------------------
   ETIQUETAS
   --------------------------------------------------------------- */
const FIELD_LABELS = {
  nombre:            'Nombre',
  edad:              'Edad',
  genero:            'Género',
  fraccion_eyeccion: 'Fracc. de Eyección',
  creatinina_serica: 'Creatinina Sérica',
  sodio_serico:      'Sodio Sérico',
  cpk:               'CPK',
  plaquetas:         'Plaquetas',
  tiempo:            'T. Seguimiento',
  anemia:            'Anemia',
  diabetes:          'Diabetes',
  presion_alta:      'Presión Alta',
  fuma:              'Fuma',
};

const GENERO_LABEL  = { '0': 'Femenino', '1': 'Masculino' };
const BINARIO_LABEL = { '0': 'No', '1': 'Sí' };

/* ---------------------------------------------------------------
   RECOMENDACIONES
   --------------------------------------------------------------- */
const RECS = {
  stable: [
    { icon: '🥗', text: 'Mantén una dieta mediterránea rica en frutas, verduras y grasas saludables para conservar tu salud cardíaca.' },
    { icon: '🚶', text: 'Realiza al menos 150 minutos de actividad física moderada por semana (caminatas, natación, ciclismo).' },
    { icon: '💧', text: 'Hidratación adecuada: consume al menos 1.5–2 litros de agua diariamente.' },
    { icon: '😴', text: 'Duerme entre 7–9 horas cada noche para apoyar la recuperación cardiovascular.' },
    { icon: '🩺', text: 'Continúa con tus controles médicos periódicos para monitorear tus valores clínicos.' },
  ],
  critical: [
    { icon: '🚨', text: 'Consulta a tu médico o cardiólogo lo antes posible para una evaluación completa.' },
    { icon: '💊', text: 'Sigue estrictamente el tratamiento farmacológico prescrito y no lo interrumpas sin supervisión.' },
    { icon: '🚫', text: 'Evita el tabaco y el alcohol; ambos agravan significativamente las condiciones cardíacas.' },
    { icon: '🧂', text: 'Reduce el consumo de sal a menos de 2g por día para controlar la presión arterial y la retención de líquidos.' },
    { icon: '📊', text: 'Monitorea diariamente tu presión arterial, frecuencia cardíaca y peso corporal, y registra los valores.' },
    { icon: '🏥', text: 'Ante síntomas como disnea, dolor de pecho o edema en piernas, acude de inmediato a urgencias.' },
  ],
  anemia:            { icon: '🩸', text: 'Tu anemia puede reducir el oxígeno disponible para el corazón. Consulta sobre suplementación con hierro o vitamina B12.' },
  diabetes:          { icon: '🍬', text: 'Controla tu glucosa estrictamente: niveles altos dañan los vasos sanguíneos y el miocardio.' },
  presion_alta:      { icon: '⚡', text: 'La hipertensión no controlada es un factor de riesgo mayor. Mide tu presión a diario y toma la medicación puntualmente.' },
  fuma:              { icon: '🚭', text: 'Dejar de fumar es la intervención de mayor impacto en salud cardiovascular. Busca apoyo médico o programas de cesación.' },
  cpk_high:          { icon: '🔬', text: 'Tu nivel de CPK elevado puede indicar daño muscular cardíaco. Informa a tu médico sobre este valor.' },
  creatinina_high:   { icon: '🫘', text: 'Tu creatinina elevada sugiere una función renal reducida, lo que complica la salud cardíaca. Requiere seguimiento nefrológico.' },
  sodio_low:         { icon: '🧪', text: 'Un sodio sérico bajo (hiponatremia) puede indicar retención de líquidos. Reduce el consumo de agua excesivo y consulta a tu médico.' },
  eyeccion_low:      { icon: '❤️', text: 'Una fracción de eyección baja indica que el corazón bombea con menos eficiencia. Es fundamental el seguimiento cardiológico regular.' },
};

/* ---------------------------------------------------------------
   UTILIDADES
   --------------------------------------------------------------- */
function z(id) { return document.getElementById(id); }

/* ---------------------------------------------------------------
   TOOLTIP
   --------------------------------------------------------------- */
const tooltipEl = z('tooltip-bubble');

document.querySelectorAll('.info-btn').forEach(btn => {
  btn.addEventListener('mouseenter', (e) => {
    const text = btn.dataset.tooltip;
    if (!text) return;
    tooltipEl.textContent = text;
    tooltipEl.setAttribute('aria-hidden', 'false');
    tooltipEl.classList.add('visible');
    positionTooltip(e);
  });
  btn.addEventListener('mousemove', positionTooltip);
  btn.addEventListener('mouseleave', hideTooltip);
  btn.addEventListener('focus', (e) => {
    const text = btn.dataset.tooltip;
    if (!text) return;
    tooltipEl.textContent = text;
    tooltipEl.classList.add('visible');
    positionTooltip(e);
  });
  btn.addEventListener('blur', hideTooltip);
});

function positionTooltip(e) {
  const x = e.clientX ?? e.target.getBoundingClientRect().left;
  const y = e.clientY ?? e.target.getBoundingClientRect().top;
  tooltipEl.style.left = Math.min(x + 12, window.innerWidth - 260) + 'px';
  tooltipEl.style.top  = (y - 52) + 'px';
}
function hideTooltip() {
  tooltipEl.classList.remove('visible');
  tooltipEl.setAttribute('aria-hidden', 'true');
}

/* ---------------------------------------------------------------
   ALGO CARDS — selección visual
   --------------------------------------------------------------- */
document.querySelectorAll('.algo-card input[type="radio"]').forEach(radio => {
  radio.addEventListener('change', () => {
    document.querySelectorAll('.algo-card .check-inner').forEach(c => {
      c.style.opacity = '0';
    });
    const inner = radio.closest('.algo-card').querySelector('.check-inner');
    if (inner) {
      inner.style.opacity = '1';
      inner.style.animation = 'none';
      inner.offsetHeight;
      inner.style.animation = '';
    }
  });
});

/* ---------------------------------------------------------------
   VALIDACIÓN DEL FORMULARIO
   --------------------------------------------------------------- */
const form          = z('patient-form');
const btnSubmit     = z('btn-submit');
const formError     = z('form-error');
const formErrorText = z('form-error-text');

const NUMERIC_FIELDS = [
  'edad', 'fraccion_eyeccion', 'creatinina_serica',
  'sodio_serico', 'cpk', 'plaquetas', 'tiempo',
];
const SELECT_FIELDS = ['genero', 'anemia', 'diabetes', 'presion_alta', 'fuma'];

function showError(msg) {
  formErrorText.textContent = msg;
  formError.hidden = false;
  formError.scrollIntoView({ behavior: 'smooth', block: 'center' });
}
function hideError()       { formError.hidden = true; }
function markFieldError(id){ const el = z(id); if (el) el.classList.add('error'); }
function clearFieldErrors(){ document.querySelectorAll('.field-input.error').forEach(el => el.classList.remove('error')); }

function validateForm() {
  clearFieldErrors();

  const algoEl = document.querySelector('input[name="algoritmo"]:checked');
  if (!algoEl) {
    showError('Por favor, selecciona un algoritmo (Paso 1) antes de continuar.');
    return null;
  }

  const nombre = z('nombre').value.trim();
  if (!nombre) {
    markFieldError('nombre');
    showError('Por favor, ingresa el nombre del paciente.');
    return null;
  }

  for (const field of NUMERIC_FIELDS) {
    const el  = z(field);
    const val = el.value.trim();
    if (val === '' || isNaN(Number(val))) {
      markFieldError(field);
      showError(`El campo "${FIELD_LABELS[field]}" es obligatorio y debe ser un número.`);
      return null;
    }
    const num = Number(val);
    if (num < Number(el.min) || num > Number(el.max)) {
      markFieldError(field);
      showError(`El valor de "${FIELD_LABELS[field]}" debe estar entre ${el.min} y ${el.max}.`);
      return null;
    }
  }

  for (const field of SELECT_FIELDS) {
    const el = z(field);
    if (el.value === '') {
      el.classList.add('error');
      showError(`Por favor, completa el campo "${FIELD_LABELS[field]}".`);
      return null;
    }
  }

  return {
    algoritmo:          algoEl.value,
    nombre,
    edad:              Number(z('edad').value),
    genero:            Number(z('genero').value),
    fraccion_eyeccion: Number(z('fraccion_eyeccion').value),
    creatinina_serica: Number(z('creatinina_serica').value),
    sodio_serico:      Number(z('sodio_serico').value),
    cpk:               Number(z('cpk').value),
    plaquetas:         Number(z('plaquetas').value),
    tiempo:            Number(z('tiempo').value),
    anemia:            Number(z('anemia').value),
    diabetes:          Number(z('diabetes').value),
    presion_alta:      Number(z('presion_alta').value),
    fuma:              Number(z('fuma').value),
  };
}

/* ---------------------------------------------------------------
   RECOMENDACIONES
   --------------------------------------------------------------- */
function buildRecommendations(datos, isCritical) {
  const list = [...(isCritical ? RECS.critical : RECS.stable)];
  if (datos.anemia      === 1) list.push(RECS.anemia);
  if (datos.diabetes    === 1) list.push(RECS.diabetes);
  if (datos.presion_alta=== 1) list.push(RECS.presion_alta);
  if (datos.fuma        === 1) list.push(RECS.fuma);
  if (datos.cpk               > 400) list.push(RECS.cpk_high);
  if (datos.creatinina_serica > 1.5) list.push(RECS.creatinina_high);
  if (datos.sodio_serico      < 135) list.push(RECS.sodio_low);
  if (datos.fraccion_eyeccion < 40)  list.push(RECS.eyeccion_low);

  // Deduplicar
  const seen = new Set();
  return list.filter(r => { if (seen.has(r.text)) return false; seen.add(r.text); return true; });
}

/* ---------------------------------------------------------------
   RENDERIZAR RESULTADO
   --------------------------------------------------------------- */
function renderResult(datos, apiResponse) {
  const isCritical   = apiResponse.prediccion === 1;
  const isNaiveBayes = apiResponse.algoritmo  === 'bayes';

  /* Header */
  const iconWrap = z('result-icon-wrap');
  iconWrap.className   = 'result-icon-wrap ' + (isCritical ? 'critical' : 'stable');
  iconWrap.textContent = isCritical ? '⚠️' : '✅';

  z('result-algo-tag').textContent = isNaiveBayes
    ? 'Naive Bayes · Preciso'
    : 'OneR · Común';

  z('result-patient').textContent = datos.nombre;

  const statusEl = z('result-status-text');
  statusEl.className   = 'result-status-text ' + (isCritical ? 'critical' : 'stable');
  statusEl.textContent = isCritical
    ? '⚠️ Estado CRÍTICO — Riesgo elevado de falla cardíaca'
    : '✅ Estado ESTABLE — Riesgo bajo de falla cardíaca';

  /* Confianza (solo Bayes) */
  const confSection = z('result-confidence');
  if (isNaiveBayes) {
    confSection.hidden = false;
    const pct = Math.round(apiResponse.confianza * 100);
    z('confidence-value').textContent = pct + '%';
    const bar = z('confidence-bar');
    bar.style.background = isCritical
      ? 'linear-gradient(90deg, #ffdad6, #ba1a1a)'
      : 'linear-gradient(90deg, #b1cdbf, #486157)';
    setTimeout(() => { bar.style.width = pct + '%'; }, 100);
  } else {
    confSection.hidden = true;
    z('confidence-bar').style.width = '0%';
  }

  /* Variable crítica (solo OneR) */
  const critVarSection = z('result-critical-var');
  if (!isNaiveBayes) {
    critVarSection.hidden = false;
    z('crit-value').textContent = apiResponse.variable_nombre ?? apiResponse.variable_critica;
  } else {
    critVarSection.hidden = true;
  }

  /* Resumen de datos */
  const summaryList = z('summary-list');
  summaryList.innerHTML = '';
  const rows = [
    ['edad',              datos.edad + ' años'],
    ['genero',            GENERO_LABEL[datos.genero]],
    ['fraccion_eyeccion', datos.fraccion_eyeccion + ' %'],
    ['creatinina_serica', datos.creatinina_serica + ' mg/dL'],
    ['sodio_serico',      datos.sodio_serico + ' mEq/L'],
    ['cpk',               datos.cpk + ' U/L'],
    ['plaquetas',         Number(datos.plaquetas).toLocaleString('es-CO') + ' /µL'],
    ['tiempo',            datos.tiempo + ' días'],
    ['anemia',            BINARIO_LABEL[datos.anemia]],
    ['diabetes',          BINARIO_LABEL[datos.diabetes]],
    ['presion_alta',      BINARIO_LABEL[datos.presion_alta]],
    ['fuma',              BINARIO_LABEL[datos.fuma]],
  ];
  rows.forEach(([key, val]) => {
    const li = document.createElement('li');
    li.className = 'summary-item';
    li.innerHTML = `<span class="s-key">${FIELD_LABELS[key]}</span><span class="s-val">${val}</span>`;
    summaryList.appendChild(li);
  });

  /* Recomendaciones */
  const recList = z('rec-list');
  recList.innerHTML = '';
  buildRecommendations(datos, isCritical).forEach(rec => {
    const li = document.createElement('li');
    li.className = 'rec-item';
    li.innerHTML = `<div class="rec-icon" aria-hidden="true">${rec.icon}</div><span>${rec.text}</span>`;
    recList.appendChild(li);
  });

  /* Mostrar sección */
  const resultSection = z('result-section');
  resultSection.hidden = false;
  setTimeout(() => resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' }), 50);
}

/* ---------------------------------------------------------------
   FORM SUBMIT → llamada real a la API
   --------------------------------------------------------------- */
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  hideError();

  const datos = validateForm();
  if (!datos) return;

  /* Mostrar loading */
  btnSubmit.disabled = true;
  btnSubmit.classList.add('loading');

  try {
    const response = await fetch(API_URL, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(datos),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.error ?? `Error del servidor (${response.status})`);
    }

    const apiResponse = await response.json();
    renderResult(datos, apiResponse);

  } catch (err) {
    if (err.message.includes('fetch') || err.message.includes('Failed')) {
      showError('No se pudo conectar con el servidor. Asegúrate de que api.py esté ejecutándose en http://localhost:5000');
    } else {
      showError('Error: ' + err.message);
    }
  } finally {
    btnSubmit.disabled = false;
    btnSubmit.classList.remove('loading');
  }
});

/* ---------------------------------------------------------------
   REINICIAR
   --------------------------------------------------------------- */
z('btn-restart').addEventListener('click', () => {
  form.reset();
  clearFieldErrors();
  hideError();
  z('confidence-bar').style.width = '0%';
  z('result-section').hidden = true;
  document.querySelectorAll('.algo-card input[type="radio"]').forEach(r => {
    r.checked = false;
    const inner = r.closest('.algo-card').querySelector('.check-inner');
    if (inner) inner.style.opacity = '0';
  });
  z('formulario').scrollIntoView({ behavior: 'smooth', block: 'start' });
});

/* ---------------------------------------------------------------
   Limpiar errores al corregir campos
   --------------------------------------------------------------- */
document.querySelectorAll('.field-input').forEach(input => {
  input.addEventListener('input',  () => { input.classList.remove('error'); hideError(); });
  input.addEventListener('change', () => { input.classList.remove('error'); hideError(); });
});
