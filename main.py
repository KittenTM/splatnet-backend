from fastapi import FastAPI, Request, Response
from routes import sessionid_check, sso
from config import settings
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from database import init_db, SessionLocal, PlayerRank
from routes import logout
from routes import boss
#yes meow meow import me please... i want to be embedded into my code... :pleading_face:
from routes import me
from routes.equipment import equipment_history
from routes.equipment import equipment
from services.boss_retrieval import process_boss_file
from routes import Ranking
from routes import twitter_link
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from sqlalchemy import delete
from config import BASE_DIR
import yaml
import asyncio
import subprocess
import signal
import sys
import httpx
import os

JUDD_CWD = os.path.join(BASE_DIR, "judd")
JUDD_SERVER_JS = os.path.join(JUDD_CWD, "server.js") 
JUDD_CMD = ["node", JUDD_SERVER_JS]

judd_process = None
skip_upcoming_reset = False

async def boss_worker_loop():
    print("background worker started")
    while True:
        try:
            print("running boss service")
            process_boss_file()
        except Exception as e:
            print(f"worker error: {e}")
        await asyncio.sleep(3600)

async def weekly_rank_reset_loop():
    global skip_upcoming_reset
    print("weekly_rank_reset worker started")
    
    FES_BOSS_PATH = os.path.join(BASE_DIR, "fes_boss.yaml")

    def get_next_sunday_reset_time_utc():
        now_utc = datetime.now(timezone.utc)
        days_ahead = 6 - now_utc.weekday()
        if days_ahead <= 0: 
            days_ahead += 7
        next_sunday_utc = now_utc + timedelta(days=days_ahead)
        return next_sunday_utc.replace(hour=0, minute=0, second=0, microsecond=0)

    async def check_splatfest_schedule_loop():
        global skip_upcoming_reset
        while True:
            try:
                target_reset_utc = get_next_sunday_reset_time_utc()
                print(f"checking if a splatfest will be active at: {target_reset_utc.isoformat()}")
                
                if os.path.exists(FES_BOSS_PATH):
                    with open(FES_BOSS_PATH, "r", encoding="utf-8") as f:
                        fes_data = yaml.safe_load(f)
                    
                    if fes_data and "Time" in fes_data:
                        start_time = datetime.fromisoformat(fes_data["Time"]["Start"])
                        end_time = datetime.fromisoformat(fes_data["Time"]["End"])
                        
                        start_time_utc = start_time.astimezone(timezone.utc)
                        end_time_utc = end_time.astimezone(timezone.utc)
                        
                        print(f"detected splatfest schedule: {start_time_utc.isoformat()} to {end_time_utc.isoformat()}")
                        
                        if start_time_utc <= target_reset_utc <= end_time_utc:
                            skip_upcoming_reset = True
                            print("Splatfest detected in reset window")
                        else:
                            skip_upcoming_reset = False
                            print("No splatfest active in reset window, yay!!!")
                else:
                    print("could not find yaml, defaulted to no fest")
                    skip_upcoming_reset = False
                    
            except Exception as e:
                print(f"failed to check fest schedule: {e}")
            
            await asyncio.sleep(7200)

    asyncio.create_task(check_splatfest_schedule_loop())

    while True:
        now_utc = datetime.now(timezone.utc)
        next_run_utc = get_next_sunday_reset_time_utc()
        wait_seconds = (next_run_utc - now_utc).total_seconds()
        
        print(f"Next ranking reset scheduled for: {next_run_utc.isoformat()} (in {wait_seconds:.0f} seconds)")
        
        try:
            await asyncio.sleep(wait_seconds)
            
            print("ranking reset triggerred!")
            
            if skip_upcoming_reset:
                print("Reset skipped due to active splatfest")
            else:
                print("Executing weekly ranking reset...")
                with SessionLocal() as db:
                    db.execute(delete(PlayerRank))
                    db.commit()
                print("Ranking table cleared successfully.")
                await FastAPICache.clear() 
                print("Cache cleared")
                
            await asyncio.sleep(60) 
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Ranking reset error: {e}")
            await asyncio.sleep(60)

@asynccontextmanager
async def lifespan(app: FastAPI):
    FastAPICache.init(InMemoryBackend())
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
    boss_task = asyncio.create_task(boss_worker_loop())
    reset_task = asyncio.create_task(weekly_rank_reset_loop())
    
    yield
    print("shutdown: cancelling background tasks")
    boss_task.cancel()
    reset_task.cancel()

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
app.include_router(twitter_link.router, prefix="/api/v1")

def start():
    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=False)

if __name__ == '__main__':
    start()