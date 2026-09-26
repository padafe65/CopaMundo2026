# CopaMundo2026

Markdown

# Proyecto Final - Avance 1: Base de Datos de Mundiales de Fútbol

    Curso: Data Science - Universidad Distrital (ACM UD)
    Integrante: Erwin Alirio Ferreira Rojas

1. Descripción del Proyecto
   Diseño, normalización e implementación de una base de datos relacional robusta en MariaDB/MySQL sobre los datos históricos de las Copas Mundiales de la FIFA (masculinas y femeninas).

El proyecto integra un pipeline automatizado de Extracción, Transformación y Carga (ETL) en Python que procesa los archivos CSV originales, deriva entidades normalizadas no presentes en las fuentes crudas, y puebla 15 tablas respetando la integridad referencial. Además, incluye un dashboard interactivo en Streamlit para el análisis de ventaja de localía y dinámica temporal de goles.

2. Tecnologías Utilizadas

   2.1. Lenguaje: Python 3.x

   2.2. Manipulación y Análisis: Pandas, NumPy

   2.3. Gestión de Base de Datos y ORM: SQLAlchemy, PyMySQL, MariaDB / MySQL (XAMPP)

   2.4. Visualización y Dashboard: Streamlit, Plotly Express

   2.5. Control de versiones: Git y GitHub

3. Modelo de Datos y Entidades
   La base de datos contiene las 15 tablas requeridas debidamente relacionadas mediante claves primarias (PK) y claves foráneas (FK):

3.1. Geografía y Organizaciones: region, confederation, country, federation, city

3.2 Competición: tournament, stadium, team, position

3.3 Participación y Partidos: player, matches, player_appearance

3.4 Rendimiento y Premios: goal, award, award_winner

4. Instrucciones para la Base de Datos: copamundo

4.1 Creación de la Base de Datos

4.2 Iniciar los módulos de Apache y MySQL en el panel de control de XAMPP.

4.3 Acceder a phpMyAdmin (http://localhost/phpmyadmin) o a la consola SQL y crear la base de datos:

SQL
CREATE DATABASE copaMundo CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
Restauración mediante script SQL consolidado
Importar directamente el archivo copamundo.sql desde la pestaña Importar de phpMyAdmin seleccionando la base de datos copaMundo.

5. Instrucciones para Ejecutar los Scripts de Carga (ETL)
   El archivo python/Primer_avance/connection.py contiene tanto la fábrica de conexiones como el script ejecutable de migración e ingesta masiva:

Instalar las dependencias del entorno:

Bash
pip install pandas sqlalchemy pymysql streamlit plotly
Configuración de parámetros:
Verificar las credenciales en connection.py (por defecto root, sin contraseña, puerto 3306 y base de datos copaMundo).

Ejecutar el proceso ETL:
Ubicarse en la carpeta python/Primer_avance/ y correr:

Bash
python connection.py
El script ejecutará automáticamente:

Desactivación controlada de FOREIGN_KEY_CHECKS.

Truncado y limpieza de las 15 tablas en orden inverso de dependencia.

Generación y carga derivada de region, country, city, federation y position.

Ingesta por bloques desde la carpeta ../datasets/ (confederations.csv, stadiums.csv, awards.csv, teams.csv, tournaments.csv, players.csv, matches.csv, goals.csv, award_winners.csv, etc.).

Reactivación de integridad referencial e impresión de confirmación por cada tabla cargada.

6. Instrucciones para Ejecutar la Aplicación Web (Streamlit)
   Para abrir la interfaz interactiva con los análisis exploratorios, gráficos comparativos de localía y series temporales de goles:

Ubicarse en el directorio del proyecto y ejecutar:

Bash
streamlit run python/Primer_avance/app.py (o entrar a la carpeta que dice python y desde alli ejecutar: streamlit run app.py )
La aplicación abrirá automáticamente el panel en el navegador en http://localhost:8501.
