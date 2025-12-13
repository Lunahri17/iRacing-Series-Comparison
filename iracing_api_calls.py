import requests

BASE_URL = "https://members-ng.iracing.com/data/"
_session = requests.Session()


class IRacingUnauthorized(Exception):
    pass


def get_series(token: str) -> list[dict]:
    return __fetch_iracing_data(token, "series/seasons?include_series=true")


def get_tracks(token: str) -> list[dict]:
    return __fetch_iracing_data(token, "track/get")


def get_member_info(token: str) -> dict:
    return __fetch_iracing_data(token, "member/info")


def get_licence_info(token: str) -> list[dict]:
    return __fetch_iracing_data(token, "lookup/licenses")


def get_cars(token: str) -> list[dict]:
    return __fetch_iracing_data(token, "car/get")


def get_car_class(token: str) -> list[dict]:
    return __fetch_iracing_data(token, "carclass/get")


def __fetch_iracing_data(token: str, endpoint: str):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}{endpoint}"

    resp = _session.get(url, headers=headers, timeout=120)

    if resp.status_code == 401:
        raise IRacingUnauthorized("Token expirado o inválido")

    resp.raise_for_status()
    return __request_to_json_link(resp.json())


def __request_to_json_link(json_response: dict):
    link = json_response.get("link")
    if not link:
        raise ValueError("Respuesta de iRacing sin 'link'")

    resp = _session.get(link, timeout=120)
    resp.raise_for_status()
    return resp.json()
