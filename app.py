import pandas as pd
import streamlit as st
from sqlalchemy import func
from sqlalchemy.orm import aliased

from models import Continente, Pais, Jugador, get_engine, get_session

# ---------------------------------------------------------------------------
# Configuración inicial
# ---------------------------------------------------------------------------
SQLITE_URL = "sqlite:///paises.db"

st.set_page_config(
    page_title="Taller 08 - Jugadores de Fútbol",
    layout="wide",
)

@st.cache_resource
def get_db_session():
    engine = get_engine(SQLITE_URL)
    return get_session(engine)

session = get_db_session()

# ---------------------------------------------------------------------------
# Consultas con ORM
# ---------------------------------------------------------------------------
def tabla_jugadores_detalle() -> pd.DataFrame:
    """Tabla 1: Detalle de jugadores con su continente."""
    PaisNac = aliased(Pais)
    PaisJue = aliased(Pais)
    ContNac = aliased(Continente)

    q = (
        session.query(
            Jugador.nombre.label("Nombre Jugador"),
            PaisNac.nombre.label("País de Nacimiento"),
            PaisJue.nombre.label("País Donde Juega"),
            Jugador.posicion.label("Posición"),
            Jugador.edad.label("Edad"),
            Jugador.numero_partidos_seleccion.label("Partidos"),
            Jugador.goles_seleccion.label("Goles"),
            ContNac.nombre.label("Continente"),
        )
        .join(PaisNac, Jugador.pais_nacimiento_id == PaisNac.id)
        .join(PaisJue, Jugador.pais_donde_juega_id == PaisJue.id)
        .join(ContNac, PaisNac.continente_id == ContNac.id)
        .order_by(Jugador.nombre)
    )
    return pd.read_sql(q.statement, session.bind)


def tabla_por_continente() -> pd.DataFrame:
    """Tabla 2: Resumen por continente (# jugadores y goles totales)."""
    q = (
        session.query(
            Continente.nombre.label("Continente"),
            func.count(Jugador.id).label("Nº de Jugadores"),
            func.coalesce(func.sum(Jugador.goles_seleccion), 0).label("Goles Totales"),
        )
        .join(Pais, Pais.continente_id == Continente.id)
        .join(Jugador, Jugador.pais_nacimiento_id == Pais.id)
        .group_by(Continente.nombre)
        .order_by(Continente.nombre)
    )
    return pd.read_sql(q.statement, session.bind)


def tabla_por_pais() -> pd.DataFrame:
    """Tabla 3: Resumen por país (# jugadores y goles totales)."""
    q = (
        session.query(
            Pais.nombre.label("País"),
            func.count(Jugador.id).label("Nº de Jugadores"),
            func.coalesce(func.sum(Jugador.goles_seleccion), 0).label("Goles Totales"),
        )
        .join(Jugador, Jugador.pais_nacimiento_id == Pais.id)
        .group_by(Pais.nombre)
        .order_by(Pais.nombre)
    )
    return pd.read_sql(q.statement, session.bind)


# ---------------------------------------------------------------------------
# Interfaz Gráfica (UI)
# ---------------------------------------------------------------------------
st.title("Taller 08 - Integración de datos y uso de ORM")
st.write("Visualización de datos cargados en la base de datos relacional.")

st.divider()

# 1) Detalle de jugadores con su continente
st.subheader("1. Detalle de jugadores")
df_jug = tabla_jugadores_detalle()
st.dataframe(df_jug, use_container_width=True, hide_index=True)

st.divider()

# 2) Resumen por continente (#jugadores, #goles)
st.subheader("2. Resumen por continente")
df_cont = tabla_por_continente()
st.dataframe(df_cont, use_container_width=True, hide_index=True)

st.divider()

# 3) Resumen por país (#jugadores, #goles)
st.subheader("3. Resumen por país")
df_pais = tabla_por_pais()
st.dataframe(df_pais, use_container_width=True, hide_index=True)