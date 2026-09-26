# queries.py

# --- CONSULTAS PARA "Análisis del fenómeno de localía" ---

QUERY_SAMPLE_MATCHES = """
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

QUERY_LOCALIA_RESUMEN = """
    SELECT
        SUM(m.home_team_win) as "Ganados de local",
        SUM(m.away_team_win) as "Ganados de Visitante",
        SUM(m.draw) as "Empatados",
        SUM(m.home_team_win) + SUM(m.away_team_win) + SUM(m.draw) as "Total de partidos" 
    FROM matches m;
"""

QUERY_DATOS_LOCAL_DESTACADOS = """
    WITH estadisticas_local AS (
        SELECT 
            m.home_team_id,
            COALESCE(SUM(m.home_team_win), 0) AS ganados_local,
            COALESCE(SUM(m.draw), 0) AS empatados_local,
            COALESCE(SUM(m.away_team_win), 0) AS perdidos_local
        FROM matches m
        GROUP BY m.home_team_id
    )
    SELECT 
        t.team_name AS equipo,
        e.ganados_local AS total_partidos,
        'Más partidos GANADOS como local' AS metrica
    FROM estadisticas_local e
    JOIN team t ON e.home_team_id = t.team_id
    WHERE e.ganados_local = (SELECT MAX(ganados_local) FROM estadisticas_local)

    UNION ALL

    SELECT 
        t.team_name AS equipo,
        e.empatados_local AS total_partidos,
        'Más partidos EMPATADOS como local' AS metrica
    FROM estadisticas_local e
    JOIN team t ON e.home_team_id = t.team_id
    WHERE e.empatados_local = (SELECT MAX(empatados_local) FROM estadisticas_local)

    UNION ALL

    SELECT 
        t.team_name AS equipo,
        e.perdidos_local AS total_partidos,
        'Más partidos PERDIDOS como local' AS metrica
    FROM estadisticas_local e
    JOIN team t ON e.home_team_id = t.team_id
    WHERE e.perdidos_local = (SELECT MAX(perdidos_local) FROM estadisticas_local);
"""

QUERY_HOST_CAMPEON = """
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

# queries.py

# --- CONSULTAS PARA "Dinámica temporal de goles" ---

# queries.py

# --- CONSULTAS PARA "Dinámica temporal de goles" ---

QUERY_GOLES_MEN = """
    SELECT 
        CAST(t.year AS UNSIGNED) AS "Año",
        SUM(m.home_team_score + m.away_team_score) AS "Total de Goles",
        COUNT(m.match_id) AS "Partidos Jugados",
        ROUND(SUM(m.home_team_score + m.away_team_score) / COUNT(m.match_id), 2) AS "Promedio de Goles",
        'Masculino' AS "Categoría"
    FROM matches m
    JOIN tournament t ON m.tournament_id = t.tournament_id
    WHERE t.tournament_name NOT LIKE '%%Women%%'
    GROUP BY t.year
    ORDER BY t.year;
"""

QUERY_GOLES_WOMEN = """
    SELECT 
        CAST(t.year AS UNSIGNED) AS "Año",
        SUM(m.home_team_score + m.away_team_score) AS "Total de Goles",
        COUNT(m.match_id) AS "Partidos Jugados",
        ROUND(SUM(m.home_team_score + m.away_team_score) / COUNT(m.match_id), 2) AS "Promedio de Goles",
        'Femenino' AS "Categoría"
    FROM matches m
    JOIN tournament t ON m.tournament_id = t.tournament_id
    WHERE t.tournament_name LIKE '%%Women%%'
    GROUP BY t.year
    ORDER BY t.year;
"""