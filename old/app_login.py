from flask import Flask, render_template, jsonify, request

import iracing_data_transform
from ir_types.cars_category import Car_Catergory

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('series_table.html')


@app.route('/get_series_list', methods=['POST'])
def get_series_list():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Usuario y contraseña requeridos"}), 400

    series_filtered = iracing_data_transform.get_dict_of_all_series(username, password)
    series_name = iracing_data_transform.get_onlys_series_name(username, password, series_filtered)
    return jsonify(series_name)


@app.route('/get_series_table', methods=['POST'])
def get_series_table():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Usuario y contraseña requeridos"}), 400

    series_filtered = iracing_data_transform.get_dict_of_all_series(username, password)

    series = iracing_data_transform.get_relevant_data(username, password, series_filtered)

    all_dates = sorted({sch["start_date_week"] for serie in series for sch in serie["schedules"]})

    return jsonify({"series": series, "all_dates": all_dates})
