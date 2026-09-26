import streamlit as st
import pandas as pd
import plotly.express as px
from connection import get_connection_engine
from ui_cards import inject_card_css, render_flip_card

# Importación de las consultas SQL organizadas
from queries import (
    QUERY_SAMPLE_MATCHES,
    QUERY_LOCALIA_RESUMEN,
    QUERY_DATOS_LOCAL_DESTACADOS,
    QUERY_HOST_CAMPEON,
    QUERY_GOLES_MEN,
    QUERY_GOLES_WOMEN
)

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
    
    inject_card_css()

    try:
        df_matches = pd.read_sql(QUERY_SAMPLE_MATCHES, con=engine)
        st.subheader("Muestra de Partidos")
        st.dataframe(df_matches)

        df_localia = pd.read_sql(QUERY_LOCALIA_RESUMEN, con=engine)
        st.subheader("Resumen de Localía")
        st.dataframe(df_localia)
        
        df_datos_local = pd.read_sql(QUERY_DATOS_LOCAL_DESTACADOS, con=engine)
        st.subheader("Equipos destacados en partidos de local")
        st.dataframe(df_datos_local)

        # Sección 1: Indicadores generales de localía
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
                fig_pie = px.pie(df_pie, names='Resultado', values='Cantidad', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                st.markdown("### 📈 Indicadores Clave")
                st.subheader("Torneos donde el anfitrión se corona campeón")
                
                df_host_campeon = pd.read_sql(QUERY_HOST_CAMPEON, con=engine)
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

        # Sección 2: Tarjetas por equipos destacados
        if not df_datos_local.empty:
            st.markdown("---")
            st.subheader("🏅 Selección con mayores récords en casa")

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
                render_flip_card(f"Más victorias como local: {eq_ganados}", "Victorias como local", cant_ganados, "🥇", "bg-local")

            with c2:
                render_flip_card(f"Más empates como local: {eq_empatados}", "Empates como local", cant_empatados, "⚖️", "bg-empate")

            with c3:
                render_flip_card(f"Más derrotas como local: {eq_perdidos}", "Derrotas como local", cant_perdidos, "💔", "bg-perdidos")
                
    except Exception as e:
        st.error(f"Error al ejecutar las consultas SQL o procesar los datos: {e}")

# Sección: Dinámica temporal de goles
if sidebar_menu == "Dinámica temporal de goles":
    st.header("📅 Dinámica temporal y promedio de goles en la Copa del Mundo")
    st.markdown(
        "Analiza tanto el volumen absoluto de anotaciones como el promedio real de goles por partido entre ambos torneos."
    )
    
    inject_card_css()

    try:
        df_goles_men = pd.read_sql(QUERY_GOLES_MEN, con=engine)
        df_goles_women = pd.read_sql(QUERY_GOLES_WOMEN, con=engine)
        
        df_goles = pd.concat([df_goles_men, df_goles_women]).sort_values(by="Año").reset_index(drop=True)
        
        # 1. Gráficos en dos columnas comparativas
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.subheader("📈 Volumen Total de Goles")
            fig_total = px.line(
                df_goles, 
                x="Año", 
                y="Total de Goles", 
                color="Categoría",
                markers=True,
                title="Goles Totales por Edición",
                labels={"Año": "Año", "Total de Goles": "Total Goles", "Categoría": "Torneo"},
                color_discrete_map={"Masculino": "#0055B7", "Femenino": "#E63946"}
            )
            fig_total.update_xaxes(type='linear', dtick=8, tickangle=-45)
            fig_total.update_layout(hovermode="x unified", legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"))
            st.plotly_chart(fig_total, use_container_width=True)

        with col_g2:
            st.subheader("⚡ Promedio de Goles por Partido")
            fig_prom = px.line(
                df_goles, 
                x="Año", 
                y="Promedio de Goles", 
                color="Categoría",
                markers=True,
                title="Promedio de Goles por Encuentro",
                labels={"Año": "Año", "Promedio de Goles": "Goles / Partido", "Categoría": "Torneo"},
                color_discrete_map={"Masculino": "#0055B7", "Femenino": "#E63946"}
            )
            fig_prom.update_xaxes(type='linear', dtick=8, tickangle=-45)
            fig_prom.update_layout(hovermode="x unified", legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"))
            st.plotly_chart(fig_prom, use_container_width=True)

        st.markdown("---")

        # 2. Tarjetas de métricas y Conclusiones del Negocio/Ciencia de Datos
        st.subheader("💡 Métricas Clave y Conclusiones del Análisis")

        # Cálculo de promedios históricos globales
        prom_men = round(df_goles_men["Total de Goles"].sum() / df_goles_men["Partidos Jugados"].sum(), 2)
        prom_women = round(df_goles_women["Total de Goles"].sum() / df_goles_women["Partidos Jugados"].sum(), 2)
        
        col_c1, col_c2 = st.columns([1, 2])
        
        with col_c1:
            render_flip_card("Histórico Masculino", "Promedio Goles/Partido", prom_men, "⚽", "bg-local")
            render_flip_card("Histórico Femenino", "Promedio Goles/Partido", prom_women, "🌟", "bg-visitante")

        with col_c2:
            st.markdown(
                f"""
                <div style="background-color: #1E293B; border-left: 5px solid #38EF7D; padding: 18px; border-radius: 10px; color: #F8FAFC;">
                    <h4 style="margin-top: 0px; color: #38EF7D;">📌 Hallazgos de Ciencia de Datos:</h4>
                    <ul style="font-size: 14px; line-height: 1.6; margin-bottom: 0px;">
                        <li><b>Efecto de Escala en Volumen:</b> La aparente brecha histórica de goles entre 1991 y 2011 se debió al calendario: el torneo masculino constaba de <b>64 partidos</b> (32 selecciones), mientras que el femenino disputaba solo <b>26 a 32 partidos</b>.</li>
                        <li><b>Rendimiento Ofensivo Real:</b> Al normalizar los datos por encuentro, el torneo femenino presenta un promedio histórico (<b>{prom_women} goles/partido</b>) muy competitivo e incluso superior a las primeras ediciones modernas masculinas (<b>{prom_men} goles/partido</b>).</li>
                        <li><b>Convergencia Competitiva:</b> A medida que la FIFA aumentó a 24 y 32 selecciones el certamen femenino, la cantidad absoluta de goles se disparó rápidamente, cerrando la brecha total a solo unos pocos goles de diferencia.</li>
                    </ul>
                </div>
                """, 
                unsafe_allow_html=True
            )

        st.markdown("---")
        st.subheader("📋 Datos Detallados")
        st.dataframe(df_goles, use_container_width=True)

    except Exception as e:
        st.error(f"Error al ejecutar la consulta SQL o procesar los datos: {e}")