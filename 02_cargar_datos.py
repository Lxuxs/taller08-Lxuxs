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

SQLITE_URL = "sqlite:///paises.db"
CSV_PATH = Path("data/jugadores_futbol.csv")


def cargar_datos(session):
    # ----- 1) Cargar continentes -----
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

    # ----- 2) Cargar países -----
    cache_pais = {}
    for nombre_pais, nombre_cont in PAIS_CONTINENTE.items():
        pais = session.query(Pais).filter_by(nombre=nombre_pais).first()
        if not pais:
            pais = Pais(nombre=nombre_pais, continente=cache_cont[nombre_cont])
            session.add(pais)
        cache_pais[nombre_pais] = pais
    session.flush()
    print(f"   - Países insertados: {len(cache_pais)}")

    # ----- 3) Cargar jugadores desde CSV -----
    # utf-8-sig: el CSV trae BOM al inicio
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"No se encontró el archivo {CSV_PATH.resolve()}")

    insertados = 0
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pais_nac = cache_pais.get(row["pais_nacimiento"])
            pais_jue = cache_pais.get(row["pais_donde_juega"])
            if not pais_nac or not pais_jue:
                # País no mapeado: lo saltamos avisando
                print(
                    f"   ! Saltado (país no mapeado): {row['nombre_jugador']} "
                    f"-> {row['pais_nacimiento']} / {row['pais_donde_juega']}"
                )
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
    print(">> Conectando a paises.db")
    engine = get_engine(SQLITE_URL, echo=False)
    crear_tablas(engine)  # por si acaso
    session = get_session(engine)

    # Evitar duplicar si se ejecuta dos veces: vaciamos en orden inverso
    if session.query(Jugador).count() > 0:
        print(">> Limpiando datos previos para recargar...")
        session.query(Jugador).delete()
        session.query(Pais).delete()
        session.query(Continente).delete()
        session.commit()

    print(">> Cargando datos desde CSV con ORM")
    cargar_datos(session)

    # ---- Resumen final ----
    print("\n=== RESUMEN ===")
    print(f"Continentes: {session.query(Continente).count()}")
    print(f"Países:      {session.query(Pais).count()}")
    print(f"Jugadores:   {session.query(Jugador).count()}")

    session.close()
    print(">> Listo.")


if __name__ == "__main__":
    main()
