from app.config import Settings


def test_normalizes_railway_postgres_url() -> None:
    settings = Settings(database_url="postgresql://user:pass@host:5432/database")

    assert settings.database_url == (
        "postgresql+psycopg://user:pass@host:5432/database"
    )


def test_keeps_explicit_database_driver() -> None:
    url = "postgresql+psycopg://user:pass@host:5432/database"

    assert Settings(database_url=url).database_url == url
