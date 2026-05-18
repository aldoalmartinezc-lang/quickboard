"""Quick smoke test: verify that the database layer can create all tables."""
from sqlmodel import SQLModel

from quickboard.db import init_db, create_test_engine

engine = create_test_engine()
init_db(engine)
print("Database layer initialized successfully")
print("Tables registered:", sorted(SQLModel.metadata.tables.keys()))