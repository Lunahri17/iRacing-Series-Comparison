import os
import base64
import hashlib
import requests
from dotenv import load_dotenv
from functools import wraps
from flask import Flask, redirect, request, session, url_for, render_template, jsonify
import iracing_data_transform

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET")

# Configuración OAuth2 de iRacing
CLIENT_ID = os.getenv("IRACING_CLIENT_ID")
CLIENT_SECRET = os.getenv("IRACING_CLIENT_SECRET")
REDIRECT_URI = "https://racescheduler.lunahri.net.ar/callback"
AUTH_URL = "https://oauth.iracing.com/oauth2/authorize"
TOKEN_URL = "https://oauth.iracing.com/oauth2/token"
PROFILE_URL = "https://oauth.iracing.com/oauth2/iracing/profile"


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = session.get("access_token")
        if not token:
            return redirect(url_for("login"))

        # Validar token llamando a /profile
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(PROFILE_URL, headers=headers)

        if resp.status_code == 401:
            session.clear()
            return redirect(url_for("login"))

        return f(*args, **kwargs)
    return decorated_function

# region Renders
@app.route("/")
def index():
    return render_template("index.html")

@app.route('/dev')
@login_required
def dev():
    token = session.get("access_token")
    if not token:
        return redirect(url_for("index"))
    return render_template('series_table_dev.html')

@app.route('/series')
@login_required
def series():
    token = session.get("access_token")
    if not token:
        return redirect(url_for("index"))
    return render_template('series_table.html')

@app.route('/all_dates')
@login_required
def series_all_dates():
    token = session.get("access_token")
    if not token:
        return redirect(url_for("index"))
    return render_template('series_table_all_dates.html')

@app.route('/cars')
@login_required
def all_cars():
    token = session.get("access_token")
    if not token:
        return redirect(url_for("index"))
    return render_template('cars_table.html')
# endregion renders

# region Home
@app.route("/profile")
@login_required
def profile():
    token = session.get("access_token")
    if not token:
        return redirect(url_for("index"))

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(PROFILE_URL, headers=headers, timeout=60)

    if response.status_code != 200:
        return f"Error fetching profile: {response.text}", 400

    profile_data = response.json()

    return render_template("profile.html", profile=profile_data)
# enregion Home

# region APIs
@app.route('/get_series_list', methods=['POST'])
@login_required
def get_series_list():
    token = session.get("access_token")
    if not token:
        return redirect(url_for("index"))

    series_filtered = iracing_data_transform.get_dict_of_all_series(token)
    series_name = iracing_data_transform.get_onlys_series_name(token, series_filtered)
    return jsonify(series_name)


@app.route('/get_series_table', methods=['POST'])
@login_required
def get_series_table():
    token = session.get("access_token")
    if not token:
        return redirect(url_for("index"))

    series_filtered = iracing_data_transform.get_dict_of_all_series(token)

    series = iracing_data_transform.get_relevant_data(token, series_filtered)

    all_dates = sorted({sch["start_date_week"] for serie in series for sch in serie["schedules"]})

    return jsonify({"series": series, "all_dates": all_dates})


@app.route('/get_all_cars', methods=['POST'])
@login_required
def get_all_cars():
    token = session.get("access_token")
    if not token:
        return redirect(url_for("index"))
    try:
        cars = iracing_data_transform.get_all_licenced_cars(token)
    except requests.HTTPError as ex:
        return jsonify({"error": str(ex)}), 401

    return jsonify({"cars": cars})
# endregion APIs

# region Login
@app.route("/login")
def login():
    # 1) Crear code_verifier y guardarlo en sesión
    code_verifier = generate_code_verifier()
    session["code_verifier"] = code_verifier

    # 2) Crear code_challenge
    code_challenge = generate_code_challenge(code_verifier)

    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "iracing.profile iracing.auth",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }

    query = "&".join([f"{k}={v}" for k, v in params.items()])
    return redirect(f"{AUTH_URL}?{query}")

@app.route("/callback")
def callback():
    code = request.args.get("code")

    if not code:
        return "Error: missing authorization code", 400

    code_verifier = session.get("code_verifier")
    if not code_verifier:
        return "Error: missing PKCE code verifier in session", 400

    masked_secret = _mask_secret(CLIENT_SECRET, CLIENT_ID)

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": masked_secret,
        "code_verifier": code_verifier,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    token_response = requests.post(TOKEN_URL, data=data, headers=headers, timeout=60)

    if token_response.status_code != 200:
        return f"Error getting token: {token_response.text}", 400

    token_json = token_response.json()
    session["access_token"] = token_json["access_token"]

    return redirect(url_for("profile"))
# endregion Login

# region Funciones auxiliares
def generate_code_verifier():
    return base64.urlsafe_b64encode(os.urandom(64)).rstrip(b'=').decode('utf-8')


def generate_code_challenge(verifier):
    digest = hashlib.sha256(verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b'=').decode('utf-8')

def _mask_secret(secret: str, identifier: str) -> str:
    """
    Mask a secret (client_secret or password) using iRacing's masking algorithm.

    Args:
        secret: The secret to mask
        identifier: client_id for client_secret, username for password

    Returns:
        Base64 encoded SHA-256 hash of secret + normalized_identifier
    """
    # Normalize the identifier (trim and lowercase)
    normalized_id = identifier.strip().lower()

    # Concatenate secret with normalized identifier
    combined = f"{secret}{normalized_id}"

    hasher = hashlib.sha256()
    hasher.update(combined.encode('utf-8'))

    return base64.b64encode(hasher.digest()).decode('utf-8')
# endregion Funciones auxiliares


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000", debug=True)
