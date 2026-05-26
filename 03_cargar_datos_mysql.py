import csv
from pathlib import Path

from models import (
    Continente,
    Pais,
    Jugador,
    PAIS_CONTINENTE,
    get_engine,
    get_session,
    crear_tablas,
)

# ---------------------------------------------------------------------------
# AJUSTAR CON LAS CREDENCIALES LOCALES
# Formato: mysql+pymysql://USUARIO:CONTRASEÑA@HOST:PUERTO/NOMBRE_BD
# ---------------------------------------------------------------------------
MYSQL_URL = "mysql+pymysql://root:root@localhost:3306/paises?charset=utf8mb4"

CSV_PATH = Path("data/jugadores_futbol.csv")


def cargar_datos(session):
    continentes_unicos = set(PAIS_CONTINENTE.values())
    cache_cont = {}
    for nombre in continentes_unicos:
        cont = session.query(Continente).filter_by(nombre=nombre).first()
        if not cont:
            cont = Continente(nombre=nombre)
            session.add(cont)
        cache_cont[nombre] = cont
    session.flush()
    print(f"   - Continentes insertados: {len(continentes_unicos)}")

    cache_pais = {}
    for nombre_pais, nombre_cont in PAIS_CONTINENTE.items():
        pais = session.query(Pais).filter_by(nombre=nombre_pais).first()
        if not pais:
            pais = Pais(nombre=nombre_pais, continente=cache_cont[nombre_cont])
            session.add(pais)
        cache_pais[nombre_pais] = pais
    session.flush()
    print(f"   - Países insertados: {len(cache_pais)}")

    if not CSV_PATH.exists():
        raise FileNotFoundError(f"No se encontró {CSV_PATH.resolve()}")

    insertados = 0
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pais_nac = cache_pais.get(row["pais_nacimiento"])
            pais_jue = cache_pais.get(row["pais_donde_juega"])
            if not pais_nac or not pais_jue:
                continue
            jugador = Jugador(
                nombre=row["nombre_jugador"].strip(),
                posicion=row["posicion"].strip(),
                edad=int(row["edad"]),
                numero_partidos_seleccion=int(row["numero_partidos_seleccion"]),
                goles_seleccion=int(row["goles_seleccion"]),
                pais_nacimiento=pais_nac,
                pais_donde_juega=pais_jue,
            )
            session.add(jugador)
            insertados += 1

    session.commit()
    print(f"   - Jugadores insertados: {insertados}")


def main():
    print(">> Conectando a MySQL/MariaDB:", MYSQL_URL)
    engine = get_engine(MYSQL_URL, echo=False)
    crear_tablas(engine)
    session = get_session(engine)

    if session.query(Jugador).count() > 0:
        print(">> Limpiando datos previos para recargar...")
        session.query(Jugador).delete()
        session.query(Pais).delete()
        session.query(Continente).delete()
        session.commit()

    print(">> Cargando datos desde CSV con ORM")
    cargar_datos(session)

    print("\n=== RESUMEN MySQL/MariaDB ===")
    print(f"Continentes: {session.query(Continente).count()}")
    print(f"Países:      {session.query(Pais).count()}")
    print(f"Jugadores:   {session.query(Jugador).count()}")

    session.close()
    print(">> Listo.")


if __name__ == "__main__":
    main()
