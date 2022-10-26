from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from config.wsgi import application
from config.asgi import application as django_async_app

django_async_app = django_async_app

app = FastAPI()


@app.get("/")
def read_main():
    return {"message": "Hello World"}


app.mount("/v1", WSGIMiddleware(application))