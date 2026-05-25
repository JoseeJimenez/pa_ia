
# Proyecto: Predicción de riesgo en pacientes cardíacos (pa_ia)

Este proyecto es una pequeña aplicación de investigación que expone varios clasificadores de máquina
aprendizaje entrenados sobre el dataset `heart_failure_clinical_records_dataset.csv` para predecir
el riesgo (muerte/estable) en pacientes con datos clínicos. Incluye una API en Python (Flask)
y una interfaz web estática con controles interactivos (sliders) para probar distintos modelos.

Características principales
- API REST que sirve predicciones desde múltiples modelos: Naive Bayes, OneR (regla simple),
	Decision Tree (J48), Random Forest, K-Nearest Neighbors (IBk), Logistic Regression.
- Frontend estático (HTML/CSS/JS) con selección de algoritmo, sliders con feedback visual,
	y renderizado de probabilidades/confianza.
- Manejo de escalado (scaler) cuando el modelo lo requiere.

Estructura del repositorio

- `api.py` — Flask app que carga los modelos y sirve el endpoint `/predict`.
- `main.py` — script auxiliar (si existe) para pruebas locales.
- `heart_failure_clinical_records_dataset.csv` — dataset usado para entrenamiento.
- `requerimientos.txt` — dependencias Python.
- `frontend/` — archivos estáticos:
	- `index.html` — interfaz de usuario.
	- `script.js` — lógica de la UI y llamadas al API.
	- `style.css` — estilos y tokens visuales.

Requisitos

- Python 3.8+ (la base del proyecto usa 3.11 durante el desarrollo).
- Pip para instalar dependencias.

Instalación rápida

1. Crear y activar un entorno virtual (opcional pero recomendado):

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

2. Instalar dependencias:

```bash
pip install -r requerimientos.txt
```

Ejecutar la API (servidor local)

1. Desde la carpeta `pa_ia` (donde está `api.py`), ejecutar:

```bash
python api.py
```

2. Por defecto la API escucha en `http://localhost:5000` y tiene habilitado CORS para pruebas desde
	 archivos locales o servidores estáticos.

Usar el frontend

- Abrir `pa_ia/frontend/index.html` en un navegador (o servir `frontend/` por un servidor estático).
- Seleccionar un algoritmo, ajustar sliders y enviar para ver la predicción y la probabilidad.

Endpoint principal

- `POST /predict` — recibe un JSON con las variables del paciente y un campo `algoritmo`.

Ejemplo de payload (JSON):

```json
{
	"edad": 64,
	"anaemia": 0,
	"creatinina_serica": 1.1,
	"cpk": 150,
	"diabetes": 0,
	"fraccion_eyeccion": 35,
	"hipertension": 0,
	"plaquetas": 263358,
	"sodio_serico": 137,
	"sexo": 1,
	"fuma": 0,
	"tiempo": 130,
	"algoritmo": "rf"
}
```

Ejemplo de `curl`:

```bash
curl -X POST http://localhost:5000/predict \
	-H "Content-Type: application/json" \
	-d '{"edad":64,"anaemia":0,"creatinina_serica":1.1,"cpk":150,"diabetes":0,"fraccion_eyeccion":35,"hipertension":0,"plaquetas":263358,"sodio_serico":137,"sexo":1,"fuma":0,"tiempo":130,"algoritmo":"rf"}'
```

Ejemplo de respuesta (JSON):

```json
{
	"pred": 0,
	"prob_estable": 0.96,
	"prob_critico": 0.04,
	"algoritmo": "rf"
}
```

Notas y consideraciones

- Los nombres de las variables deben coincidir exactamente con los que espera la API.
- Algunos modelos (KNN, Logistic, Naive Bayes) requieren que las entradas estén escaladas; la
	aplicación aplica `scaler.transform` donde corresponde.
- `OneR` devuelve además una `variable_critica` que indica la variable determinante según la regla simple.
- Si se van a exponer los modelos en producción, considero recomendable persistir los modelos
	entrenados (pickle/joblib) y añadir validaciones más estrictas del payload entrante.

Cómo funciona

- Flujo general:
	1. El usuario ajusta los controles en el frontend (`frontend/index.html`) y selecciona un algoritmo.
	2. El frontend construye un JSON con las variables del paciente y hace `POST /predict` al API.
	3. `api.py` recibe el payload, lo valida y lo convierte en un vector en el orden esperado.
	4. Si el modelo requiere escalado (p. ej. KNN, Logistic, Naive Bayes), la aplicación aplica `scaler.transform`.
	5. Se selecciona el modelo según el campo `algoritmo` y se ejecuta la predicción.
	6. La API devuelve un JSON con la predicción (`pred`), probabilidades (`prob_estable`, `prob_critico`) y,
		 en el caso de `OneR`, la `variable_critica` asociada.

- Respuesta típica del API (campos relevantes):
	- `pred`: 0 (estable) o 1 (alto riesgo)
	- `prob_estable`: probabilidad estimada de clase "estable"
	- `prob_critico`: probabilidad estimada de clase "crítico/muerte"
	- `algoritmo`: algoritmo usado (p. ej. `bayes`, `rf`, `j48`)
	- `variable_critica`: (solo `OneR`) variable que determinó la regla simple

- Consideraciones internas:
	- El orden de las columnas y los nombres deben coincidir con lo que espera `parse_patient()` en `api.py`.
	- El frontend aplica coloración y mensajes en función de rangos 'saludables' declarados en los atributos
		de los controles (sliders). Esa lógica está en `frontend/script.js`.
	- Para producción conviene serializar (pickle/joblib) los modelos y añadir validación y autenticación.


Licencia

- Este repositorio es para fines educativos/internos. Añade una licencia si planeas compartirlo públicamente.

----
