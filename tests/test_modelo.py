"""
Pruebas unitarias del modelo simulado y del reporte de estadísticas.

Cada prueba usa su propio archivo de estadísticas temporal, de modo que las
predicciones de una prueba no afectan a las demás.
"""

import pytest

from app import app
from model import predecir_estado_paciente


@pytest.fixture
def cliente(tmp_path, monkeypatch):
    """Cliente de pruebas de Flask con un archivo de estadísticas vacío."""
    monkeypatch.setenv("RUTA_ESTADISTICAS", str(tmp_path / "predicciones.jsonl"))
    return app.test_client()


@pytest.mark.parametrize(
    "entrada, estado_esperado",
    [
        ({"temperatura": 36.6, "duracion_dias": 1, "severidad_dolor": 1, "biomarcador_anormal": 0}, "NO ENFERMO"),
        ({"temperatura": 37.6, "duracion_dias": 3, "severidad_dolor": 4, "biomarcador_anormal": 0}, "ENFERMEDAD LEVE"),
        ({"temperatura": 39.1, "duracion_dias": 4, "severidad_dolor": 8, "biomarcador_anormal": 1}, "ENFERMEDAD AGUDA"),
        ({"temperatura": 37.4, "duracion_dias": 45, "severidad_dolor": 5, "biomarcador_anormal": 1}, "ENFERMEDAD CRÓNICA"),
        ({"temperatura": 37.0, "duracion_dias": 120, "severidad_dolor": 9, "biomarcador_anormal": 1}, "ENFERMEDAD TERMINAL"),
    ],
)
def test_modelo_retorna_las_5_categorias(entrada, estado_esperado):
    """Distintos grupos de parámetros producen cada una de las 5 categorías."""
    assert predecir_estado_paciente(**entrada)["estado"] == estado_esperado


def test_estadisticas_vacias_antes_de_predecir(cliente):
    """Antes de cualquier predicción, las estadísticas tienen sus valores por defecto."""
    respuesta = cliente.get("/estadisticas")
    assert respuesta.status_code == 200

    estadisticas = respuesta.get_json()
    assert estadisticas["total_predicciones"] == 0
    assert estadisticas["predicciones_por_categoria"] == {
        "NO ENFERMO": 0,
        "ENFERMEDAD LEVE": 0,
        "ENFERMEDAD AGUDA": 0,
        "ENFERMEDAD CRÓNICA": 0,
        "ENFERMEDAD TERMINAL": 0,
    }
    assert estadisticas["ultimas_predicciones"] == []
    assert estadisticas["fecha_ultima_prediccion"] is None


def test_ultima_prediccion_en_estadisticas(cliente):
    """Después de predecir, la última predicción de las estadísticas es la esperada."""
    entrada = {"temperatura": 37.0, "duracion_dias": 120, "severidad_dolor": 9, "biomarcador_anormal": 1}
    respuesta = cliente.post("/predecir", json=entrada)
    assert respuesta.status_code == 200
    assert respuesta.get_json()["estado"] == "ENFERMEDAD TERMINAL"

    estadisticas = cliente.get("/estadisticas").get_json()
    ultima = estadisticas["ultimas_predicciones"][0]
    assert ultima["estado"] == "ENFERMEDAD TERMINAL"
    assert ultima["parametros"] == entrada
    assert estadisticas["predicciones_por_categoria"]["ENFERMEDAD TERMINAL"] == 1
    assert estadisticas["fecha_ultima_prediccion"] == ultima["fecha"]
