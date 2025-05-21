from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict
import groq
import os
import json
import sys
from datetime import datetime

# Configura tu API key de Groq
os.environ["GROQ_API_KEY"] = ""

client = groq.Groq(api_key=os.environ["GROQ_API_KEY"])

class Pregunta(TypedDict):
    id: str
    texto: str

class HRState(TypedDict):
    respuestas: dict
    resultado_json: str
    preguntas: List[Pregunta]

# Función para cargar preguntas desde JSON
def cargar_preguntas() -> List[Pregunta]:
    try:
        ruta_archivo = os.path.join(os.path.dirname(__file__), 'preguntas.json')
        if not os.path.exists(ruta_archivo):
            print(f"Error: No se encuentra el archivo de preguntas en {ruta_archivo}")
            return []
            
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not data.get('preguntas'):
                print("Error: El archivo JSON no contiene la clave 'preguntas'")
                return []
                
            preguntas = data['preguntas']
            if not preguntas:
                print("Error: La lista de preguntas está vacía")
                return []
                
            # Validar estructura de cada pregunta
            for pregunta in preguntas:
                if not isinstance(pregunta, dict) or 'id' not in pregunta or 'texto' not in pregunta:
                    print(f"Error: Estructura inválida en pregunta: {pregunta}")
                    return []
                    
            return preguntas
            
    except json.JSONDecodeError as e:
        print(f"Error al decodificar el JSON: {e}")
        return []
    except Exception as e:
        print(f"Error inesperado al cargar preguntas: {e}")
        return []

# Función para validar respuesta
def validar_respuesta(pregunta: str, respuesta: str) -> bool:
    prompt = f"""
Analiza la siguiente respuesta y determina si responde a la pregunta.

Pregunta: "{pregunta}"
Respuesta del candidato: "{respuesta}"

Responde solo con:
- sí: si la respuesta esta directamente relacionada con la pregunta.
- no: si la respuesta irrelevante o no responde a la pregunta.
"""

    try:
        response = client.chat.completions.create(
            model='llama3-70b-8192',
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        resultado = response.choices[0].message.content.strip().lower()
        print("[VALIDACIÓN LLM]:", resultado)  # Para depurar
        return "sí" in resultado
    except Exception as e:
        print("[ERROR EN VALIDACIÓN]:", e)
        return True  # fallback para no detener el flujo

# Lógica para preguntar con validación
def hacer_pregunta(state: HRState, pregunta: Pregunta) -> HRState:
    while True:
        respuesta = input(pregunta['texto'] + " ")
        if validar_respuesta(pregunta['texto'], respuesta):
            state['respuestas'][pregunta['id']] = respuesta
            return state
        else:
            print("La respuesta no parece adecuada. Intenta ser más claro.")

# Nodos de preguntas dinámicos
def crear_nodo_pregunta(pregunta: Pregunta):
    def nodo_pregunta(state: HRState) -> HRState:
        return hacer_pregunta(state, pregunta)
    return nodo_pregunta

# Nodo final para generar JSON
def generar_json(state: HRState) -> HRState:
    # Crear directorio para resultados si no existe
    resultados_dir = os.path.join(os.path.dirname(__file__), 'resultados')
    os.makedirs(resultados_dir, exist_ok=True)
    
    # Generar nombre de archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"entrevista_{timestamp}.json"
    ruta_archivo = os.path.join(resultados_dir, nombre_archivo)
    
    # Crear estructura del resultado
    resultado = {
        'fecha': datetime.now().isoformat(),
        'entrevista': [
            {
                'pregunta': next(p['texto'] for p in state['preguntas'] if p['id'] == clave),
                'respuesta': respuesta
            }
            for clave, respuesta in state['respuestas'].items()
        ]
    }
    
    # Guardar en archivo
    try:
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        print(f"\nResultado guardado en: {ruta_archivo}")
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")
    
    state['resultado_json'] = json.dumps(resultado, ensure_ascii=False, indent=2)
    return state

# Cargar preguntas
preguntas = cargar_preguntas()
if not preguntas:
    print("No se pudieron cargar las preguntas. Verifica el archivo preguntas.json")
    sys.exit(1)

# Construcción del grafo
builder = StateGraph(HRState)

# Añadir nodos dinámicamente basados en las preguntas
for i, pregunta in enumerate(preguntas):
    builder.add_node(pregunta['id'], crear_nodo_pregunta(pregunta))
    
    # Conectar nodos
    if i == 0:
        builder.set_entry_point(pregunta['id'])
    else:
        builder.add_edge(preguntas[i-1]['id'], pregunta['id'])

# Añadir nodo final
builder.add_node("generar_json", generar_json)
builder.add_edge(preguntas[-1]['id'], "generar_json")
builder.add_edge("generar_json", END)

# Compilar el grafo
graph = builder.compile()

# Visualizar el grafo usando Mermaid
try:
    # Crear directorio para imágenes si no existe
    imgs_dir = os.path.join(os.path.dirname(__file__), 'imgs')
    os.makedirs(imgs_dir, exist_ok=True)
    
    # Generar nombre de archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file_path = os.path.join(imgs_dir, f'grafo_entrevista_{timestamp}.png')
    
    # Generar y guardar la imagen del grafo
    _ = (
        graph
        .get_graph()
        .draw_mermaid_png(output_file_path=output_file_path)
    )
    print(f"\nGrafo guardado en: {output_file_path}")
except Exception as e:
    print("No se pudo visualizar el grafo:", e)

# Ejecutar
initial_state = {
    "respuestas": {}, 
    "resultado_json": "",
    "preguntas": preguntas
}
final_state = graph.invoke(initial_state)


# Mostrar resultados
print("\nJSON generado:")
print(final_state["resultado_json"])