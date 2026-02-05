from flask import Flask, request, redirect
import requests
import base64

app = Flask(__name__)

SPFN_API_URL = "https://account.spfn.net/api/v2/oauth2/generate_token"

def generate_spfn_token(encoded_creds):
    headers = {
        "Authorization": f"Basic {encoded_creds}",
        "User-Agent": "saturday & allison should lwk kiss..."
    }

    response = requests.get(SPFN_API_URL, headers=headers, timeout=10)
    if not response.ok:
        return None

    data = response.json()
    return data.get("token")


@app.route('/api/v2/sso/spfn/generate_token', methods=['POST'])
def handle_login():
    username = request.form.get('username')
    password = request.form.get('password')

    # fuck you login_host
    login_host = request.referrer or "/"
    if login_host.endswith('/'):
        login_host = login_host[:-1]

    creds = f"{username} {password}"
    encoded_creds = base64.b64encode(creds.encode()).decode()

    try:
        token = generate_spfn_token(encoded_creds)

        #if onika eat burgers then does oomi appear?
        if token:
            print("=== TOKEN ===")
            print(token)
            print("=============")

            profile_headers = {
                "Authorization": f"Bearer {token}",
                "User-Agent": "maple still awake"
            }

            profile_response = requests.get(
                "https://account.spfn.net/api/v2/users/@me/profile",
                headers=profile_headers,
                timeout=10
            )

            if profile_response.ok:
                print("=== PROFILE ===")
                print(profile_response.text)
                print("===============")
            else:
                print("Profile request failed:", profile_response.status_code)

            redirect_to = request.args.get('redirect', f"{login_host}/friend_list/")
            return redirect(redirect_to)

        else:
            sep = "&" if "?" in login_host else "?"
            return redirect(
                f"{login_host}/users/auth/splatfestival/{sep}error=auth&username={username}"
            )

    except Exception as e:
        return f"Proxy Error: {str(e)}", 500


if __name__ == '__main__':
    app.run(port=5000)
