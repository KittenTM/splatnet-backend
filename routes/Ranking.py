from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import desc
from database import SessionLocal, PlayerRank

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/leaderboard")
async def get_leaderboard(db: DBSession = Depends(get_db)):
    try:
        top_100_query = (
            db.query(PlayerRank.PId)
            .order_by(desc(PlayerRank.FesPower))
            .limit(100)
            .all()
        )
        top_100_tuples = set(top_100_query)
        modes = {0, 1, 2}
        leaderboard = {}

        for mode in modes:
            top_players = (
                db.query(PlayerRank)
                .filter(PlayerRank.GameMode == mode)
                .order_by(desc(PlayerRank.RankingScore))
                .limit(9)
                .all()
            )

            mode_results = []
            for player in top_players:
                player_pid_tuple = (player.PId,)
                is_top_100 = player_pid_tuple in top_100_tuples
                mode_results.append({
                    "PId": player.PId,
                    "MiiName": player.MiiName,
                    "Rank": player.Rank,
                    "WinSum": player.WinSum,
                    "LoseSum": player.LoseSum,
                    "RankingScore": round(player.RankingScore, 2),
                    "FesPower": player.FesPower,
                    "is_top_100_fes": is_top_100
                })
            
            leaderboard[f"mode_{mode}"] = mode_results

        return leaderboard

    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}