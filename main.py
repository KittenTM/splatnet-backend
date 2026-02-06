from fastapi import FastAPI
from routes import sso
import uvicorn

app = FastAPI()
app.include_router(sso.router, prefix="/api/v2/sso")

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=5000)