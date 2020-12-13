import investpy
from bonds import bonds
from bond import bond
import rest
import threading
import concurrent.futures
from threading import Thread
from datetime import datetime, timedelta, date
import time, threading


WAIT_SECONDS = 120
# pip install investpy
# pip install matplotlib
# pip install scipy

def bond_request_thread(country, results, position):
    bonds_in_country = investpy.bonds.get_bonds(country)["name"]
    bonds_list = []

    for bond_name in bonds_in_country:
        bond_data = investpy.bonds.get_bond_information(bond_name)
        #print(bond_data["Maturity Date"][0])
        #print(bond_data["Coupon"][0])
        if bond_data["Maturity Date"][0] is not None and bond_data["Price"][0] is not None and datetime.strptime(bond_data["Maturity Date"][0], '%d/%m/%Y').date() > date.today():
            if 50 < bond_data["Price"][0] and bond_data["Price"][0] < 150:
                bonds_list.append(bond(bond_data["Price"][0], bond_data["Maturity Date"][0], bond_data["Coupon"][0]))

    results[position] = bonds_list


def main():
    bonds_dic = {}
    rest.set_bonds_dic(bonds_dic)
    list_countries_with_bonds = investpy.bonds.get_bond_countries()
    # list_countries_with_bonds = ["germany"] # only for testing purposes

    rest.set_countries(list_countries_with_bonds)
    i = 0
    threads = [None] * len(list_countries_with_bonds)
    results = [None] * len(list_countries_with_bonds)

    for country in list_countries_with_bonds:
        threads[i] = Thread(target=bond_request_thread, args=(country, results, i))
        threads[i].start()
        i = i + 1

    # Wait for all the threads to finish the task
    for j in range(len(threads)):
        threads[j].join()

    print("Received all Bonds")

    for i in range(len(results)):
        bonds_dic[list_countries_with_bonds[i]] = bonds(results[i], list_countries_with_bonds[i])
        bonds_dic[list_countries_with_bonds[i]].calculate_curve()

    flat_list = [item for sublist in results for item in sublist]
    bonds_dic["world"] = bonds(flat_list, "world")
    bonds_dic["world"].calculate_curve()
    threading.Timer(WAIT_SECONDS, main).start()
        #bonds_dic[country].plot_curve()

if __name__ == "__main__":
    print ("Starting Curve Program")
    main()
    print("APP STARTED")
