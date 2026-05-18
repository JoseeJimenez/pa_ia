import pandas as pd
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

df = pd.read_csv('heart_failure_clinical_records_dataset.csv')
X = df.drop('DEATH_EVENT', axis=1)
y = df['DEATH_EVENT']
nombres_columnas = X.columns

# Escalacion de datos, segun la IA eso funciona para los metodos Bayes, KNN y Regresión Logística
#Mejora los resultados 
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)


# 1. Naive Bayes
modelo_bayes = GaussianNB()
modelo_bayes.fit(X_scaled, y)

# 2. OneR 
modelo_oner = DecisionTreeClassifier(max_depth=1, random_state=42)
modelo_oner.fit(X, y)

# 3. J48 
modelo_j48 = DecisionTreeClassifier(random_state=42)
modelo_j48.fit(X, y)

# 4. Random Forest
modelo_rf = RandomForestClassifier(n_estimators=100, random_state=42)
modelo_rf.fit(X, y)

# 5. IBk, este fue recomendado por Claude, pero ni idea 
modelo_ibk = KNeighborsClassifier(n_neighbors=5)
modelo_ibk.fit(X_scaled, y)

# 6. Logistic, este tambien fue recomendacion de Claude 
modelo_logistic = LogisticRegression(random_state=42)
modelo_logistic.fit(X_scaled, y)


def obtener_dato(mensaje, es_binario=False):
    while True:
        try:
            valor = float(input(mensaje))
            if es_binario and valor not in [0, 1]:
                print(" Por favor, ingresa 0 para No o 1 para Sí.")
                continue
            return valor
        except ValueError:
            print(" Entrada no válida. Ingresa un número.")


ejecutando = True

while ejecutando:
    print("\n" + "="*50)
    print("   SISTEMA DE SELECCIÓN DE ALGORITMOS IA (WEKA)")
    print("="*50)
    print("1. Naive Bayes (Probabilidades completas)")
    print("2. OneR (Basado en la variable más crítica)")
    print("3. J48 (Árbol de Decisión Completo)")
    print("4. Random Forest (Ensamble de múltiples árboles)")
    print("5. IBk / KNN (Clasificación por vecindad/similitud)")
    print("6. Logistic (Regresión Logística Estadística)")
    
    opcion_algoritmo = input("\nElija el algoritmo para el diagnóstico (1 al 6): ")
    
    if opcion_algoritmo not in ['1', '2', '3', '4', '5', '6']:
        print(" Opción no válida. Intente de nuevo.")
        continue

    print("\n--- Datos del Paciente ---")
    nombre_paciente = input("Nombre: ")
    
    datos_usuario = []
    datos_usuario.append(obtener_dato("1. Edad: "))
    datos_usuario.append(obtener_dato("2. ¿Anemia? (1:Si, 0:No): ", True))
    datos_usuario.append(obtener_dato("3. CPK: "))
    datos_usuario.append(obtener_dato("4. ¿Diabetes? (1:Si, 0:No): ", True))
    datos_usuario.append(obtener_dato("5. Fracción de Eyección: "))
    datos_usuario.append(obtener_dato("6. ¿Presión Alta? (1:Si, 0:No): ", True))
    datos_usuario.append(obtener_dato("7. Plaquetas: "))
    datos_usuario.append(obtener_dato("8. Creatinina Sérica: "))
    datos_usuario.append(obtener_dato("9. Sodio Sérico: "))
    datos_usuario.append(obtener_dato("10. Género (1:H, 0:M): ", True))
    datos_usuario.append(obtener_dato("11. ¿Fuma? (1:Si, 0:No): ", True))
    datos_usuario.append(obtener_dato("12. Tiempo de seguimiento: "))

    paciente_df = pd.DataFrame([datos_usuario], columns=nombres_columnas)
    paciente_escalado = scaler.transform(paciente_df)

    print("\n" + "*"*50)
    print(f" RESULTADO PARA: {nombre_paciente.upper()} ")
    print("*"*50)

    if opcion_algoritmo == '1':
        res = modelo_bayes.predict(paciente_escalado)[0]
        prob = modelo_bayes.predict_proba(paciente_escalado)[0]
        print(f"Algoritmo: Naive Bayes")
        print(f"Diagnóstico: {'CRÍTICO' if res == 1 else 'ESTABLE'}")
        print(f"Confianza: {prob[res]*100:.2f}%")

    elif opcion_algoritmo == '2':
        res = modelo_oner.predict(paciente_df)[0]
        variable_critica = nombres_columnas[modelo_oner.feature_importances_.argmax()]
        print(f"Algoritmo: OneR")
        print(f"Variable determinante: {variable_critica}")
        print(f"Diagnóstico: {'CRÍTICO' if res == 1 else 'ESTABLE'}")

    elif opcion_algoritmo == '3':
        res = modelo_j48.predict(paciente_df)[0]
        print(f"Algoritmo: J48 (Árbol Completo)")
        print(f"Diagnóstico: {'CRÍTICO' if res == 1 else 'ESTABLE'}")

    elif opcion_algoritmo == '4':
        res = modelo_rf.predict(paciente_df)[0]
        prob = modelo_rf.predict_proba(paciente_df)[0]
        print(f"Algoritmo: Random Forest")
        print(f"Diagnóstico: {'CRÍTICO' if res == 1 else 'ESTABLE'}")
        print(f"Confianza del Bosque: {prob[res]*100:.2f}%")

    elif opcion_algoritmo == '5':
        res = modelo_ibk.predict(paciente_escalado)[0]
        prob = modelo_ibk.predict_proba(paciente_escalado)[0]
        print(f"Algoritmo: IBk (KNN)")
        print(f"Diagnóstico: {'CRÍTICO' if res == 1 else 'ESTABLE'}")
        print(f"Votos de vecinos: {prob[res]*100:.2f}%")

    elif opcion_algoritmo == '6':
        res = modelo_logistic.predict(paciente_escalado)[0]
        prob = modelo_logistic.predict_proba(paciente_escalado)[0]
        print(f"Algoritmo: Logistic Regression")
        print(f"Diagnóstico: {'CRÍTICO' if res == 1 else 'ESTABLE'}")
        print(f"Probabilidad estadística: {prob[res]*100:.2f}%")

    print("*"*50)

    while True:
        salir = input(f"\n¿Desea realizar otro análisis? (Si/No): ").upper()
        if salir in ['S', 'SI']:
            break
        elif salir in ['N', 'NO']:
            ejecutando = False
            break
        else:
            print("Escriba 'Si' o 'No'.")

print("\nCerrando sistema médico interactivo...")