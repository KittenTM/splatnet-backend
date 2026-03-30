<p align= "center">
<img src="https://git.crafterpika.cc/kittentm/splatnet-backend/raw/branch/main/cover.png" width=600>
<br>

   <img src="https://git.crafterpika.cc/kittentm/splatnet-backend/raw/branch/main/currentprogress.png" height=50px> 
  <img src="https://progress-bar.xyz/40?title=&height=20&show_text=false" width="100%" height=20px>
  <br>
  <strong>Basically 0% lol</strong>
</p>

---
<div align=center>

# SplatNet

[![Commits](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fgit.crafterpika.cc%2Fapi%2Fv1%2Frepos%2Fkittentm%2Fsplatnet-backend%2Fcommits&query=%24.length&label=commits&style=for-the-badge&color=blue)](https://git.crafterpika.cc/kittentm/splatnet-backend/commits/branch/main)
[![Build Status](https://git.crafterpika.cc/kittentm/splatnet-backend/badges/workflows/build.yml/badge.svg?style=for-the-badge)](https://git.crafterpika.cc/kittentm/splatnet-backend/actions)
[![Languages](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fgit.crafterpika.cc%2Fapi%2Fv1%2Frepos%2Fkittentm%2Fsplatnet-backend%2Flanguages&query=%24.*~&label=language&style=for-the-badge&color=yellow)](https://git.crafterpika.cc/kittentm/splatnet-backend)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg?style=for-the-badge&logo=gnu&logoColor=white)](https://git.crafterpika.cc/kittentm/splatnet-backend/src/branch/main/LICENSE)

This is the backend for the [SplatNet](https://git.crafterpika.cc/kittentm/splatnet) Revival frontend. It is a combination of Python & JS.

</div>

## Self-hosting

> [!IMPORTANT]  
> This project is not easy to self host!! Please please please read the console logs before asking for help.

### Installing from source

Telemetry is technically not required for the server to run, however it is required for most functions on the website. Judd is run via Node `/judd`. First change directories to Judd, and install the node modules.
```
npm install
```

To start, install Python `3.11+`. While newer versions aren't tested they should work fine. Then install using:
```
pip install . -v
```

> [!NOTE]  
> It is not required to run in verbose, however is reccomended as otherwise it looks like it has hung. The installation progress will take awhile as it copies all Node modules.

Now you must configure your `.env` A example `.env` is included for you. For a full explanation, jump to [.env configuration](https://git.crafterpika.cc/kittentm/splatnet-backend#env-configuration).
Once done, run:
```
splatnet
```
This uses the `.env` found in your current directory.

### Docker
Alternatively, this is available as a Docker image.

> [!NOTE]  
> Postgres & incoming connections will have to be manually allowed through into Docker

```
docker run kittentm/splatnet-backend:latest
```

By default, the program will look for the `.env` in the same directory main.py is located. If you wish to not do that, you can manually specify a `.env`

Here is an example of that, it pulls from your current directory for the .env.
```
docker run --env-file .env kittentm/splatnet-backend:latest
```

## DB Config

This project requires postgres. Database setup is automatic upon startup, so all you need to do is add your database URL in the .env.

## .env configuration
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
| `webhook_url` | str | *Required* | Where logging of blacklist.json will be sent to |

> [!TIP]
> For dumping your boss keys, see [this](https://github.com/PretendoNetwork/BetterKeyDumper/releases/tag/v1.0.0) HBL app. Note that the keys shown on the screen are garbage, I reccomend using a hex editor on the files it dumps.