"""
FUENTES MÉDICAS Y DE CLASIFICACIÓN (TRIAGE):
1. Organización Mundial de la Salud (OMS). Interagency Integrated Triage Tool (IITT).
   Enlace oficial: https://www.who.int/tools/triage
2. Grupo de Triage de Manchester (MTS). 
"""
import pandas as pd
import joblib
import re
import unicodedata
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

def limpiar_texto(texto):
    """
    Normalización de texto profesional:
    - Minúsculas, sin acentos, sin puntuación, sin espacios extra.
    """
    if not isinstance(texto, str):
        return ""
    # Pasar a minúsculas
    texto = texto.lower()
    # Eliminar acentos
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    # Eliminar cualquier cosa que no sea letra a-z o espacio
    texto = re.sub(r'[^a-z\s]', '', texto)
    # Eliminar dobles espacios
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

def iniciar_entrenamiento():
    print("Cargando dataset oficial de urgencias...")
    try:
        # Cargamos el archivo completo
        # Usamos engine='python' para mayor estabilidad al leer CSVs editados manualmente
        df = pd.read_csv('dataset_sintomas.csv', sep=',', engine='python')
        
        # FILTRO: Eliminamos las líneas de comentarios (#) que Pandas pudo leer como datos
        df = df[~df.iloc[:, 0].astype(str).str.startswith('#')]
        
        # FORZAMOS CABECERAS: Si leyó mal los títulos, aquí los reasignamos por posición
        # Esto soluciona el KeyError: 'sintomas' definitivamente
        df.columns = ['sintomas', 'especialidad', 'urgencia']
        
        # Limpiamos espacios en blanco accidentales en los nombres de las columnas
        df.columns = df.columns.str.strip()
        
    except Exception as e:
        print(f" Error crítico al leer el archivo: {e}")
        return

    # Verificación de seguridad
    if 'sintomas' not in df.columns:
        print(f" Error: No se detectó la columna 'sintomas'. Columnas actuales: {list(df.columns)}")
        return

    print("Aplicando Normalización de Texto (NLP)...")
    # Aseguramos que los datos sean tratados como texto antes de limpiar
    df['sintomas_limpios'] = df['sintomas'].astype(str).apply(limpiar_texto)

    # Creamos la etiqueta objetivo combinando especialidad y urgencia
    # Usamos .str.strip() para evitar que espacios al final rompan la lógica
    df['etiqueta_objetivo'] = df['especialidad'].astype(str).str.strip() + "|" + df['urgencia'].astype(str).str.strip()

    X = df['sintomas_limpios']
    y = df['etiqueta_objetivo']

    print("Entrenando la Inteligencia Artificial (TF-IDF + Naive Bayes)...")
    # TF-IDF: Convierte palabras en importancia estadística
    # MultinomialNB: Clasifica el texto basándose en probabilidades
    modelo = make_pipeline(TfidfVectorizer(), MultinomialNB())
    modelo.fit(X, y)

    # SERIALIZACIÓN: Guardamos el modelo entrenado (el cerebro)
    archivo_modelo = "modelo_triage.pkl"
    joblib.dump(modelo, archivo_modelo)

    print(f"¡Éxito! El archivo '{archivo_modelo}' ha sido generado correctamente.")
    print("El modelo está listo para ser integrado en el backend (main.py).")

if __name__ == "__main__":
    iniciar_entrenamiento()