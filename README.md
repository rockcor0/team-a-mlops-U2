# team-a-mlops-U2

Repositorio de la Unidad 2 de la asignatura **Electiva III — MLOps Engineering** (Maestría en Inteligencia Artificial Aplicada, Universidad Icesi).

## Problema

En medicina existe abundante información de pacientes para enfermedades comunes, pero para las enfermedades **huérfanas** los datos escasean. Se requiere un modelo que, a partir de los síntomas de un paciente, estime si puede sufrir alguna enfermedad, tanto común como huérfana.

## Propósito

Mantener bajo control de versiones la solución desarrollada en la Unidad 1: un servicio web en Docker que permite a un médico ingresar síntomas y obtener un estado clínico a partir de un modelo simulado. Sobre esta base se incorporan nuevos requerimientos (nueva categoría de predicción y reporte de estadísticas) mediante ramas y pull requests, y un pipeline de CI/CD con GitHub Actions que ejecuta pruebas y publica la imagen de Docker.

## Estructura del repositorio

| Rama | Contenido |
| :--- | :--- |
| `main` | Rama principal y protegida; solo recibe cambios mediante pull requests. |
| `solucion-inicial` | Archivos de la solución de la Unidad 1 (servicio Flask, modelo simulado, Dockerfile). |
| Ramas de funcionalidades | Nuevos requerimientos: categoría ENFERMEDAD TERMINAL y reporte de estadísticas. |
| `añadir-github-actions` | Workflows de CI/CD: pruebas en cada PR y publicación de la imagen de Docker en cada push a `main`. |
