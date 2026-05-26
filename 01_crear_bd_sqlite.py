
from models import get_engine, crear_tablas

SQLITE_URL = "sqlite:///paises.db"


def main():
    print(">> Creando base de datos SQLite: paises.db")
    engine = get_engine(SQLITE_URL, echo=False)
    crear_tablas(engine)
    print(">> Tablas creadas: continente, pais, jugador")
    print(">> Listo. Archivo generado: paises.db")


if __name__ == "__main__":
    main()
