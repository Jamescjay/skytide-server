from fastapi import FastAPI
import models
from database import engine
from resources import movies, likes

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


app.include_router(movies.router)  
app.include_router(likes.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Movie Review API"}
