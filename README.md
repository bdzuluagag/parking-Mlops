# 🅿️ Predicción de Ocupación de Parqueaderos con GCP y Vertex AI

**Autores:**

* Brayan David Zuluaga Giraldo — [bdzuluagag@eafit.edu.co](mailto:bdzuluagag@eafit.edu.co)
* Sofía Mendieta Marín — [smendietam@eafit.edu.co](mailto:smendietam@eafit.edu.co)

**Curso:** ST1630 - Reto 4 / Proyecto Final
**Institución:** Universidad EAFIT
**Año:** 2025

## 📘 Descripción del Caso

### 🎯 Caso de negocio

El crecimiento del parque automotor en las principales ciudades de Colombia ha incrementado la demanda por soluciones inteligentes de movilidad.
Uno de los retos más comunes en entornos urbanos es la **baja disponibilidad y localización ineficiente de espacios de parqueo**, lo que genera congestión y pérdidas económicas.

El presente proyecto busca **predecir la ocupación futura de parqueaderos urbanos en Colombia** utilizando un flujo de datos en tiempo real y técnicas de aprendizaje automático.

La **pregunta analítica principal** es:

> “¿Podemos anticipar cuántos cupos libres tendrá un parqueadero en los próximos minutos basándonos en su comportamiento reciente?”

El modelo desarrollado permite estimar, con base en los datos históricos de disponibilidad, **la cantidad de espacios disponibles dentro de los próximos 10 intervalos de tiempo**, apoyando así la toma de decisiones en la gestión de movilidad urbana.

---

### 💻 Caso tecnológico

El caso aborda un reto de **Big Data y MLOps**, centrado en la integración de fuentes de datos en streaming, su procesamiento en la nube y el despliegue de un modelo de Machine Learning en un entorno gestionado.

El pipeline propuesto combina servicios de **Google Cloud Platform (GCP)** para construir una solución escalable, automatizada y analítica, que permite:

* Ingestar datos de disponibilidad de parqueaderos en **tiempo real**.
* Procesarlos mediante un **pipeline de streaming con Dataflow (Apache Beam)**.
* Almacenarlos y transformarlos en **BigQuery**.
* Entrenar y desplegar un **modelo predictivo** con **Vertex AI (AutoML Tabular)**.
* Visualizar los resultados.

---

## 🔬 Metodología Analítica — CRISP-DM

El proyecto sigue la metodología **CRISP-DM (Cross Industry Standard Process for Data Mining)**, que estructura el ciclo de vida analítico en seis fases:

| Etapa                           | Descripción                                                                                                                                                                                                                      |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1. Comprensión del negocio**  | El objetivo es anticipar la ocupación de parqueaderos para optimizar la gestión del tráfico y el aprovechamiento de la infraestructura en zonas urbanas de Colombia.                                                             |
| **2. Comprensión de los datos** | Los datos simulados representan sensores IoT que envían, cada 5 segundos, información de disponibilidad (`timestamp`, `parking_id`, `available_spots`). Se transmiten en tiempo real a través de Pub/Sub.                        |
| **3. Preparación de los datos** | Los datos son procesados con Dataflow y almacenados en BigQuery. Se construyeron variables derivadas (`lag_1`, `ma_5`, `target_t_plus_10`) mediante funciones de ventana SQL. Se eliminan valores nulos antes del entrenamiento. |
| **4. Modelado**                 | Se usó Vertex AI AutoML Tabular con modelo de regresión supervisada. Variables de entrada: `current_value`, `lag_1`, `ma_5`, `parking_id`. Variable objetivo: `target_t_plus_10`.                                                |
| **5. Evaluación**               | Vertex AI generó métricas de desempeño (RMSE, MAE, R²). El modelo predice con una precisión adecuada la disponibilidad futura.                                                                                                   |
| **6. Despliegue**               | El modelo fue desplegado en Vertex AI Endpoint para realizar predicciones en tiempo real mediante peticiones REST. Los resultados se visualizan en BigQuery Console.                                                             |

---

## ☁️ Arquitectura de la Solución (GCP)

| Etapa                       | Servicio GCP                         | Función                                                                                                    |
| --------------------------- | ------------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| **Ingesta (streaming)**     | **Pub/Sub**                          | Recibe datos de disponibilidad de parqueaderos en tiempo real (mensajes JSON simulados con `producer.py`). |
| **Procesamiento**           | **Dataflow (Apache Beam)**           | Limpia, transforma y carga los datos desde Pub/Sub hacia BigQuery.                                         |
| **Almacenamiento**          | **BigQuery**                         | Almacena los datos crudos (`raw_parking`) y las tablas derivadas (`training_data_clean`).                  |
| **Entrenamiento ML**        | **Vertex AI AutoML Tabular**         | Entrena el modelo de predicción de ocupación de parqueaderos.                                              |
| **Evaluación / Predicción** | **Vertex AI Endpoint**               | Permite realizar predicciones de disponibilidad futura vía API.                                            |
| **Visualización**           | **BigQuery Console** | Permite consultas analíticas y visualización de resultados.                                                |

### 🔧 Diagrama general

```
[Producer.py] 
     ↓ 
[Pub/Sub Topic: parking-raw]
     ↓ 
[Dataflow Job → BigQuery.raw_parking]
     ↓ 
[BigQuery.training_data_clean]
     ↓ 
[Vertex AI: Entrenamiento y despliegue de modelo]
     ↓ 
[Predicciones y visualización]
```

---

## ⚙️ Implementación Técnica

### a) Ingesta de datos (streaming)

* Simulación mediante `producer.py`, que genera mensajes JSON cada 5 segundos.
* Publicación en Pub/Sub (`parking-raw`).

### b) Procesamiento (Dataflow)

* `dataflow_pipeline.py` usa Apache Beam para leer desde Pub/Sub y escribir en BigQuery.
* Streaming habilitado en modo `DataflowRunner`.

### c) Almacenamiento y preparación

* **BigQuery Dataset:** `parking_dataset`

  * `raw_parking`: datos crudos.
  * `training_data`: features y target generados con SQL.
  * `training_data_clean`: datos finales sin nulos.

Ejemplo de funciones SQL usadas:

```sql
LAG(available_spots, 1) OVER (PARTITION BY parking_id ORDER BY timestamp)
AVG(available_spots) OVER (PARTITION BY parking_id ORDER BY timestamp ROWS BETWEEN 4 PRECEDING AND CURRENT ROW)
LEAD(available_spots, 10) OVER (PARTITION BY parking_id ORDER BY timestamp)
```

### d) Entrenamiento (Vertex AI)

* **Tipo:** AutoML Tabular
* **Modelo:** Regresión
* **Target:** `target_t_plus_10`
* **Features:** `current_value`, `lag_1`, `ma_5`, `parking_id`

---

### ⚙️ 2. Métricas de rendimiento obtenidas

| Métrica | Valor | Interpretación |
|----------|--------|----------------|
| **MAE (Mean Absolute Error)** | 2.395 | En promedio, el modelo se equivoca en ±2,4 cupos disponibles. |
| **MAPE (Mean Absolute Percentage Error)** | 2.666 | El error relativo promedio es del 2,6%. |
| **R² (Coeficiente de determinación)** | 0.962 | El modelo explica el 96,2% de la variabilidad total de los datos. |
| **RMSE (Root Mean Squared Error)** | 2.967 | Error cuadrático medio; penaliza más los errores grandes. |
| **RMSLE (Root Mean Squared Log Error)** | 0.032 | Error logarítmico bajo; indica buena estabilidad. |

---

### 🧩 3. Interpretación académica

Los resultados demuestran una **alta capacidad predictiva (R² ≈ 0.96)** y un **error promedio bajo (MAE ≈ 2.4)**, lo que hace del modelo una herramienta confiable para estimar la ocupación futura de parqueaderos.

> En términos prácticos, si un parqueadero tiene 100 cupos, el modelo predice con una desviación media de ±2 a 3 cupos respecto al valor real.

Esto valida la eficacia de la arquitectura implementada (Pub/Sub + Dataflow + BigQuery + Vertex AI) para flujos de datos en tiempo real y predicciones automatizadas sin intervención humana directa.

---

### e) Despliegue y visualización

* Modelo desplegado en Vertex AI Endpoint.
* Consultas y reportes ejecutados directamente desde **BigQuery Console**.

---
---

## 🚀 Reproducción del Proyecto

### 1️⃣ Crear topic y suscripción

```bash
gcloud pubsub topics create parking-raw
gcloud pubsub subscriptions create parking-raw-sub --topic=parking-raw
```

### 2️⃣ Ejecutar productor

```bash
python3 producer.py
```

### 3️⃣ Ejecutar pipeline Dataflow

```bash
python3 dataflow_pipeline.py \
  --project=pure-heuristic-471315-i8 \
  --input_topic=projects/pure-heuristic-471315-i8/topics/parking-raw \
  --dataset_table=pure-heuristic-471315-i8:parking_dataset.raw_parking \
  --temp_location=gs://pure-heuristic-471315-i8-raw-data/temp \
  --region=us-central1 \
  --runner=DataflowRunner
```

### 4️⃣ Crear tablas derivadas en BigQuery

Ejecutar los SQL ubicados en la carpeta `sql/`.

### 5️⃣ Entrenar el modelo en Vertex AI

1. Crear dataset tabular desde BigQuery.
2. Definir `target_t_plus_10` como variable objetivo.
3. Entrenar con AutoML (regresión).

---

## 🧭 Conclusiones

* Se logró implementar un **pipeline completo de MLOps en GCP**, desde la ingesta hasta el despliegue del modelo.
* Los resultados muestran la **viabilidad de predecir la disponibilidad futura de parqueaderos** con datos en tiempo real.
* El uso de **servicios serverless (Pub/Sub, Dataflow, BigQuery, Vertex AI)** simplifica la infraestructura y permite escalar fácilmente.
* Este enfoque puede adaptarse a otros contextos urbanos en Colombia (tránsito, transporte público, estaciones de bicicletas, etc.).

---

## 👥 Autores

| Nombre                           | Correo                                                    |
| -------------------------------- | --------------------------------------------------------- |
| **Brayan David Zuluaga Giraldo** | [bdzuluagag@eafit.edu.co](mailto:bdzuluagag@eafit.edu.co) |
| **Sofía Mendieta Marín**         | [smendietam@eafit.edu.co](mailto:smendietam@eafit.edu.co) |

---

## 🧩 Licencia

Proyecto académico — Universidad EAFIT (2025).
Uso educativo y demostrativo.
---

### 🤝 Declaración de trabajo colaborativo

Ambos integrantes del equipo, **Brayan David Zuluaga Giraldo** y **Sofía Mendieta Marín**, participaron de manera conjunta, equitativa y activa en **todas las etapas del desarrollo del proyecto**, incluyendo el diseño arquitectónico, la implementación técnica, la documentación y la validación del modelo en Vertex AI.  
El trabajo fue realizado en su totalidad de forma colaborativa y mutua, garantizando la comprensión y aporte de ambos miembros en cada componente del proyecto.

---
