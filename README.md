<p align= "center">
<img src="https://git.crafterpika.cc/kittentm/splatnet-backend/raw/branch/main/cover.png" width=600>
<br>

   <img src="https://git.crafterpika.cc/kittentm/splatnet-backend/raw/branch/main/currentprogress.png" height=50px> 
  <img src="https://progress-bar.xyz/10?title=&height=20&show_text=false" width="100%" height=20px>
  <br>
  <strong>Basically 0% lol</strong>
</p>

---

### Overview

This project is set up in a weird way. To properly host, first install all the python dependencies, then in `/judd` install the node modules. The way this server works is main.py launches and manages Judd alongside the API for the web server. While this technically means you can seperate Judd and run it by itself, it is not reccomended and can run into issues. It is best to run them on the same server via `main.py`.

> [!IMPORTANT]  
> This project is not easy to self host!! While I have made attempts to mitigate that, I do not want to update the readme everytime I add a new dependency. Proceed with caution ;-;

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
| `judd_port` | `int` | `4000` | The port the Judd (telemetry) server will listen on |

> [!TIP]
> For dumping your boss keys, see [this](https://github.com/PretendoNetwork/BetterKeyDumper/releases/tag/v1.0.0) HBL app. Note that the keys shown on the screen are garbage, I reccomend using a hex editor on the files it dumps.