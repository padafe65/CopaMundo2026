import os
import pandas as pd
from sqlalchemy import create_engine, text  # Importamos 'text' de sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
import pymysql

# Configuración de la BD (XAMPP)
USER = 'root'
PASSWORD = ''
HOST = 'localhost'
PORT = '3306'
DATABASE = 'copaMundo'
connection_string = f'mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'

try:
    engine = create_engine(connection_string)
    connection = engine.connect()
    print("Conexión exitosa a la base de datos.")
except SQLAlchemyError as e:
    print(f"Error al conectar a la base de datos: {e}")
    exit()

# -------------------------------------------------------------------
# AGREGAR AQUÍ: Limpiar datos previos antes de volver a cargar
# -------------------------------------------------------------------
try:
    with engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        conn.execute(text("TRUNCATE TABLE goals;"))
        conn.execute(text("TRUNCATE TABLE players;"))
        conn.execute(text("TRUNCATE TABLE tournaments;"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        print("Tablas limpiadas correctamente antes de la migración.")
except SQLAlchemyError as e:
    print(f"Error al vaciar las tablas: {e}")
# -------------------------------------------------------------------

# Definir archivos en orden correcto
csv_files = {
    'tournaments': '../datasets/tournaments.csv',
    'players': '../datasets/players.csv',
    'goals': '../datasets/goals.csv'
}

print("Iniciando el proceso de migración de datos...")

for table_name, file_path in csv_files.items():
    if os.path.exists(file_path):
        print(f"Cargando archivo {file_path} en la tabla {table_name}...")
        df = pd.read_csv(file_path)
        
        # Conversión de fechas a formato MySQL (YYYY-MM-DD)
        if table_name == 'tournaments':
            df['start_date'] = pd.to_datetime(df['start_date'], errors='coerce').dt.strftime('%Y-%m-%d')
            df['end_date'] = pd.to_datetime(df['end_date'], errors='coerce').dt.strftime('%Y-%m-%d')
        elif table_name == 'players':
            df['birth_date'] = pd.to_datetime(df['birth_date'], errors='coerce').dt.strftime('%Y-%m-%d')
        elif table_name == 'goals':
            df['match_date'] = pd.to_datetime(df['match_date'], errors='coerce').dt.strftime('%Y-%m-%d')
            
        try:
            df.to_sql(name=table_name, con=engine, if_exists='append', index=False)
            print(f"Archivo {file_path} cargado correctamente en la tabla {table_name}.")
        except SQLAlchemyError as e:
            print(f"Error al cargar el archivo {file_path} en la tabla {table_name}: {e}")
        except Exception as e:
            print(f"Error inesperado al cargar {file_path}: {e}")
    else:
        print(f"Archivo {file_path} no encontrado. Verifica la ruta.")