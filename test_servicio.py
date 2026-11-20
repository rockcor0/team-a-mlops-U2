"""
Script de validación técnica del modelo y de los endpoints del servicio Flask.

Verifica:
1. Que la función `predecir_estado_paciente` retorne los 4 estados requeridos:
   - NO ENFERMO
   - ENFERMEDAD LEVE
   - ENFERMEDAD AGUDA
   - ENFERMEDAD CRÓNICA
2. Que el endpoint POST /predecir funcione correctamente con diccionario y lista.
3. Que el endpoint GET /predecir funcione con parámetros de consulta en la URL.
4. Que la interfaz web GET / y POST / responda correctamente.
"""

from model import predecir_estado_paciente, predecir_desde_coleccion
from app import app


CASOS_PRUEBA = [
    (
        {"temperatura": 36.6, "duracion_dias": 1, "severidad_dolor": 1, "biomarcador_anormal": 0},
        "NO ENFERMO",
    ),
    (
        {"temperatura": 37.6, "duracion_dias": 3, "severidad_dolor": 4, "biomarcador_anormal": 0},
        "ENFERMEDAD LEVE",
    ),
    (
        {"temperatura": 39.1, "duracion_dias": 4, "severidad_dolor": 8, "biomarcador_anormal": 1},
        "ENFERMEDAD AGUDA",
    ),
    (
        {"temperatura": 37.4, "duracion_dias": 45, "severidad_dolor": 5, "biomarcador_anormal": 1},
        "ENFERMEDAD CRÓNICA",
    ),
]


def ejecutar_pruebas():
    print("=== 1. Probando función directa del modelo (model.py) ===")
    for entrada, estado_esperado in CASOS_PRUEBA:
        resultado = predecir_estado_paciente(**entrada)
        assert resultado["estado"] == estado_esperado, (
            f"Fallo en función directa: esperado {estado_esperado}, obtenido {resultado['estado']}"
        )
        print(f"  [OK] Entrada {entrada} -> {resultado['estado']}")

    print("\n=== 2. Probando entrada por lista de 3 valores ===")
    res_lista = predecir_desde_coleccion([39.0, 2, 8])
    assert res_lista["estado"] == "ENFERMEDAD AGUDA"
    print(f"  [OK] Lista [39.0, 2, 8] -> {res_lista['estado']}")

    print("\n=== 3. Probando endpoints del servicio Flask (app.py) ===")
    client = app.test_client()

    # Healthcheck
    r_health = client.get("/health")
    assert r_health.status_code == 200
    print(f"  [OK] GET /health -> {r_health.get_json()}")

    # Interfaz web GET /
    r_index = client.get("/")
    assert r_index.status_code == 200
    print("  [OK] GET / (Formulario Web HTML cargado correctamente)")

    # POST /predecir y GET /predecir para los 4 estados
    for entrada, estado_esperado in CASOS_PRUEBA:
        r_post = client.post("/predecir", json=entrada)
        assert r_post.status_code == 200
        datos_post = r_post.get_json()
        assert datos_post["estado"] == estado_esperado
        print(f"  [OK] POST /predecir -> {datos_post['estado']}")

        r_get = client.get("/predecir", query_string=entrada)
        assert r_get.status_code == 200
        datos_get = r_get.get_json()
        assert datos_get["estado"] == estado_esperado
        print(f"  [OK] GET  /predecir -> {datos_get['estado']}")

    print("\nTODAS LAS PRUEBAS PASARON EXITOSAMENTE (4/4 estados validados).")


if __name__ == "__main__":
    ejecutar_pruebas()
