"""
Módulo de registro y reporte de estadísticas de las predicciones realizadas.

Cada predicción se exporta como una línea JSON en un archivo de texto
(formato JSON Lines). A partir de ese archivo se construye el reporte:
    - Número total de predicciones realizadas por cada categoría.
    - Últimas 5 predicciones realizadas.
    - Fecha de la última predicción.

La ruta del archivo se configura con la variable de entorno RUTA_ESTADISTICAS
(por defecto: data/predicciones.jsonl junto a este módulo).
"""

import json
import os
import threading
from datetime import datetime
from typing import Dict, Any, List

from model import (
    ESTADO_NO_ENFERMO,
    ESTADO_LEVE,
    ESTADO_AGUDA,
    ESTADO_CRONICA,
    ESTADO_TERMINAL,
)


ESTADOS = [
    ESTADO_NO_ENFERMO,
    ESTADO_LEVE,
    ESTADO_AGUDA,
    ESTADO_CRONICA,
    ESTADO_TERMINAL,
]

NUM_ULTIMAS_PREDICCIONES = 5

RUTA_POR_DEFECTO = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "predicciones.jsonl"
)

# Evita que dos peticiones simultáneas escriban líneas mezcladas en el archivo.
_bloqueo_escritura = threading.Lock()


def obtener_ruta_archivo() -> str:
    """
    Retorna la ruta del archivo de predicciones. Se lee en cada llamada para
    que las pruebas puedan usar un archivo temporal.
    """
    return os.environ.get("RUTA_ESTADISTICAS", RUTA_POR_DEFECTO)


def registrar_prediccion(resultado: Dict[str, Any]) -> None:
    """
    Agrega al archivo de predicciones el estado, los parámetros y la fecha
    de una predicción realizada por el modelo.
    """
    registro = {
        "fecha": datetime.now().astimezone().isoformat(timespec="seconds"),
        "estado": resultado["estado"],
        "parametros": resultado["parametros_recibidos"],
    }
    ruta = obtener_ruta_archivo()
    os.makedirs(os.path.dirname(ruta) or ".", exist_ok=True)
    with _bloqueo_escritura:
        with open(ruta, "a", encoding="utf-8") as archivo:
            archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")


def leer_predicciones() -> List[Dict[str, Any]]:
    """
    Lee todas las predicciones registradas, en orden cronológico.
    Si el archivo aún no existe, retorna una lista vacía.
    """
    ruta = obtener_ruta_archivo()
    if not os.path.exists(ruta):
        return []
    with open(ruta, "r", encoding="utf-8") as archivo:
        return [json.loads(linea) for linea in archivo if linea.strip()]


def obtener_estadisticas() -> Dict[str, Any]:
    """
    Construye el reporte de estadísticas para los médicos. Sin predicciones,
    los conteos están en 0, la lista de últimas predicciones está vacía y la
    fecha de la última predicción es None.
    """
    predicciones = leer_predicciones()

    conteo_por_categoria = {estado: 0 for estado in ESTADOS}
    for prediccion in predicciones:
        conteo_por_categoria[prediccion["estado"]] = (
            conteo_por_categoria.get(prediccion["estado"], 0) + 1
        )

    # Las más recientes primero
    ultimas = list(reversed(predicciones[-NUM_ULTIMAS_PREDICCIONES:]))

    return {
        "total_predicciones": len(predicciones),
        "predicciones_por_categoria": conteo_por_categoria,
        "ultimas_predicciones": ultimas,
        "fecha_ultima_prediccion": predicciones[-1]["fecha"] if predicciones else None,
    }
