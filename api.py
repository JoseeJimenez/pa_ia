"""
api.py — Servidor Flask para el diagnóstico cardíaco con IA.
Expone los modelos Naive Bayes y OneR entrenados con el dataset real.

Instalar dependencias:
    pip install flask flask-cors pandas scikit-learn

Ejecutar:
    python api.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# ─────────────────────────────────────────
#  Cargar y entrenar modelos al iniciar
# ─────────────────────────────────────────
df = pd.read_csv('heart_failure_clinical_records_dataset.csv')
X = df.drop('DEATH_EVENT', axis=1)
y = df['DEATH_EVENT']
COLUMN_ORDER = list(X.columns)   # orden exacto del dataset

# Naive Bayes con escalado
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
modelo_bayes = GaussianNB()
modelo_bayes.fit(X_scaled, y)

# OneR (árbol de profundidad 1)
modelo_oner = DecisionTreeClassifier(max_depth=1, random_state=42)
modelo_oner.fit(X, y)

# Variable crítica de OneR
VARIABLE_CRITICA = COLUMN_ORDER[modelo_oner.feature_importances_.argmax()]

# J48 (árbol de decisión completo)
modelo_j48 = DecisionTreeClassifier(random_state=42)
modelo_j48.fit(X, y)

# Random Forest
modelo_rf = RandomForestClassifier(n_estimators=100, random_state=42)
modelo_rf.fit(X, y)

# IBk / KNN (usa datos escalados)
modelo_ibk = KNeighborsClassifier(n_neighbors=5)
modelo_ibk.fit(X_scaled, y)

# Regresión logística (usa datos escalados)
modelo_logistic = LogisticRegression(random_state=42, max_iter=1000)
modelo_logistic.fit(X_scaled, y)

NOMBRES_VARIABLES = {
    'age':                    'Edad',
    'anaemia':                'Anemia',
    'creatinine_phosphokinase': 'CPK (Creatina Quinasa)',
    'diabetes':               'Diabetes',
    'ejection_fraction':      'Fracción de Eyección',
    'high_blood_pressure':    'Presión Alta',
    'platelets':              'Plaquetas',
    'serum_creatinine':       'Creatinina Sérica',
    'serum_sodium':           'Sodio Sérico',
    'sex':                    'Género',
    'smoking':                'Fuma',
    'time':                   'Tiempo de Seguimiento',
}

# ─────────────────────────────────────────
#  App Flask
# ─────────────────────────────────────────
app = Flask(__name__)
CORS(app)   # permite peticiones desde el frontend (localhost)


def parse_patient(data: dict) -> pd.DataFrame:
    """
    Convierte el JSON del frontend al DataFrame con el
    orden de columnas exacto que espera el modelo.
    """
    # Mapa: clave del frontend → nombre de columna del CSV
    mapping = {
        'edad':              'age',
        'anemia':            'anaemia',
        'cpk':               'creatinine_phosphokinase',
        'diabetes':          'diabetes',
        'fraccion_eyeccion': 'ejection_fraction',
        'presion_alta':      'high_blood_pressure',
        'plaquetas':         'platelets',
        'creatinina_serica': 'serum_creatinine',
        'sodio_serico':      'serum_sodium',
        'genero':            'sex',
        'fuma':              'smoking',
        'tiempo':            'time',
    }

    row = {csv_col: float(data[frontend_key])
           for frontend_key, csv_col in mapping.items()}

    return pd.DataFrame([row], columns=COLUMN_ORDER)


# ─────────────────────────────────────────
#  Endpoints
# ─────────────────────────────────────────

@app.route('/predict', methods=['POST'])
def predict():
    """
    Recibe JSON con los datos del paciente y el algoritmo elegido.
    Retorna el diagnóstico, probabilidad (Bayes) o variable crítica (OneR).

    Body esperado:
    {
      "algoritmo": "bayes" | "oner",
      "nombre": "...",
      "edad": 60,
      "anemia": 0,
      "cpk": 100,
      "diabetes": 1,
      "fraccion_eyeccion": 38,
      "presion_alta": 0,
      "plaquetas": 250000,
      "creatinina_serica": 1.1,
      "sodio_serico": 137,
      "genero": 1,
      "fuma": 0,
      "tiempo": 130
    }
    """
    try:
        data = request.get_json(force=True)
        algoritmo = data.get('algoritmo', 'bayes')
        paciente_df = parse_patient(data)

        # Naive Bayes (usa escalado)
        if algoritmo == 'bayes':
            paciente_escalado = scaler.transform(paciente_df)
            prediccion = int(modelo_bayes.predict(paciente_escalado)[0])
            probabilidades = modelo_bayes.predict_proba(paciente_escalado)[0].tolist()
            confianza = probabilidades[prediccion]

            return jsonify({
                'algoritmo':  'bayes',
                'prediccion': prediccion,
                'confianza':  round(confianza, 4),
                'prob_estable':  round(probabilidades[0], 4),
                'prob_critico':  round(probabilidades[1], 4),
            })

        # OneR — variable crítica
        if algoritmo == 'oner':
            prediccion = int(modelo_oner.predict(paciente_df)[0])
            var_critica_csv = VARIABLE_CRITICA
            var_critica_nombre = NOMBRES_VARIABLES.get(var_critica_csv, var_critica_csv)

            return jsonify({
                'algoritmo':         'oner',
                'prediccion':        prediccion,
                'variable_critica':  var_critica_csv,
                'variable_nombre':   var_critica_nombre,
            })

        # J48 (Decision Tree completo)
        if algoritmo == 'j48':
            prediccion = int(modelo_j48.predict(paciente_df)[0])
            probabilidades = modelo_j48.predict_proba(paciente_df)[0].tolist()
            confianza = probabilidades[prediccion]
            return jsonify({
                'algoritmo': 'j48',
                'prediccion': prediccion,
                'confianza': round(confianza, 4),
                'prob_estable': round(probabilidades[0], 4),
                'prob_critico': round(probabilidades[1], 4),
            })

        # Random Forest
        if algoritmo == 'rf':
            prediccion = int(modelo_rf.predict(paciente_df)[0])
            probabilidades = modelo_rf.predict_proba(paciente_df)[0].tolist()
            confianza = probabilidades[prediccion]
            return jsonify({
                'algoritmo': 'rf',
                'prediccion': prediccion,
                'confianza': round(confianza, 4),
                'prob_estable': round(probabilidades[0], 4),
                'prob_critico': round(probabilidades[1], 4),
            })

        # IBk / KNN (usa escalado)
        if algoritmo == 'ibk' or algoritmo == 'knn':
            paciente_escalado = scaler.transform(paciente_df)
            prediccion = int(modelo_ibk.predict(paciente_escalado)[0])
            probabilidades = modelo_ibk.predict_proba(paciente_escalado)[0].tolist()
            confianza = probabilidades[prediccion]
            return jsonify({
                'algoritmo': 'ibk',
                'prediccion': prediccion,
                'confianza': round(confianza, 4),
                'prob_estable': round(probabilidades[0], 4),
                'prob_critico': round(probabilidades[1], 4),
            })

        # Regresión logística (usa escalado)
        if algoritmo == 'logistic' or algoritmo == 'logreg':
            paciente_escalado = scaler.transform(paciente_df)
            prediccion = int(modelo_logistic.predict(paciente_escalado)[0])
            probabilidades = modelo_logistic.predict_proba(paciente_escalado)[0].tolist()
            confianza = probabilidades[prediccion]
            return jsonify({
                'algoritmo': 'logistic',
                'prediccion': prediccion,
                'confianza': round(confianza, 4),
                'prob_estable': round(probabilidades[0], 4),
                'prob_critico': round(probabilidades[1], 4),
            })

        return jsonify({'error': f'Algoritmo desconocido: {algoritmo}'}), 400

    except KeyError as e:
        return jsonify({'error': f'Campo faltante: {e}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Verificar que el servidor está activo."""
    return jsonify({
        'status': 'ok',
        'variable_critica_oner': VARIABLE_CRITICA,
        'columnas': COLUMN_ORDER,
    })


# ─────────────────────────────────────────
#  Inicio
# ─────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 50)
    print("  Serene Health — API de Diagnóstico Cardíaco")
    print("=" * 50)
    print(f"  Variable crítica (OneR): {VARIABLE_CRITICA}")
    print(f"  Servidor en: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)
