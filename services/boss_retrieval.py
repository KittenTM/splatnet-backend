import subprocess
import requests
import oead
import os
from config import settings

def process_boss_file():
    temp_boss = "bosstemp.bin"
    output_yaml = "boss.yaml"
    decrypt_script = os.path.join("services", "decrypt.js")
    
    if not os.path.exists(decrypt_script):
        print(f"{decrypt_script} is missing!")
        return False

    try:
        boss_url = settings.boss_url
        res = requests.get(boss_url, timeout=10)
        res.raise_for_status()
        
        with open(temp_boss, "wb") as f:
            f.write(res.content)

        node_env = os.environ.copy()
        node_env["BOSS_AES_KEY"] = settings.boss_aes_key
        node_env["BOSS_HMAC_KEY"] = settings.boss_hmac_key

        result = subprocess.run(
            ['node', decrypt_script, temp_boss],
            capture_output=True,
            text=False,
            env=node_env
        )
        
        if result.returncode != 0:
            print(f"decrypt fail! {result.stderr.decode()}")
            return False

        byml_obj = oead.byml.from_binary(result.stdout)
        yaml_content = oead.byml.to_text(byml_obj)
        
        with open(output_yaml, "w", encoding="utf-8") as f:
            f.write(yaml_content)
            
        print(f"yay! success: {output_yaml}")
        return True

    except Exception as e:
        print(f"exception {e}")
        return False

    finally:
        print("garbage pickup is running (boss)")
        if os.path.exists(temp_boss):
            os.remove(temp_boss)
            print(f"Removed {temp_boss}")
            
        if os.path.exists("boss.byml"):
            os.remove("boss.byml")
            print("Removed boss.byml")