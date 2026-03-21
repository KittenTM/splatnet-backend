from fastapi import FastAPI, Request, Response
from routes import sessionid_check, sso
from config import settings
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routes import logout
from routes import boss
#yes meow meow import me please... i want to be embedded into my code... :pleading_face:
from routes import me
from routes.equipment import equipment_history
from routes.equipment import equipment
from services.boss_retrieval import process_boss_file
from routes import Ranking
from contextlib import asynccontextmanager
import asyncio
import subprocess
import signal
import sys
import httpx
import os

JUDD_CMD = ["node", "server.js"]
JUDD_CWD = "./judd"

judd_process = None


async def boss_worker_loop():
    print("background worker started")
    while True:
        try:
            print("running boss service")
            process_boss_file()
        except Exception as e:
            print(f"worker error: {e}")
        await asyncio.sleep(3600)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global judd_process

    print("starting judd server")
    
    env_vars = os.environ.copy()
    env_vars.update({k.upper(): str(v) for k, v in settings.model_dump().items()})

    judd_process = subprocess.Popen(
        JUDD_CMD,
        cwd=JUDD_CWD,
        stdout=sys.stdout,
        stderr=sys.stderr,
        env=env_vars,
    )

    worker = asyncio.create_task(boss_worker_loop())
    yield
    print("shutdown: cancelling background tasks")
    worker.cancel()

    if judd_process:
        judd_process.send_signal(signal.SIGINT)
        judd_process.wait()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Set-Cookie"],
)


@app.middleware("http")
async def proxy_fallback(request: Request, call_next):
    response = await call_next(request)

    if response.status_code != 404:
        return response

    url = f"http://127.0.0.1:{settings.judd_port}{request.url.path}"
    body = await request.body()

    async with httpx.AsyncClient() as client:
        try:
            judd_resp = await client.request(
                request.method,
                url,
                headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
                params=request.query_params,
                content=body,
            )
        except httpx.RequestError:
            return response

    return Response(
        content=judd_resp.content,
        status_code=judd_resp.status_code,
        headers=dict(judd_resp.headers),
    )


@app.middleware("http")
async def force_cors_on_errors(request: Request, call_next):
    response = await call_next(request)
    origin = request.headers.get("origin")
    if origin == settings.frontend_url:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

app.include_router(sso.router, prefix="/api/v2/sso")
app.include_router(sessionid_check.router, prefix="/api/v1")
app.include_router(logout.router, prefix="/api/v1")
app.include_router(boss.router, prefix="/api/v1")
app.include_router(me.router, prefix="/api/v1")
app.include_router(equipment_history.router, prefix="/api/v1")
app.include_router(equipment.router, prefix="/api/v1")
app.include_router(Ranking.router, prefix="/api/v1")

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=True)