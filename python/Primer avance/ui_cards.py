import streamlit as st

def inject_card_css():
    """Inyecta los estilos CSS globales para las tarjetas 3D Flip."""
    st.markdown("""
        <style>
        /* Contenedor principal de la tarjeta */
        .flip-card {
            background-color: transparent;
            width: 100%;
            height: 160px;
            perspective: 1000px;
            margin-bottom: 15px;
            cursor: pointer;
        }

        /* Contenedor interno con la animación de giro */
        .flip-card-inner {
            position: relative;
            width: 100%;
            height: 100%;
            text-align: center;
            transition: transform 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            transform-style: preserve-3d;
        }

        /* Giro de 180 grados al interactuar */
        .flip-card:hover .flip-card-inner, .flip-card:active .flip-card-inner {
            transform: rotateY(180deg);
        }

        /* Lados frontal y trasero */
        .flip-card-front, .flip-card-back {
            position: absolute;
            width: 100%;
            height: 100%;
            -webkit-backface-visibility: hidden;
            backface-visibility: hidden;
            border-radius: 15px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 15px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.3);
            color: white;
        }

        .flip-card-front {
            border: 2px solid rgba(255, 255, 255, 0.2);
        }

        .flip-card-back {
            transform: rotateY(180deg);
            border: 2px solid rgba(255, 255, 255, 0.4);
        }

        .card-icon {
            font-size: 32px;
            margin-bottom: 8px;
        }

        .card-label {
            font-size: 15px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
            line-height: 1.3;
        }

        .card-hint {
            font-size: 11px;
            margin-top: 8px;
            opacity: 0.8;
            font-style: italic;
        }

        .card-value {
            font-size: 40px;
            font-weight: 800;
            text-shadow: 2px 2px 5px rgba(0,0,0,0.5);
        }

        /* Colores degradados */
        .bg-local { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
        .bg-visitante { background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%); }
        .bg-empate { background: linear-gradient(135deg, #FFB75E 0%, #ED8F03 100%); }
        .bg-total { background: linear-gradient(135deg, #1F1C2C 0%, #928DAB 100%); }
        </style>
    """, unsafe_allow_html=True)


def render_flip_card(title_front, title_back, value, icon, bg_class):
    """
    Renderiza una tarjeta 3D Flip con frente y reverso personalizables.
    """
    st.markdown(f"""
        <div class="flip-card">
          <div class="flip-card-inner">
            <div class="flip-card-front {bg_class}">
              <div class="card-icon">{icon}</div>
              <div class="card-label">{title_front}</div>
              <div class="card-hint">🔄 Toca para girar</div>
            </div>
            <div class="flip-card-back {bg_class}">
              <div class="card-label">{title_back}</div>
              <div class="card-value">{value:,}</div>
            </div>
          </div>
        </div>
    """, unsafe_allow_html=True)