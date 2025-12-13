from flask import Flask, render_template, jsonify, request

import iracing_data_transform

app = Flask(__name__)


## Renders
@app.route('/dev')
def dev():
    return render_template('series_table_dev.html')

@app.route('/')
def home():
    return render_template('series_table.html')

@app.route('/all_dates')
def all_dates():
    return render_template('series_table_all_dates.html')

@app.route('/cars')
def all_cars():
    return render_template('cars_table.html')


## APIs
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

@app.route('/get_all_cars', methods=['POST'])
def get_all_cars():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Usuario y contraseña requeridos"}), 400

    cars = iracing_data_transform.get_all_licenced_cars(username, password)

    return jsonify({"cars": cars})


## Legacy
@app.route('/v1')
def __series_table_v1():
    return render_template('series_table_v1.html')

@app.route('/v2')
def __series_table_v2():
    return render_template('series_table_v2.html')

@app.route('/v3')
def __series_table_v3():
    return render_template('series_table_v3.html')

@app.route('/v4')
def __series_table_v4():
    return render_template('series_table_v4.html')

