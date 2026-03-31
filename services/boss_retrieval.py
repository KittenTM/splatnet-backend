import subprocess
import requests
import oead
import os
import xml.etree.ElementTree as ET
from config import settings, BASE_DIR

def process_boss_file():
    temp_boss = "bosstemp.bin"
    output_yaml = "boss.yaml"
    decrypt_script = os.path.join(BASE_DIR, "services", "decrypt.js")
    
    if not os.path.exists(decrypt_script):
        print(f"{decrypt_script} is missing!")
        return False

    try:
        base_url = settings.boss_url.rstrip('/')
        master_url = f"{base_url}/zvGSM4kOrXpkKnpT/schdat2?c=JP&l=en"
        
        print(f"data get: {master_url}")
        
        meta_res = requests.get(master_url, timeout=10)
        meta_res.raise_for_status()
        root = ET.fromstring(meta_res.content)
        data_url_element = root.find(".//Url")
        if data_url_element is None or not data_url_element.text:
            print("woops! no <Url> tag found in the XML response")
            return False
        real_data_url = data_url_element.text.strip()
        print(f"parsed data url: {real_data_url}")
        res = requests.get(real_data_url, timeout=10)
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

    except ET.ParseError:
        print("woops! the url returned non xml... we're hanging here")
        return False
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