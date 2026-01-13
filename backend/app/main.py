from fastapi import FastAPI

from app.db.database import Base, engine

Base.metadata.create_all(engine)

app = FastAPI()
