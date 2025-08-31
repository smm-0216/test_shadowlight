from fastapi import FastAPI
from routers import metrics, agent

app = FastAPI()


@app.get("/")
def main():
    return {"message": "ShadowLight!"}


app.include_router(agent.router)
app.include_router(metrics.router)
