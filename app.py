"""
Servicio Web y API REST en Flask para exponer el modelo de clasificación clínica.

Puntos finales (Endpoints) disponibles:
    - GET /          : Interfaz web para que el médico ingrese los síntomas.
    - POST /         : Procesa el formulario web y muestra el estado en pantalla.
    - GET /predecir  : Permite obtener predicción mediante parámetros en la URL.
    - POST /predecir : Permite obtener predicción enviando un JSON o lista de valores.
    - GET /health    : Verifica que el contenedor Docker está activo y saludable.
"""

import os
from flask import Flask, request, jsonify, render_template
from model import predecir_estado_paciente, predecir_desde_coleccion

app = Flask(__name__)


def extraer_y_predecir(origen_datos: dict) -> dict:
    """
    Extrae los parámetros enviados por el médico (como campos individuales
    o como una lista 'valores') y ejecuta la función del modelo.
    """
    # Si el usuario envía una lista bajo la llave 'valores', ej: {"valores": [36.5, 1, 1, 0]}
    if "valores" in origen_datos and isinstance(origen_datos["valores"], list):
        return predecir_desde_coleccion(origen_datos["valores"])

    # Validación de presencia de los 3 parámetros mínimos requeridos
    campos_requeridos = ["temperatura", "duracion_dias", "severidad_dolor"]
    faltantes = [c for c in campos_requeridos if c not in origen_datos or origen_datos[c] == ""]
    if faltantes:
        raise ValueError(
            f"Faltan parámetros requeridos: {', '.join(faltantes)}. "
            "Debe enviar al menos: temperatura, duracion_dias y severidad_dolor."
        )

    return predecir_estado_paciente(
        temperatura=float(origen_datos["temperatura"]),
        duracion_dias=int(float(origen_datos["duracion_dias"])),
        severidad_dolor=int(float(origen_datos["severidad_dolor"])),
        biomarcador_anormal=int(float(origen_datos.get("biomarcador_anormal", 0))),
    )


@app.route("/", methods=["GET", "POST"])
def index():
    """
    Ruta principal con interfaz gráfica web para el médico.
    """
    resultado = None
    error = None
    valores_form = {
        "temperatura": "36.6",
        "duracion_dias": "1",
        "severidad_dolor": "1",
        "biomarcador_anormal": "0",
    }

    if request.method == "POST":
        valores_form = {
            "temperatura": request.form.get("temperatura", "36.6"),
            "duracion_dias": request.form.get("duracion_dias", "1"),
            "severidad_dolor": request.form.get("severidad_dolor", "1"),
            "biomarcador_anormal": request.form.get("biomarcador_anormal", "0"),
        }
        try:
            resultado = extraer_y_predecir(valores_form)
        except Exception as exc:
            error = str(exc)

    return render_template(
        "index.html",
        resultado=resultado,
        error=error,
        valores=valores_form,
    )


@app.route("/predecir", methods=["GET", "POST"])
def predecir():
    """
    Endpoint de API para consultar el modelo programáticamente (curl, Postman, navegador).
    Soporta tanto peticiones POST (JSON o Form) como GET (query params en la URL).
    """
    try:
        if request.method == "POST":
            datos = request.get_json(silent=True)
            if datos is None:
                datos = request.form.to_dict()
        else:
            datos = request.args.to_dict()

        if isinstance(datos, list):
            resultado = predecir_desde_coleccion(datos)
        else:
            resultado = extraer_y_predecir(datos)

        return jsonify(resultado), 200

    except (ValueError, TypeError, KeyError) as err:
        return jsonify({"error": str(err)}), 400
    except Exception as err:
        return jsonify({"error": f"Error interno procesando la solicitud: {str(err)}"}), 500


@app.route("/health", methods=["GET"])
def health():
    """
    Endpoint de verificación de estado del servicio (Healthcheck).
    """
    return jsonify({"status": "ok", "servicio": "api-diagnostico-clinico-mlops"}), 200


if __name__ == "__main__":
    # Se ejecuta en 0.0.0.0 para que sea accesible desde fuera del contenedor Docker.
    # Permite configurar el puerto mediante variable de entorno PORT (por defecto 5000).
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=puerto, debug=False)
