from flask import Flask, send_file, make_response, send_from_directory
import threading
from test import do_plot
import os

app = Flask(__name__)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/', methods=['GET'])
def test():
    a = ""
    for count in countries:
        a = a + '<a href="/'+count.replace(" ","_")+'">'+count+'</a> <br>'
    return a

@app.route('/<country>', methods=['GET'])
def correlation_matrix(country):
    print("Country "+str(country))
    obj = bonds_dic[country.replace("_"," ")].curve_to_byte()

    return send_file(obj, attachment_filename="lot.png", mimetype='image/png')

@app.route('/test', methods=['GET'])
def test_test():
    bytes_obj = do_plot()

    return send_file(bytes_obj, attachment_filename='plot.png', mimetype='image/png')

def set_bonds_dic(bonds_dictionary):
    global bonds_dic
    bonds_dic = bonds_dictionary

def set_countries(cont):
    global countries
    countries = cont

def run_app():
    app.run(host='0.0.0.0', port=80)

threading.Thread(target=run_app).start()
