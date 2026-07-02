from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import desc
from database import SessionLocal, PlayerRank, EquipmentLast
from fastapi_cache.decorator import cache

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/leaderboard/getplayerstats/{pid}")
@cache(expire=60)
async def get_player_stats(pid: int, mode: int | None = None, db: DBSession = Depends(get_db)):
    try:
        query = (
            db.query(PlayerRank, EquipmentLast)
            .outerjoin(EquipmentLast, PlayerRank.PId == EquipmentLast.PId)
            .filter(PlayerRank.PId == pid)
        )
        
        if mode is not None:
            query = query.filter(PlayerRank.GameMode == mode)
            
        result = query.first()

        if not result:
            raise HTTPException(status_code=404, detail="Player not found")

        player, gear = result

        player_data = {
            "PId": player.PId,
            "MiiName": player.MiiName,
            "Rank": player.Rank,
            "GameMode": player.GameMode,
            "WinSum": player.WinSum,
            "LoseSum": player.LoseSum,
            "RankingScore": round(player.RankingScore, 2),
            "weapon": gear.weapon if gear else None,
            "headgear": gear.Gear_Head if gear else None,
            "clothes": gear.Gear_Clothes if gear else None,
            "shoes": gear.Gear_Shoes if gear else None,
        }

        if player.GameMode == 2:
            top_100_query = (
                db.query(PlayerRank.PId)
                .order_by(desc(PlayerRank.FesPower))
                .limit(100)
                .all()
            )
            top_100_tuples = set(top_100_query)
            
            is_top_100 = (player.PId,) in top_100_tuples
            player_data["FesPower"] = player.FesPower
            player_data["is_top_100_fes"] = is_top_100
        else:
            player_data["FesPower"] = None
            player_data["is_top_100_fes"] = False

        return player_data

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        print(f"Error fetching stats for player {pid}: {e}")
        return {"error": str(e)}