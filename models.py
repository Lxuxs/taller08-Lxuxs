r"""
models.py
---------
Definición de entidades usando SQLAlchemy ORM.

Entidades:
- Continente (1) ----< (N) Pais (1) ----< (N) Jugador (pais_nacimiento)
                                       \---< (N) Jugador (pais_donde_juega)
"""

from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


class Continente(Base):
    __tablename__ = "continente"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), unique=True, nullable=False)

    # Relación inversa: un continente tiene muchos países
    paises = relationship("Pais", back_populates="continente")

    def __repr__(self):
        return f"<Continente(id={self.id}, nombre='{self.nombre}')>"


class Pais(Base):
    __tablename__ = "pais"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(80), unique=True, nullable=False)
    continente_id = Column(Integer, ForeignKey("continente.id"), nullable=False)

    continente = relationship("Continente", back_populates="paises")

    # Un país puede ser país de nacimiento de muchos jugadores
    jugadores_nacidos = relationship(
        "Jugador",
        back_populates="pais_nacimiento",
        foreign_keys="Jugador.pais_nacimiento_id",
    )
    # Un país puede ser donde juegan muchos jugadores
    jugadores_que_juegan = relationship(
        "Jugador",
        back_populates="pais_donde_juega",
        foreign_keys="Jugador.pais_donde_juega_id",
    )

    def __repr__(self):
        return f"<Pais(id={self.id}, nombre='{self.nombre}')>"


class Jugador(Base):
    __tablename__ = "jugador"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(120), nullable=False)
    posicion = Column(String(50), nullable=False)
    edad = Column(Integer, nullable=False)
    numero_partidos_seleccion = Column(Integer, nullable=False, default=0)
    goles_seleccion = Column(Integer, nullable=False, default=0)

    pais_nacimiento_id = Column(Integer, ForeignKey("pais.id"), nullable=False)
    pais_donde_juega_id = Column(Integer, ForeignKey("pais.id"), nullable=False)

    pais_nacimiento = relationship(
        "Pais",
        back_populates="jugadores_nacidos",
        foreign_keys=[pais_nacimiento_id],
    )
    pais_donde_juega = relationship(
        "Pais",
        back_populates="jugadores_que_juegan",
        foreign_keys=[pais_donde_juega_id],
    )

    def __repr__(self):
        return f"<Jugador(id={self.id}, nombre='{self.nombre}')>"


# ---------------------------------------------------------------------------
# Mapeo país -> continente (para poblar la tabla Continente y enlazar países)
# ---------------------------------------------------------------------------
PAIS_CONTINENTE = {
    # América
    "Argentina": "América",
    "Brasil": "América",
    "Ecuador": "América",
    "Estados Unidos": "América",
    "México": "América",
    # Europa
    "Alemania": "Europa",
    "España": "Europa",
    "Francia": "Europa",
    "Inglaterra": "Europa",
    "Portugal": "Europa",
    # África
    "Marruecos": "África",
    "Nigeria": "África",
    "Senegal": "África",
    # Asia
    "Japón": "Asia",
    # Oceanía
    "Australia": "Oceanía",
}


# ---------------------------------------------------------------------------
# Helpers para obtener engine y session
# ---------------------------------------------------------------------------
def get_engine(url: str, echo: bool = False):
    """Crea y devuelve un engine de SQLAlchemy a partir de una URL."""
    return create_engine(url, echo=echo, future=True)


def get_session(engine):
    """Crea una sesión vinculada al engine."""
    Session = sessionmaker(bind=engine, future=True)
    return Session()


def crear_tablas(engine):
    """Crea todas las tablas declaradas en Base si no existen."""
    Base.metadata.create_all(engine)
