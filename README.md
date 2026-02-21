<p align= "center">
<img src="https://git.crafterpika.cc/kittentm/splatnet-backend/raw/branch/main/cover.png" width=600>
---


   <img src="https://git.crafterpika.cc/kittentm/splatnet-backend/raw/branch/main/currentprogress.png" height=50px> 
  <img src="https://progress-bar.xyz/10?title=&height=20&show_text=false" width="100%" height=20px>
  <br>
  <strong>Basically 0% lol</strong>
</p>

---

> [!IMPORTANT]  
> this readme is incomplete and you should not rely on it at this time.

### .env configuration
The .env file is used for server setup. A example one with the fields already there has been provided for your pleasure. Rename it to .env & fill in the fields.

| Field Name | Type | Default Value | Description / Usage |
| :--- | :--- | :--- | :--- |
| `port` | `int` | `5000` | The port the API will listen on |
| `db_url` | `str` | *Required* | Connection string for the database |
| `fernet_key` | `str` | *Required* | Key used for DB encryption |
| `cookie_httponly` | `bool` | `True` | Primarily for debugging, controls the flag in cookies |
| `frontend_url` | `str` | *Required* | The URL where the frontend is hosted |
| `boss_url` | `str` | *Required* | Endpoint URL for retrieving Boss |
| `boss_aes_key` | `str` | *Required* | AES key for Boss |
| `boss_hmac_key` | `str` | *Required* | HMAC key for Boss |
| `cookie_secure` | `bool` | `True` | Primarily for debugging, controls the flag in cookies |

For dumping your boss keys, see [this](https://github.com/PretendoNetwork/BetterKeyDumper/releases/tag/v1.0.0) HBL app. Note that the keys shown on the screen are garbage, I reccomend using a hex editor on the files it dumps.