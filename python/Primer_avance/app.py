import streamlit as st
import pandas as pd
from connection import get_connection_engine
from ui_cards import inject_card_css, render_flip_card
import plotly.express as px

st.set_page_config(page_title="Copa del Mundo", page_icon="⚽", layout="wide") 
st.title("Copa del Mundo - Análisis de Datos")
st.markdown(
    "Bienvenido a la aplicación de análisis de datos de la Copa del Mundo. "
    "Explora los torneos, partidos, selecciones y goleadores históricos."
)

try:
    engine = get_connection_engine()
except Exception as e:
    st.error(f"Error al conectar a la base de datos: {e}")
    st.stop()

# Menú lateral
sidebar_menu = st.sidebar.selectbox(
    "Selecciona un enfoque de negocio",
    ["Inicio", "Análisis del fenómeno de localía", "Dinámica temporal de goles", "Rendimiento de los equipos"]
)

# Sección: Análisis del fenómeno de localía
if sidebar_menu == "Análisis del fenómeno de localía":
    st.header("🏟️ Rendimiento del anfitrión y ventaja de localía")
    
    # Inyectar estilos CSS centralizados
    inject_card_css()

    query = """
        SELECT 
            t.tournament_name,
            m.match_date,
            tehome.team_name AS home_team,
            teaway.team_name AS away_team,
            m.home_team_score,
            m.away_team_score,
            m.result
        FROM matches m
        JOIN tournament t ON m.tournament_id = t.tournament_id
        JOIN team tehome ON m.home_team_id = tehome.team_id
        JOIN team teaway ON m.away_team_id = teaway.team_id
        LIMIT 50;
    """

    query_localia = """
        SELECT
            SUM(m.home_team_win) as "Ganados de local",
            SUM(m.away_team_win) as "Ganados de Visitante",
            SUM(m.draw) as "Empatados",
            SUM(m.home_team_win) + SUM(m.away_team_win) + SUM(m.draw) as "Total de partidos" 
        FROM `matches` m;
    """
    
    query_datos_local = """
        WITH estadisticas_local AS (
            SELECT 
                m.home_team_id,
                COALESCE(SUM(m.home_team_win), 0) AS ganados_local,
                COALESCE(SUM(m.draw), 0) AS empatados_local,
                COALESCE(SUM(m.away_team_win), 0) AS perdidos_local
            FROM `matches` m
            GROUP BY m.home_team_id
        )
        SELECT 
            t.team_name AS equipo,
            e.ganados_local AS total_partidos,
            'Más partidos GANADOS como local' AS metrica
        FROM estadisticas_local e
        JOIN `team` t ON e.home_team_id = t.team_id
        WHERE e.ganados_local = (SELECT MAX(ganados_local) FROM estadisticas_local)

        UNION ALL

        SELECT 
            t.team_name AS equipo,
            e.empatados_local AS total_partidos,
            'Más partidos EMPATADOS como local' AS metrica
        FROM estadisticas_local e
        JOIN `team` t ON e.home_team_id = t.team_id
        WHERE e.empatados_local = (SELECT MAX(empatados_local) FROM estadisticas_local)

        UNION ALL

        SELECT 
            t.team_name AS equipo,
            e.perdidos_local AS total_partidos,
            'Más partidos PERDIDOS como local' AS metrica
        FROM estadisticas_local e
        JOIN `team` t ON e.home_team_id = t.team_id
        WHERE e.perdidos_local = (SELECT MAX(perdidos_local) FROM estadisticas_local);
    """

    try:
        df_matches = pd.read_sql(query, con=engine)
        st.subheader("Muestra de Partidos")
        st.dataframe(df_matches)

        df_localia = pd.read_sql(query_localia, con=engine)
        st.subheader("Resumen de Localía")
        st.dataframe(df_localia)
        
        df_datos_local = pd.read_sql(query_datos_local, con=engine)
        st.subheader("Equipos destacados en partidos de local")
        st.dataframe(df_datos_local)

        # Seccion 1: Indicadores generales de localia
        if not df_localia.empty:
            v_local = int(df_localia.loc[0, "Ganados de local"])
            v_visitante = int(df_localia.loc[0, "Ganados de Visitante"])
            empates = int(df_localia.loc[0, "Empatados"])
            total_partidos = int(df_localia.loc[0, "Total de partidos"])
            
            df_pie = pd.DataFrame({
                'Resultado': ['Ganados de local', 'Ganados de Visitante', 'Empatados'],
                'Cantidad': [v_local, v_visitante, empates]
            })
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 📊 Distribución de Resultados")
                st.subheader("Distribución de resultados de partidos")
                fig_pie = px.pie(df_pie, names='Resultado', values='Cantidad',  hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig_pie, width="stretch")
            
            with col2:
                st.markdown("### 📈 Indicadores Clave")
                st.subheader("Torneos donde el anfitrión se corona campeón")
                
                query_host_campeon = """
                    SELECT 
                        t.year AS "fecha del torneo", 
                        t.tournament_name AS "nombre del torneo", 
                        t.host_country AS "País anfitrión", 
                        te.team_code AS "código del país campeón",
                        t.winner AS "nombre del país campeón"
                    FROM tournament t
                    JOIN team te ON t.winner = te.team_name
                    WHERE t.host_won = 1 AND t.tournament_name NOT LIKE '%%Women%%'
                    ORDER BY t.year DESC;
                """
                df_host_campeon = pd.read_sql(query_host_campeon, con=engine)
                st.dataframe(df_host_campeon, width=700, height=300, hide_index=True)
                

                st.markdown("---")
                st.subheader("📊 Indicadores Clave Generales")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                render_flip_card("Partidos ganados como local", "Ganados de Local", v_local, "🏠", "bg-local")

            with col2:
                render_flip_card("Partidos ganados como visitante", "Ganados Visitante", v_visitante, "✈️", "bg-visitante")

            with col3:
                render_flip_card("Partidos empatados", "Empates", empates, "🤝", "bg-empate")

            with col4:
                render_flip_card("Partidos totales", "Total Partidos", total_partidos, "🏆", "bg-total")

        # Seccion 2: Tarjetas por equipos destacados
        if not df_datos_local.empty:
            st.markdown("---")
            st.subheader("🏅 Selección con mayores récords en casa")

            # Función para concatenar equipos si existen empates en el primer lugar
            def obtener_datos_metrica(df, metrica_buscada):
                df_filtrado = df[df['metrica'] == metrica_buscada]
                if df_filtrado.empty:
                    return "Sin datos", 0
                equipos = ", ".join(df_filtrado['equipo'].tolist())
                total = int(df_filtrado.iloc[0]['total_partidos'])
                return equipos, total

            eq_ganados, cant_ganados = obtener_datos_metrica(df_datos_local, 'Más partidos GANADOS como local')
            eq_empatados, cant_empatados = obtener_datos_metrica(df_datos_local, 'Más partidos EMPATADOS como local')
            eq_perdidos, cant_perdidos = obtener_datos_metrica(df_datos_local, 'Más partidos PERDIDOS como local')

            c1, c2, c3 = st.columns(3)

            with c1:
                render_flip_card(
                    f"Más victorias: {eq_ganados}", 
                    "Victorias Local", 
                    cant_ganados, 
                    "🥇", 
                    "bg-local"
                )

            with c2:
                render_flip_card(
                    f"Más empates: {eq_empatados}", 
                    "Empates Local", 
                    cant_empatados, 
                    "⚖️", 
                    "bg-empate"
                )

            with c3:
                render_flip_card(
                    f"Más derrotas: {eq_perdidos}", 
                    "Derrotas Local", 
                    cant_perdidos, 
                    "💔", 
                    "bg-visitante"
                )
    except Exception as e:
        st.error(f"Error al ejecutar las consultas SQL o procesar los datos: {e}")