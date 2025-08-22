import json
import iracing_data_transform


def save_file(name: str, data: dict) -> None:
    with open(name, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def main():
    #serie = iracing_data_transform.get_dict_of_serie(Car_Catergory.SPORTS_CAR)
    #save_file("z_test.json", serie)

    username = "local"
    password = "local&"

    series_filtered = iracing_data_transform.get_dict_of_all_series(username, password)

    series = iracing_data_transform.get_relevant_data(username, password, series_filtered)

    save_file("series.json", series)

    with open("payloads/x_car_get.json", "r", encoding="utf-8") as f:
        car_data_get = json.load(f)

    with open("payloads/x_member_info.json", "r", encoding="utf-8") as f:
        member_data = json.load(f)

    car_packages = member_data.get("car_packages", [])
    car_data_by_id = {p["package_id"]: p for p in car_data_get}

    save_file("car_data_by_id.json", car_data_by_id)

    response = []

    for car_package in car_packages:
        id_to_find = car_package.get("package_id","")
        try:
            car_data = car_data_by_id[id_to_find]
            
            id = car_data.get("package_id","")
            car_id = car_data.get("car_id","")
            car_name = car_data.get("car_name","")
            response.append({
                "package_id": id,
                "car_id": car_id,
                "car_name": car_name
            })
        except:
            response.append({
                "id_to_find": id_to_find,
                "car_id": "null",
                "car_name": "null"
            })

    save_file("output.json", response)

if __name__ == "__main__":
    main()
