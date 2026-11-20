# Taller MLOps: Pipeline End-to-End y Servicio Clínico en Docker

**Asignatura:** Electiva III — MLOps Engineering (Maestría en Inteligencia Artificial Aplicada)  

**Integrantes:**
- David Valencia – davidvalenciaj@gmail.com
- Alonso Arbeláez – alonsoarbelaez@gmail.com
- Ricardo Delgado – ridel007@gmail.com

---

## 1. Finalidad del Proyecto y de la Solución

Este repositorio contiene la solución completa al taller de **Pipeline de MLOps y Contenerización con Docker** para un sistema médico de apoyo al diagnóstico clínico capaz de evaluar síntomas de pacientes tanto para **enfermedades comunes** (abundancia de datos) como para **enfermedades huérfanas** (escasez de datos):

1. **Punto 1 — Diseño del Pipeline de MLOps:** Describe el flujo *end-to-end* (Diseño, Desarrollo y Producción/Monitoreo) junto con su diagrama general de arquitectura. Se presentó en la Unidad 1 y no forma parte de este repositorio.
2. **Punto 2 — Servicio Contenerizado en Docker (`Dockerfile`, `model.py`, `app.py`):** Empaqueta un servicio web y API REST en **Python + Flask** dentro de una imagen de Docker para que cualquier médico pueda desplegar el modelo en su propio computador y obtener diagnósticos sin instalar dependencias locales.

---

## 2. Estructura del Directorio

```text
team-a-mlops-U2/
├── README.md                # Entregable Punto 2: Documentación de uso, construcción y pruebas
├── Dockerfile               # Definición de la imagen personalizada de Docker
├── requirements.txt         # Dependencias de Python (Flask)
├── requirements-dev.txt     # Dependencias de desarrollo (pytest)
├── pytest.ini               # Configuración de pytest
├── model.py                 # Función del modelo simulado (retorna los 5 estados clínicos)
├── estadisticas.py          # Registro de cada predicción y reporte de estadísticas
├── app.py                   # Servicio Flask con interfaz web (/) y endpoints API (/predecir, /estadisticas)
├── test_servicio.py         # Suite de validación automatizada de los 5 estados y endpoints
├── tests/
│   └── test_modelo.py       # Pruebas unitarias con pytest
├── templates/
│   └── index.html           # Página web interactiva para el médico
└── .github/
    └── workflows/
        └── workflow.yaml    # Pipeline de CI/CD con GitHub Actions
```

---

## 3. Descripción de la Función del Modelo (`model.py`)

La función `predecir_estado_paciente` recibe **mínimo 3 parámetros clínicos** (y un 4.º parámetro opcional de apoyo) y evalúa el cuadro del paciente para retornar exactamente alguno de los **5 estados exigidos**:

- `NO ENFERMO`
- `ENFERMEDAD LEVE`
- `ENFERMEDAD AGUDA`
- `ENFERMEDAD CRÓNICA`
- `ENFERMEDAD TERMINAL`

### Parámetros de entrada

| Parámetro | Tipo | Descripción Clínica |
| :--- | :--- | :--- |
| `temperatura` | `float` | Temperatura corporal en grados Celsius (°C). Normal: $\le 37.2^\circ\text{C}$. Fiebre alta: $\ge 38.5^\circ\text{C}$. |
| `duracion_dias` | `int` | Días de evolución de los síntomas. Cuadros $\ge 30$ días (o $\ge 14$ días con biomarcador alterado) indican cronicidad. |
| `severidad_dolor` | `int` | Escala subjetiva de dolor/malestar de `0` (sin dolor) a `10` (dolor severo $\ge 7$). |
| `biomarcador_anormal` | `int` *(opcional)* | `0` = Normal (valor por defecto), `1` = Alteración en laboratorio o signo de alarma clínica. |

**Enfermedad terminal:** se predice cuando coinciden una evolución de $\ge 60$ días, dolor muy severo ($\ge 9$) y biomarcador alterado (`1`). Esta regla se evalúa antes que la de enfermedad crónica.

---

## 4. Instrucciones Paso a Paso: Construir y Correr la Imagen de Docker

### Prerrequisitos
Tener **Docker** instalado y en ejecución en el sistema (Docker Desktop en Windows/Mac o Docker Engine en Linux).

### Paso 1: Ubicarse en el directorio del proyecto
Abrir una terminal y navegar a la carpeta donde se encuentra el `Dockerfile`:

```bash
cd team-a-mlops-U2
```

### Paso 2: Construir la imagen de Docker (`docker build`)
Ejecutar el siguiente comando para construir la imagen llamada `servicio-medico-ml`:

```bash
docker build -t servicio-medico-ml:1.0 .
```

Para verificar que la imagen fue creada correctamente:

```bash
docker images | grep servicio-medico-ml
```

### Paso 3: Ejecutar el contenedor (`docker run`)
Iniciar el contenedor mapeando el puerto `5000` de la máquina local al puerto `5000` del contenedor:

```bash
docker run -d -p 5000:5000 --name contenedor-medico servicio-medico-ml:1.0
```

*(Nota para usuarios de macOS: si el puerto `5000` está ocupado por AirPlay Receiver, puede mapearse cualquier otro puerto local, por ejemplo `-p 5050:5000`, accediendo a `http://localhost:5050`).*

Para conservar las estadísticas de predicciones aunque el contenedor se elimine, se puede montar un volumen en `/app/data`:

```bash
docker run -d -p 5000:5000 -v "$(pwd)/data:/app/data" --name contenedor-medico servicio-medico-ml:1.0
```

Para comprobar que el contenedor está corriendo:

```bash
docker ps
```

---

## 5. Cómo Obtener Respuestas del Modelo (Los 5 Estados Clínicos)

El servicio ofrece **3 formas** de uso para comodidad del médico o evaluador:

### Opción A: A través del Navegador Web (Interfaz Gráfica para el Médico)
1. Abrir en cualquier navegador web:  
   **http://localhost:5000**
2. Ingresar los valores clínicos del paciente (o pulsar cualquiera de los **5 botones de casos de prueba rápidos** incluidos en la interfaz) y hacer clic en **"Evaluar Estado del Paciente"**.

---

### Opción B: A través del Endpoint de API con `POST /predecir` (JSON)

Se pueden enviar los parámetros como un diccionario JSON o como una lista de valores:

#### 1. Obtener estado `NO ENFERMO`
```bash
curl -X POST http://localhost:5000/predecir \
  -H "Content-Type: application/json" \
  -d '{"temperatura": 36.6, "duracion_dias": 1, "severidad_dolor": 1, "biomarcador_anormal": 0}'
```
**Respuesta esperada:**
```json
{
  "estado": "NO ENFERMO",
  "justificacion": "Signos vitales dentro de rangos normales, sin dolor significativo ni alteraciones en biomarcadores.",
  "parametros_recibidos": {
    "biomarcador_anormal": 0,
    "duracion_dias": 1,
    "severidad_dolor": 1,
    "temperatura": 36.6
  }
}
```

#### 2. Obtener estado `ENFERMEDAD LEVE`
```bash
curl -X POST http://localhost:5000/predecir \
  -H "Content-Type: application/json" \
  -d '{"temperatura": 37.6, "duracion_dias": 3, "severidad_dolor": 4, "biomarcador_anormal": 0}'
```
**Respuesta esperada:** `"estado": "ENFERMEDAD LEVE"`

#### 3. Obtener estado `ENFERMEDAD AGUDA`
```bash
curl -X POST http://localhost:5000/predecir \
  -H "Content-Type: application/json" \
  -d '{"temperatura": 39.1, "duracion_dias": 4, "severidad_dolor": 8, "biomarcador_anormal": 1}'
```
**Respuesta esperada:** `"estado": "ENFERMEDAD AGUDA"`

#### 4. Obtener estado `ENFERMEDAD CRÓNICA`
```bash
curl -X POST http://localhost:5000/predecir \
  -H "Content-Type: application/json" \
  -d '{"temperatura": 37.4, "duracion_dias": 45, "severidad_dolor": 5, "biomarcador_anormal": 1}'
```
**Respuesta esperada:** `"estado": "ENFERMEDAD CRÓNICA"`

#### 5. Obtener estado `ENFERMEDAD TERMINAL`
```bash
curl -X POST http://localhost:5000/predecir \
  -H "Content-Type: application/json" \
  -d '{"temperatura": 37.0, "duracion_dias": 120, "severidad_dolor": 9, "biomarcador_anormal": 1}'
```
**Respuesta esperada:** `"estado": "ENFERMEDAD TERMINAL"`

#### Envío alternativo como lista de 3 valores:
```bash
curl -X POST http://localhost:5000/predecir \
  -H "Content-Type: application/json" \
  -d '{"valores": [39.0, 2, 8]}'
```

---

### Opción C: A través de petición `GET /predecir` (Directo en URL o navegador)

También se puede consultar directamente desde la barra de direcciones del navegador o con `curl`:

- **NO ENFERMO:**  
  `http://localhost:5000/predecir?temperatura=36.6&duracion_dias=1&severidad_dolor=1`
- **ENFERMEDAD LEVE:**  
  `http://localhost:5000/predecir?temperatura=37.6&duracion_dias=3&severidad_dolor=4`
- **ENFERMEDAD AGUDA:**  
  `http://localhost:5000/predecir?temperatura=39.1&duracion_dias=4&severidad_dolor=8`
- **ENFERMEDAD CRÓNICA:**  
  `http://localhost:5000/predecir?temperatura=37.4&duracion_dias=45&severidad_dolor=5`
- **ENFERMEDAD TERMINAL:**  
  `http://localhost:5000/predecir?temperatura=37.0&duracion_dias=120&severidad_dolor=9&biomarcador_anormal=1`

---

## 6. Reporte de Estadísticas de las Predicciones (`GET /estadisticas`)

Cada predicción realizada (desde la interfaz web o desde `/predecir`) se exporta como una línea JSON en el archivo `/app/data/predicciones.jsonl` del contenedor (configurable con la variable de entorno `RUTA_ESTADISTICAS`). Las peticiones con datos inválidos no se registran.

El reporte se obtiene en el navegador (también hay un enlace en la interfaz web) o con `curl`:

```bash
curl http://localhost:5000/estadisticas
```

**Respuesta esperada:**
```json
{
  "fecha_ultima_prediccion": "2026-11-19T20:14:38-05:00",
  "predicciones_por_categoria": {
    "ENFERMEDAD AGUDA": 1,
    "ENFERMEDAD CRÓNICA": 0,
    "ENFERMEDAD LEVE": 0,
    "ENFERMEDAD TERMINAL": 1,
    "NO ENFERMO": 0
  },
  "total_predicciones": 2,
  "ultimas_predicciones": [
    {
      "estado": "ENFERMEDAD TERMINAL",
      "fecha": "2026-11-19T20:14:38-05:00",
      "parametros": {"biomarcador_anormal": 1, "duracion_dias": 120, "severidad_dolor": 9, "temperatura": 37.0}
    },
    {
      "estado": "ENFERMEDAD AGUDA",
      "fecha": "2026-11-19T20:14:38-05:00",
      "parametros": {"biomarcador_anormal": 1, "duracion_dias": 4, "severidad_dolor": 8, "temperatura": 39.1}
    }
  ]
}
```

| Campo | Descripción |
| :--- | :--- |
| `predicciones_por_categoria` | Número total de predicciones por cada una de las 5 categorías. |
| `ultimas_predicciones` | Últimas 5 predicciones realizadas, de la más reciente a la más antigua. |
| `fecha_ultima_prediccion` | Fecha y hora de la última predicción (`null` si aún no hay predicciones). |

---

## 7. Detener y Eliminar el Contenedor

Cuando se desee finalizar el servicio:

```bash
docker stop contenedor-medico
docker rm contenedor-medico
```

---

## 8. Pruebas Unitarias

Las pruebas unitarias (`tests/test_modelo.py`) usan **pytest** y verifican que:

1. Distintos grupos de parámetros de entrada producen las **5 categorías** del modelo.
2. Antes de cualquier predicción, `GET /estadisticas` retorna los **valores por defecto** (conteos en 0, sin predicciones y sin fecha).
3. Después de una predicción, la **última predicción** de las estadísticas es la esperada.

Cada prueba usa su propio archivo de estadísticas temporal, por lo que no modifican los datos reales.

Para correrlas localmente:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -v
```

---

## 9. Pipeline de CI/CD con GitHub Actions

El pipeline está definido en `.github/workflows/workflow.yaml`. La rama `main` está protegida, por lo que los cambios solo ingresan mediante pull requests.

| Evento | Tareas |
| :--- | :--- |
| **Pull request contra `main`** | 1. Comenta en el PR: *"CI/CD en acción. Ejecutando tareas …"*.<br>2. Corre las pruebas unitarias.<br>3. Si pasan, comenta en el PR: *"CI/CD terminado con éxito."*. |
| **Commit en `main`** (merge de un PR) | 1. Vuelve a correr las pruebas unitarias.<br>2. Si pasan, construye la imagen de Docker y la publica en GitHub Packages (`ghcr.io`). |

### Usar la imagen publicada

La imagen publicada en GitHub Packages se puede descargar y ejecutar sin construirla localmente:

```bash
docker pull ghcr.io/rockcor0/team-a-mlops-u2:latest
docker run -d -p 5000:5000 --name contenedor-medico ghcr.io/rockcor0/team-a-mlops-u2:latest
```

Además de `latest`, cada imagen se etiqueta con el SHA corto del commit de `main` que la generó (por ejemplo, `sha-1a2b3c4`).
