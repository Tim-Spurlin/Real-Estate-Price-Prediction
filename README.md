# Real Estate Predictions 🏡📊

Este repositorio contiene mi solución para la competencia de Kaggle: [House Prices - Advanced Regression Techniques](https://www.kaggle.com/c/house-prices-advanced-regression-techniques).

El objetivo principal de este proyecto es predecir con precisión el precio de venta de propiedades en Ames, Iowa, mediante la implementación de técnicas avanzadas de regresión en Machine Learning. Se utilizan un total de 79 variables explicativas (características de las casas) para construir el modelo.

## 🚀 Estructura del Proyecto

* `data/`: Contiene los archivos de datos originales provistos por Kaggle (`train.csv`, `test.csv`, `data_description.txt`).
* `src/`: Carpeta con scripts modulares en Python.
  * `depuration.py`: Funciones customizadas para la visualización y limpieza de la base de datos (e.g. histogramas, boxplots).
  * `preprocessing.py`: Modulo completo de preprocesado, imputación de nulos y feature engineering.
  * `train.py`: Script de entrenamiento que ejecuta el ensamblado (Stacking) usando Lasso, Ridge, XGBoost, LightGBM, y CatBoost.
* `01_Preprocessing.ipynb`: Jupyter notebook enfocado en la exploración inicial (EDA).
* `submission.csv`: Archivo final generado por el pipeline con las predicciones.

## 🛠️ Instalación y Requisitos

Para replicar y ejecutar el código de este proyecto de manera local, asegúrate de tener instalado Python 3.8+ y las siguientes librerías. Se recomienda usar un entorno virtual:

```bash
git clone https://github.com/sebakremis/real-estate-predictions.git
cd real-estate-predictions
python -m venv .venv
source .venv/bin/activate
pip install pandas numpy matplotlib seaborn scikit-learn xgboost lightgbm catboost
```

Para generar las predicciones finales con el Stacking Regressor, ejecuta:
```bash
PYTHONPATH=. python src/train.py
```

🧠 Metodología
Análisis Exploratorio de Datos (EDA): Visualización y descubrimiento de la distribución de SalePrice y su relación con variables clave.

Data Cleaning & Preprocessing:

Concatenación de datos de entrenamiento y test para un procesamiento uniforme.

Manejo avanzado de valores faltantes (NaNs interpretados según el dominio del problema).

Conversión inteligente de variables categóricas vs. numéricas.

Feature Engineering: Creación de métricas de dominio específicas, como AvgRoomSize, HasGarage y GarageAge.

📈 Tareas Completadas (Completed)
[x] Transformación Box-Cox / Logarítmica para características sesgadas y target.

[x] Codificación Ordinal (Ordinal Encoding) para features de calidad de los inmuebles.

[x] Entrenar y optimizar modelos Baseline (Lasso, Ridge Regression).

[x] Implementar modelos basados en árboles (XGBoost, LightGBM, CatBoost).

[x] Ensamblado de modelos (Stacking) para optimizar el Root Mean Squared Logarithmic Error (RMSLE).

🏆 Resultados
(A completar).

👨‍💻 Autor
[Sebastian Kremis] * [LinkedIn](https://www.linkedin.com/in/sebastian-kremis)
