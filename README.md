# Taller MLOps: Pipeline End-to-End y Servicio Clínico en Docker

**Asignatura:** Electiva III — MLOps Engineering (Maestría en Inteligencia Artificial Aplicada)  

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
├── model.py                 # Función del modelo simulado (retorna los 4 estados clínicos)
├── app.py                   # Servicio Flask con interfaz web (/) y endpoint API (/predecir)
├── test_servicio.py         # Suite de validación automatizada de los 4 estados y endpoints
└── templates/
    └── index.html           # Página web interactiva para el médico
```

---

## 3. Descripción de la Función del Modelo (`model.py`)

La función `predecir_estado_paciente` recibe **mínimo 3 parámetros clínicos** (y un 4.º parámetro opcional de apoyo) y evalúa el cuadro del paciente para retornar exactamente alguno de los **4 estados exigidos**:

- `NO ENFERMO`
- `ENFERMEDAD LEVE`
- `ENFERMEDAD AGUDA`
- `ENFERMEDAD CRÓNICA`

### Parámetros de entrada

| Parámetro | Tipo | Descripción Clínica |
| :--- | :--- | :--- |
| `temperatura` | `float` | Temperatura corporal en grados Celsius (°C). Normal: $\le 37.2^\circ\text{C}$. Fiebre alta: $\ge 38.5^\circ\text{C}$. |
| `duracion_dias` | `int` | Días de evolución de los síntomas. Cuadros $\ge 30$ días (o $\ge 14$ días con biomarcador alterado) indican cronicidad. |
| `severidad_dolor` | `int` | Escala subjetiva de dolor/malestar de `0` (sin dolor) a `10` (dolor severo $\ge 7$). |
| `biomarcador_anormal` | `int` *(opcional)* | `0` = Normal (valor por defecto), `1` = Alteración en laboratorio o signo de alarma clínica. |

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

Para comprobar que el contenedor está corriendo:

```bash
docker ps
```

---

## 5. Cómo Obtener Respuestas del Modelo (Los 4 Estados Clínicos)

El servicio ofrece **3 formas** de uso para comodidad del médico o evaluador:

### Opción A: A través del Navegador Web (Interfaz Gráfica para el Médico)
1. Abrir en cualquier navegador web:  
   **http://localhost:5000**
2. Ingresar los valores clínicos del paciente (o pulsar cualquiera de los **4 botones de casos de prueba rápidos** incluidos en la interfaz) y hacer clic en **"Evaluar Estado del Paciente"**.

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

---

## 6. Detener y Eliminar el Contenedor

Cuando se desee finalizar el servicio:

```bash
docker stop contenedor-medico
docker rm contenedor-medico
```
