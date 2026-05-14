import pandas as pd
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler

df = pd.read_csv('heart_failure_clinical_records_dataset.csv')
X = df.drop('DEATH_EVENT', axis=1)
y = df['DEATH_EVENT']
nombres_columnas = X.columns

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

#Modelo de Bayes con todas las variables
modelo_bayes = GaussianNB()
modelo_bayes.fit(X_scaled, y)

#Modelo OneR con la variable más crítica
modelo_oner = DecisionTreeClassifier(max_depth=1, random_state=42)
modelo_oner.fit(X, y)

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
    print("\n" + "="*45)#45 y lo que sea ya
    print("   SISTEMA DE SELECCIÓN DE ALGORITMOS IA")
    print("="*45)
    print("1. Naive Bayes (Probabilidades completas)")
    print("2. OneR (Basado en la variable más crítica)")
    
    opcion_algoritmo = input("\nElija el algoritmo para el diagnóstico (1 o 2): ")
    
    if opcion_algoritmo not in ['1', '2']:
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

    print("\n" + "*"*45)
    print(f" RESULTADO PARA: {nombre_paciente.upper()} ")
    print("*"*45)

    if opcion_algoritmo == '1':
        # Uso de Bayes
        paciente_escalado = scaler.transform(paciente_df)
        res = modelo_bayes.predict(paciente_escalado)[0]
        prob = modelo_bayes.predict_proba(paciente_escalado)[0]
        
        estado = " CRÍTICO" if res == 1 else " ESTABLE"
        print(f"Algoritmo: Naive Bayes")
        print(f"Diagnóstico: {estado}")
        print(f"Confianza: {prob[res]*100:.2f}%")

    else:
        # Uso de OneR
        res = modelo_oner.predict(paciente_df)[0]
        variable_critica = nombres_columnas[modelo_oner.feature_importances_.argmax()]
        
        estado = " CRÍTICO" if res == 1 else " ESTABLE"
        print(f"Algoritmo: OneR")
        print(f"Variable determinante: {variable_critica}")
        print(f"Diagnóstico: {estado}")

    print("*"*45)

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