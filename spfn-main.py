#TODO: make this more modular for future use

# TLDR FOR ANYONE READING THIS:
# THIS IS A SIMPLE API TO ACCEPT LOGIN REQUESTS
# FROM THE NN LOGIN PAGE ON THE SPLATNET RECREATION
#yes i unintentionally had caps on im sorry, but this is
# a really thrown together piece of code so whatever
# breaks will most likely be rewritten later

from flask import Flask, request, redirect
import requests
import base64

app = Flask(__name__)

SPFN_API_URL = "https://account.spfn.net/api/v2/oauth2/generate_token"

@app.route('/api/v2/sso/spfn/generate_token', methods=['POST'])
def handle_login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    #fuck you login_host
    login_host = request.referrer or "/"
    if login_host.endswith('/'):
        login_host = login_host[:-1]

    creds = f"{username} {password}"
    encoded_creds = base64.b64encode(creds.encode()).decode()
    headers = {
        "Authorization": f"Basic {encoded_creds}",
        "User-Agent": "maple if you see this its 10:27am with no sleep how do you feel about this"
    }

    try:
        response = requests.get(SPFN_API_URL, headers=headers, timeout=10)

        if response.ok:
            redirect_to = request.args.get('redirect', f"{login_host}/friend_list/")
            return redirect(redirect_to)
        else:
            sep = "&" if "?" in login_host else "?"
            return redirect(f"{login_host}/users/auth/splatfestival/{sep}error=auth&username={username}")

    except Exception as e:
        return f"Proxy Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(port=5000)