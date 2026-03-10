from fastapi import APIRouter, Request, Response
import yaml
import json
from datetime import datetime, timedelta

router = APIRouter()

#ripped straight from splatcord. sorry not sorry?
MAP_DATA = {
    0: {"it-IT": "Periferia urbana", "de-DE": "Dekabahnstation", "en-US": "Urchin Underpass", "es-ES": "Parque Viaducto", "ja-JP": "デカライン高架下"},
    1: {"it-IT": "Magazzino", "de-DE": "Kofferfisch-Lager", "en-US": "Walleye Warehouse", "es-ES": "Almacén Rodaballo", "ja-JP": "ハコフグ倉庫"},
    2: {"it-IT": "Raffineria", "de-DE": "Bohrinsel Nautilus", "en-US": "Saltspray Rig", "es-ES": "Plataforma Gaviota", "ja-JP": "シオノメ油田"},
    3: {"it-IT": "Centro commerciale", "de-DE": "Arowana-Center", "en-US": "Arowana Mall", "es-ES": "Plazuela del Calamar", "ja-JP": "アロワナモール"},
    4: {"it-IT": "Pista Polposkate", "de-DE": "Punkasius-Skatepark", "en-US": "Blackbelly Skatepark", "es-ES": "Parque Lubina", "ja-JP": "Ｂバスパーク"},
    5: {"it-IT": "Campeggio Totan", "de-DE": "Camp Schützenfisch", "en-US": "Camp Triggerfish", "es-ES": "Campamento Arowana", "ja-JP": "モンガラキャンプ場"},
    6: {"it-IT": "Porto Polpo", "de-DE": "Heilbutt-Hafen", "en-US": "Port Mackerel", "es-ES": "Puerto Jurel", "ja-JP": "ホッケふ頭"},
    7: {"it-IT": "Serra di alghe", "de-DE": "Tümmlerkuppel", "en-US": "Kelp Dome", "es-ES": "Jardín botánico", "ja-JP": "モズク農園"},
    8: {"it-IT": "Torri cittadine", "de-DE": "Muränentürme", "en-US": "Moray Towers", "es-ES": "Torres Merluza", "ja-JP": "タチウオパーキング"},
    9: {"it-IT": "Molo Mollusco", "de-DE": "Blauflossen-Depot", "en-US": "Bluefin Depot", "es-ES": "Mina costera", "ja-JP": "ネギトロ炭鉱"},
    10: {"it-IT": "Ponte Sgombro", "de-DE": "Makrelenbrücke", "en-US": "Hammerhead Bridge", "es-ES": "Puente Salmón", "ja-JP": "マサバ海峡大橋"},
    11: {"it-IT": "Cime sogliolose", "de-DE": "Schollensiedlung", "en-US": "Flounder Heights", "es-ES": "Complejo Medusa", "ja-JP": "ヒラメが丘団地"},
    12: {"it-IT": "Museo di Cefalò", "de-DE": "Pinakoithek", "en-US": "Museum d'Alfonsino", "es-ES": "Museo del Pargo", "ja-JP": "キンメダイ美術館"},
    13: {"it-IT": "Acciugames", "de-DE": "Anchobit Games HQ", "en-US": "Ancho-V Games", "es-ES": "Estudios Esturión", "ja-JP": "アンチョビットゲームズ"},
    14: {"it-IT": "Miniera d'Orata", "de-DE": "Steinköhler-Grube", "en-US": "Piranha Pit", "es-ES": "Cantera Tintorera", "ja-JP": "ショッツル鉱山"},
    15: {"it-IT": "Villanguilla", "de-DE": "Mahi-Mahi Resort", "en-US": "Mahi-Mahi Resort", "es-ES": "Spa Cala Bacalao", "ja-JP": "マヒマヒリゾート＆スパ"}
}

RULE_NAMES = {
    "cVar": "SplatZones",
    "cVgl": "Rainmaker",
    "cVlf": "TowerControl",
    "cPnt": "TurfWar"
}

@router.api_route('/boss', methods=['GET', 'POST'])
async def boss_rotation(request: Request):
    try:
        with open("boss.yaml", "r") as f:
            yaml_data = yaml.safe_load(f)
        
        base_time_str = yaml_data.get("ByamlInfo", {}).get("BaseByamlStartTime", "2026-02-06T06:00:00.0000000Z")
        base_time_str = base_time_str.replace('Z', '+00:00')
        current_time = datetime.fromisoformat(base_time_str)

        rotations = {}

        for phase in yaml_data.get("Phases", []):
            ts_ms = str(int(current_time.timestamp() * 1000))
            turf_stages = []
            for s in phase.get("RegularStages", []):
                mid = s.get("MapID")
                turf_stages.append({"mapID": mid, "translatedNames": MAP_DATA.get(mid, {})})

            ranked_stages = []
            for s in phase.get("GachiStages", []):
                mid = s.get("MapID")
                ranked_stages.append({"mapID": mid, "translatedNames": MAP_DATA.get(mid, {})})

            rotations[ts_ms] = {
                "turfStages": turf_stages,
                "rankedStages": ranked_stages,
                "rankedMode": RULE_NAMES.get(phase.get("GachiRule"), "SplatZones")
            }

            current_time += timedelta(hours=2)

        response_data = {
            "nintendo": {
                "notice": "Nintendo Network has been shut down. Thanks for your interest."
            },
            "pretendo": {
                "rotations": rotations
            }
        }
        
        return Response(content=json.dumps(response_data), media_type="application/json")

    except Exception as e:
        return Response(content=json.dumps({"error": str(e)}), status_code=500, media_type="application/json")