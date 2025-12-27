from fastapi import FastAPI

app = FastAPI(title="Hazm Tuwaiq API")

@app.get("/")
def root():
    return {"status": "Hazm Tuwaiq backend is running"}
