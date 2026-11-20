"""
Módulo de simulación del modelo de Machine Learning para clasificación clínica.

Este módulo implementa la función requerida en el Punto 2 del taller, capaz de
recibir al menos 3 parámetros clínicos de síntomas de un paciente y retornar
alguno de los 5 estados posibles definidos en el enunciado:
    - NO ENFERMO
    - ENFERMEDAD LEVE
    - ENFERMEDAD AGUDA
    - ENFERMEDAD CRÓNICA
    - ENFERMEDAD TERMINAL
"""

from typing import Dict, Any, Union


# Estados oficiales requeridos por el enunciado
ESTADO_NO_ENFERMO = "NO ENFERMO"
ESTADO_LEVE = "ENFERMEDAD LEVE"
ESTADO_AGUDA = "ENFERMEDAD AGUDA"
ESTADO_CRONICA = "ENFERMEDAD CRÓNICA"
ESTADO_TERMINAL = "ENFERMEDAD TERMINAL"


def predecir_estado_paciente(
    temperatura: float,
    duracion_dias: int,
    severidad_dolor: int,
    biomarcador_anormal: int = 0,
) -> Dict[str, Any]:
    """
    Evalúa los síntomas del paciente y retorna el estado clínico estimado.

    Parámetros:
    -----------
    temperatura : float
        Temperatura corporal del paciente en grados Celsius (°C). Ej: 36.6
    duracion_dias : int
        Número de días que el paciente lleva presentando los síntomas. Ej: 3
    severidad_dolor : int
        Nivel de dolor o malestar general en escala de 0 a 10. Ej: 4
    biomarcador_anormal : int, opcional (por defecto 0)
        Indicador de alteración en pruebas de laboratorio o signo de alarma
        (0 = Normal / Sin alteración, 1 = Anormal / Alterado).

    Retorna:
    --------
    dict
        Diccionario con el estado clínico ('estado'), una recomendación clínica
        ('justificacion') y los parámetros evaluados ('parametros_recibidos').
    """
    temperatura = float(temperatura)
    duracion_dias = int(duracion_dias)
    severidad_dolor = int(severidad_dolor)
    biomarcador_anormal = int(biomarcador_anormal)

    # 1. Caso: NO ENFERMO
    # Temperatura normal (<= 37.2 °C), síntomas de 2 días o menos,
    # dolor mínimo (<= 2) y sin biomarcadores anormales.
    if (
        temperatura <= 37.2
        and duracion_dias <= 2
        and severidad_dolor <= 2
        and biomarcador_anormal == 0
    ):
        estado = ESTADO_NO_ENFERMO
        justificacion = (
            "Signos vitales dentro de rangos normales, sin dolor significativo "
            "ni alteraciones en biomarcadores."
        )

    # 2. Caso: ENFERMEDAD TERMINAL
    # Evolución muy prolongada (>= 60 días), dolor muy severo (>= 9) y
    # biomarcador anormal. Se evalúa antes que CRÓNICA porque también la cumple.
    elif duracion_dias >= 60 and severidad_dolor >= 9 and biomarcador_anormal == 1:
        estado = ESTADO_TERMINAL
        justificacion = (
            "Enfermedad de larga evolución con dolor muy severo y biomarcador "
            "alterado, compatible con una fase avanzada. Se sugiere valoración "
            "por cuidados paliativos y manejo especializado."
        )

    # 3. Caso: ENFERMEDAD CRÓNICA
    # Síntomas persistentes por 30 días o más, o evolución >= 14 días acompañada
    # de biomarcador anormal (patrón frecuente en enfermedades crónicas o huérfanas).
    elif duracion_dias >= 30 or (duracion_dias >= 14 and biomarcador_anormal == 1):
        estado = ESTADO_CRONICA
        justificacion = (
            "Persistencia prolongada de síntomas o evolución subaguda con "
            "biomarcador alterado. Se sugiere estudio especializado para "
            "patología crónica o enfermedad huérfana."
        )

    # 4. Caso: ENFERMEDAD AGUDA
    # Fiebre alta (>= 38.5 °C), dolor severo (>= 7) o biomarcador alterado
    # en un cuadro de aparición reciente (< 30 días).
    elif (
        temperatura >= 38.5
        or severidad_dolor >= 7
        or biomarcador_anormal == 1
    ):
        estado = ESTADO_AGUDA
        justificacion = (
            "Cuadro de instauración reciente con signos de severidad "
            "(fiebre elevada, dolor intenso o alteración aguda de laboratorio). "
            "Requiere atención médica prioritaria."
        )

    # 5. Caso: ENFERMEDAD LEVE
    # Síntomas leves o moderados de corta duración sin signos de alarma.
    else:
        estado = ESTADO_LEVE
        justificacion = (
            "Sintomatología leve a moderada de corta evolución sin signos "
            "de alarma aguda ni criterios de cronicidad."
        )

    return {
        "estado": estado,
        "justificacion": justificacion,
        "parametros_recibidos": {
            "temperatura": temperatura,
            "duracion_dias": duracion_dias,
            "severidad_dolor": severidad_dolor,
            "biomarcador_anormal": biomarcador_anormal,
        },
    }


def predecir_desde_coleccion(
    datos: Union[list, tuple, dict]
) -> Dict[str, Any]:
    """
    Función adaptadora que permite recibir los parámetros como lista, tupla
    o diccionario, garantizando flexibilidad total de entrada.
    """
    if isinstance(datos, dict):
        return predecir_estado_paciente(
            temperatura=datos["temperatura"],
            duracion_dias=datos["duracion_dias"],
            severidad_dolor=datos["severidad_dolor"],
            biomarcador_anormal=datos.get("biomarcador_anormal", 0),
        )
    elif isinstance(datos, (list, tuple)):
        if len(datos) < 3:
            raise ValueError(
                "Se requieren al menos 3 valores: [temperatura, duracion_dias, severidad_dolor]"
            )
        biomarcador = datos[3] if len(datos) >= 4 else 0
        return predecir_estado_paciente(
            temperatura=datos[0],
            duracion_dias=datos[1],
            severidad_dolor=datos[2],
            biomarcador_anormal=biomarcador,
        )
    else:
        raise TypeError("El formato de entrada debe ser diccionario, lista o tupla.")
