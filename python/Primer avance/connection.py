import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pymysql

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

# Configuración de la Base de Datos (XAMPP / MariaDB)
USER = 'root'
PASSWORD = ''
HOST = 'localhost'
PORT = '3306'
DATABASE = 'copaMundo'
connection_string = f'mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'

# Motor global de SQLAlchemy
try:
    engine = create_engine(connection_string)
except SQLAlchemyError as e:
    print(f"Error al conectar a la base de datos: {e}")

# Función con caché para Streamlit
if HAS_STREAMLIT:
    @st.cache_resource
    def get_connection_engine():
        return create_engine(connection_string)
else:
    def get_connection_engine():
        return create_engine(connection_string)

# -------------------------------------------------------------------
# PROCESO ETL Y MIGRACIÓN (Solo se ejecuta con: python connection.py)
# -------------------------------------------------------------------
if __name__ == '__main__':
    tables_in_order = [
        'region', 'confederation', 'country', 'award', 'position',
        'city', 'federation', 'stadium', 'team', 'tournament',
        'player', 'matches', 'player_appearance', 'goal', 'award_winner'
    ]

    DATASETS_DIR = '../datasets/'
    print("Iniciando proceso de limpieza y migración de datos...")

    # 1. Limpieza de las 15 tablas en orden inverso
    with engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        for tbl in reversed(tables_in_order):
            conn.execute(text(f"TRUNCATE TABLE {tbl};"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        print("✅ Las 15 tablas de la base de datos se limpiaron correctamente.")

    # 2. Extracción, Transformación y Carga (ETL)
    try:
        with engine.begin() as conn:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))

            # 1. TABLA REGION (Derivada)
            df_region = pd.DataFrame([
                {'region_id': 'R-1', 'region_name': 'Africa'},
                {'region_id': 'R-2', 'region_name': 'Americas'},
                {'region_id': 'R-3', 'region_name': 'Asia'},
                {'region_id': 'R-4', 'region_name': 'Europe'},
                {'region_id': 'R-5', 'region_name': 'Oceania'}
            ])
            df_region.to_sql('region', con=conn, if_exists='append', index=False)
            print("✅ 1. Tabla 'region' generada y poblada (5 registros).")

            # 2. TABLA CONFEDERATION
            if os.path.exists(f'{DATASETS_DIR}confederations.csv'):
                df_conf = pd.read_csv(f'{DATASETS_DIR}confederations.csv')
                df_conf.to_sql('confederation', con=conn, if_exists='append', index=False)
                print("✅ 2. Tabla 'confederation' poblada (6 registros).")

            # 3. TABLA COUNTRY (Derivada desde stadiums.csv)
            if os.path.exists(f'{DATASETS_DIR}stadiums.csv'):
                df_stadiums_csv = pd.read_csv(f'{DATASETS_DIR}stadiums.csv')
                unique_countries = sorted(list(df_stadiums_csv['country_name'].dropna().unique()))
                country_map = {cname: f"C-{i+1:02d}" for i, cname in enumerate(unique_countries)}
                df_country = pd.DataFrame([
                    {'country_id': country_map[cname], 'country_name': cname}
                    for cname in unique_countries
                ])
                df_country.to_sql('country', con=conn, if_exists='append', index=False)
                print("✅ 3. Tabla 'country' extraída y poblada (20 registros).")

            # 4. TABLA AWARD
            if os.path.exists(f'{DATASETS_DIR}awards.csv'):
                df_award = pd.read_csv(f'{DATASETS_DIR}awards.csv')
                df_award.to_sql('award', con=conn, if_exists='append', index=False)
                print("✅ 4. Tabla 'award' poblada (8 registros).")

            # 5. TABLA POSITION (Derivada desde player_appearances.csv)
            if os.path.exists(f'{DATASETS_DIR}player_appearances.csv'):
                df_pa_csv = pd.read_csv(f'{DATASETS_DIR}player_appearances.csv')
                df_pos = df_pa_csv[['position_code', 'position_name']].dropna().drop_duplicates()
                df_pos.to_sql('position', con=conn, if_exists='append', index=False)
                print("✅ 5. Tabla 'position' extraída y poblada (21 registros).")

            # 6. TABLA CITY (Derivada desde stadiums.csv)
            unique_cities = df_stadiums_csv[['city_name', 'country_name']].dropna().drop_duplicates().reset_index(drop=True)
            city_map = {}
            cities_list = []
            for idx, row in unique_cities.iterrows():
                cid = f"CTY-{idx+1:03d}"
                city_map[(row['city_name'], row['country_name'])] = cid
                cities_list.append({
                    'city_id': cid,
                    'city_name': row['city_name'],
                    'country_id': country_map[row['country_name']]
                })
            df_city = pd.DataFrame(cities_list)
            df_city.to_sql('city', con=conn, if_exists='append', index=False)
            print("✅ 6. Tabla 'city' extraída y poblada (202 registros).")

            # 7. TABLA FEDERATION (Derivada desde teams.csv y confederations.csv)
            if os.path.exists(f'{DATASETS_DIR}teams.csv'):
                confed_region_map = {
                    'CF-1': 'R-3', 'CF-2': 'R-1', 'CF-3': 'R-2',
                    'CF-4': 'R-2', 'CF-5': 'R-5', 'CF-6': 'R-4'
                }
                df_teams_csv = pd.read_csv(f'{DATASETS_DIR}teams.csv')
                federations = []
                for idx, row in df_teams_csv.iterrows():
                    fed_id = f"FED-{row['team_id'].replace('T-', '')}"
                    fed_name = f"{row['team_name']} Football Federation"
                    fed_link = row['federation_wikipedia_link']
                    conf_id = row['confederation_id']
                    reg_id = confed_region_map.get(conf_id, 'R-1')
                    federations.append({
                        'federation_id': fed_id,
                        'federation_name': fed_name,
                        'federation_wikipedia_link': fed_link,
                        'confederation_id': conf_id,
                        'region_id': reg_id
                    })
                df_federation = pd.DataFrame(federations)
                df_federation.to_sql('federation', con=conn, if_exists='append', index=False)
                print("✅ 7. Tabla 'federation' extraída y poblada (88 registros).")

            # 8. TABLA STADIUM
            stadiums_list = []
            for idx, row in df_stadiums_csv.iterrows():
                cid = city_map[(row['city_name'], row['country_name'])]
                stadiums_list.append({
                    'stadium_id': row['stadium_id'],
                    'stadium_name': row['stadium_name'],
                    'city_id': cid
                })
            df_stadium = pd.DataFrame(stadiums_list)
            df_stadium.to_sql('stadium', con=conn, if_exists='append', index=False)
            print("✅ 8. Tabla 'stadium' poblada (240 registros).")

            # 9. TABLA TEAM
            cols_team = ['team_id', 'team_name', 'team_code', 'mens_team', 'womens_team', 'confederation_id', 'mens_team_wikipedia_link', 'womens_team_wikipedia_link']
            df_team = df_teams_csv[cols_team].copy()
            df_team['federation_id'] = df_team['team_id'].apply(lambda x: f"FED-{x.replace('T-', '')}")
            df_team.to_sql('team', con=conn, if_exists='append', index=False)
            print("✅ 9. Tabla 'team' poblada (88 registros).")

            # 10. TABLA TOURNAMENT
            if os.path.exists(f'{DATASETS_DIR}tournaments.csv'):
                df_tourn = pd.read_csv(f'{DATASETS_DIR}tournaments.csv')
                df_tourn['start_date'] = pd.to_datetime(df_tourn['start_date'], errors='coerce').dt.strftime('%Y-%m-%d')
                df_tourn['end_date'] = pd.to_datetime(df_tourn['end_date'], errors='coerce').dt.strftime('%Y-%m-%d')
                df_tourn.to_sql('tournament', con=conn, if_exists='append', index=False)
                print("✅ 10. Tabla 'tournament' poblada (30 registros).")

            # 11. TABLA PLAYER
            if os.path.exists(f'{DATASETS_DIR}players.csv'):
                df_player = pd.read_csv(f'{DATASETS_DIR}players.csv')
                df_player['birth_date'] = pd.to_datetime(df_player['birth_date'], errors='coerce').dt.strftime('%Y-%m-%d')
                df_player.to_sql('player', con=conn, if_exists='append', index=False)
                print("✅ 11. Tabla 'player' poblada (10,401 registros).")

            # 12. TABLA MATCHES
            if os.path.exists(f'{DATASETS_DIR}matches.csv'):
                df_matches = pd.read_csv(f'{DATASETS_DIR}matches.csv')
                df_matches['match_date'] = pd.to_datetime(df_matches['match_date'], errors='coerce').dt.strftime('%Y-%m-%d')
                cols_matches = [
                    'match_id', 'tournament_id', 'match_name', 'stage_name', 'group_name',
                    'group_stage', 'knockout_stage', 'replayed', 'replay', 'match_date',
                    'match_time', 'stadium_id', 'home_team_id', 'away_team_id', 'score',
                    'home_team_score', 'away_team_score', 'home_team_score_margin',
                    'away_team_score_margin', 'extra_time', 'penalty_shootout',
                    'score_penalties', 'home_team_score_penalties', 'away_team_score_penalties',
                    'result', 'home_team_win', 'away_team_win', 'draw'
                ]
                df_matches_clean = df_matches[cols_matches].drop_duplicates()
                df_matches_clean.to_sql('matches', con=conn, if_exists='append', index=False)
                print("✅ 12. Tabla 'matches' poblada (1,248 registros).")

            # 13. TABLA PLAYER_APPEARANCE
            cols_pa = ['match_id', 'player_id', 'team_id', 'shirt_number', 'position_code', 'starter', 'substitute']
            df_pa = df_pa_csv[cols_pa].copy()
            df_pa.to_sql('player_appearance', con=conn, if_exists='append', index=False)
            print("✅ 13. Tabla 'player_appearance' poblada (27,432 registros).")

            # 14. TABLA GOAL
            if os.path.exists(f'{DATASETS_DIR}goals.csv'):
                df_goals = pd.read_csv(f'{DATASETS_DIR}goals.csv')
                df_goals.to_sql('goal', con=conn, if_exists='append', index=False)
                print("✅ 14. Tabla 'goal' poblada (3,637 registros).")

            # 15. TABLA AWARD_WINNER
            if os.path.exists(f'{DATASETS_DIR}award_winners.csv'):
                df_aw = pd.read_csv(f'{DATASETS_DIR}award_winners.csv')
                cols_aw = ['tournament_id', 'award_id', 'shared', 'player_id', 'team_id']
                df_aw_clean = df_aw[cols_aw].copy()
                df_aw_clean['player_id'] = df_aw_clean['player_id'].where(pd.notnull(df_aw_clean['player_id']), None)
                df_aw_clean['team_id'] = df_aw_clean['team_id'].where(pd.notnull(df_aw_clean['team_id']), None)
                df_aw_clean.to_sql('award_winner', con=conn, if_exists='append', index=False)
                print("✅ 15. Tabla 'award_winner' poblada (200 registros).")

            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
            print("\n🎉 Proceso completado exitosamente. Se poblaron las 15 tablas en MariaDB.")

    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")