from datetime import datetime, timedelta
from hashlib import sha256

import iracing_api_calls
from ir_types.cars_category import Car_Catergory


def get_onlys_series_name(username: str = "", password: str = "", data: dict = []) -> dict:
    licence_groups = __get_licence_groups(username, password)
    series = []

    for serie in data:
        serie_name = serie.get("season_name", "")
        license_group = serie.get("license_group", "")
        schedules = serie.get("schedules", [])
        category = schedules[0].get("category","idk uwu")

        series.append({
            "serie_name": serie_name,
            "licence_group": licence_groups[license_group]["group_name"],
            "category" : __get_category_human_name(category)
        })
    return series

def get_relevant_data(username: str = "", password: str = "", data: dict = []) -> dict:
    track_data_with_id = __get_track_data(username, password)
    cars_data = __get_car_data(username, password)
    car_class_data = __get_car_class_data(username, password)
    member_licensed_tracks, member_licensed_cars = __get_member_licensed_cars_and_tracks(username, password)

    licence_groups = __get_licence_groups(username, password)
    series = []

    for serie in data:
        serie_name = serie.get("season_name", "")
        license_group = serie.get("license_group", "")
        race_week = serie.get("race_week", "")
        schedules = serie.get("schedules", [])
        car_class_ids = serie.get("car_class_ids", [])
        category = schedules[0].get("category","idk uwu")

        cars = []
        for car_class_id in car_class_ids:
            cars_in_class_data = car_class_data[car_class_id]
            for car_in_class in cars_in_class_data["cars_in_class"]:
                car_id_from_car_in_class = car_in_class.get("car_id", "")
                car_data = cars_data[car_id_from_car_in_class]
                cars.append({
                    "car_class": cars_in_class_data.get("name","no lo se uwu"),
                    "car_name": car_data.get("car_name", "no lo se uwu"),
                    "car_owned": __check_member_has_licensed_car(member_licensed_cars, car_data.get("package_id",""))
                })

        schedules_new = []
        for schedule in schedules:
            race_week_num = schedule.get("race_week_num", "")
            start_date = schedule.get("start_date", "")
            track_id = schedule.get("track", {}).get("track_id", "")

            schedules_new.append({
                "race_week_num": race_week_num,
                "start_date": start_date,
                "track_id": track_data_with_id[track_id]["track_name"],
                "track_id_color": __get_color_by_track_id(str(track_id)),
                "track_owned": __check_member_has_licensed_track(member_licensed_tracks, track_id),
                "start_date_week": __get_monday(start_date)
            })

        series.append({
            "serie_name": serie_name,
            "licence_group": licence_groups[license_group]["group_name"],
            "race_week": race_week,
            "cars_ids": cars,
            "schedules": schedules_new,
            "category" : __get_category_human_name(category)
        })
    return series

def __get_category_human_name(category: str = "default") -> str:
    categorys = {
        "sports_car": "Sports Cars",
        "formula_car": "Formula",
        "oval": "Oval",
        "dirt_road": "Dirt Road",
        "dirt_oval": "Dirt Oval",
        "default": "idk uwu"
    }
    return categorys[category]


def __get_licence_groups(username: str = "", password: str = "") -> dict:
    license_groups = iracing_api_calls.get_licence_info(username, password)
    license_groups_by_id = {p["license_group"]: p for p in license_groups}
    return license_groups_by_id


def __check_member_has_licensed_track(member_licensed_tracks: dict, track_id: str) -> str:
    try:
        member_licensed_tracks[track_id]
        return "true"
    except:
        return "false"

def __check_member_has_licensed_car(member_licensed_cars: dict, car_id: str) -> str:
    try:
        member_licensed_cars[car_id]
        return "true"
    except:
        return "false"

def __get_member_licensed_cars_and_tracks(username: str = "", password: str = "") -> dict:
    member_info = iracing_api_calls.get_member_info(username, password)
    track_packages = member_info.get("track_packages", None)
    track_ids = {}
    for track_packege in track_packages:
        for content_id in track_packege["content_ids"]:
            track_ids[content_id] = content_id

    car_packages = member_info.get("car_packages", [])
    car_packages_ids = {p["package_id"]: p["package_id"] for p in car_packages}
    
    return track_ids, car_packages_ids


def __get_color_by_track_id(track_id: str):
    """
    Genera un código de color hexadecimal pastel a partir de una cadena.

    Args:
        track_id: La cadena de entrada (p. ej., un nombre de usuario, una etiqueta, un ID).

    Returns:
        Una cadena de color hexadecimal pastel (p. ej., '#E6F0F5').
    """
    # 1. Crear un hash SHA256 para obtener un valor numérico único
    hash_object = sha256(track_id.encode('utf-8'))
    # Convertir el hash hexadecimal a un número entero
    hash_as_int = int(hash_object.hexdigest(), 16)

    # 2. Manipular el número del hash para generar componentes RGB pastel
    # Los valores pastel tienden a estar en el rango alto, p. ej., de 200 a 255.
    # Usamos el operador módulo para obtener valores entre 0 y 55.
    # Luego, sumamos un valor base alto (como 200) para elevar el brillo.
    
    # Extraer componentes del hash
    # Se usan diferentes partes del hash para cada componente para mantener la variación
    r = (hash_as_int % 55) + 200
    g = ((hash_as_int // 55) % 55) + 200
    b = ((hash_as_int // (55 * 55)) % 55) + 200

    # 3. Formatear los componentes RGB en un código hexadecimal
    # Asegurar que el formato sea de 2 dígitos por componente
    hex_color = f"#{r:02X}{g:02X}{b:02X}"
    return hex_color

def __get_car_data(username: str = "", password: str = "") -> dict:
    car_data = iracing_api_calls.get_cars(username, password)
    car_data_by_id = {p["car_id"]: p for p in car_data}
    return car_data_by_id

def __get_car_class_data(username: str = "", password: str = "") -> dict:
    car_class_data = iracing_api_calls.get_car_class(username, password)
    car_class_data_by_id = {p["car_class_id"]: p for p in car_class_data}
    return car_class_data_by_id

def __get_track_data(username: str = "", password: str = "") -> dict:
    track_data = iracing_api_calls.get_tracks(username, password)
    track_data_with_id = {p["track_id"]: p for p in track_data}
    return track_data_with_id

def __get_monday(date_str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    monday = date_obj - timedelta(days=date_obj.weekday())
    return monday.strftime("%Y-%m-%d")

def get_dict_of_all_series(username: str = "", password: str = "") -> dict:
    series = iracing_api_calls.get_series(username, password)
    return series


def _get_dict_of_serie(username: str = "", password: str = "", category: Car_Catergory = Car_Catergory.SPORTS_CAR) -> dict:
    series = iracing_api_calls.get_series(username, password)
    series_filetered= []

    for serie in series:
        schedueles = serie.get("schedules", [])
        schedule = schedueles[0]
        serie_type = schedule.get("category", "")

        if serie_type == category.value:
            series_filetered.append(serie)

    return series_filetered

def _get_series_OLD() -> dict:
    series = iracing_api_calls.get_series()
    
    series_sports_car = []
    series_formula = []
    test = []

    for serie in series:
        schedueles = serie.get("schedules", [])
        schedule = schedueles[0]
        serie_type = schedule.get("category", "")

        name = serie.get("season_name", "")
        entry = {
            "name": name,
            "catergory": serie_type
        }
        test.append(entry)

        if serie_type == "sports_car":
            series_sports_car.append(serie)

        if serie_type == "formula_car":
            series_formula.append(serie)
    return series_sports_car, series_formula
