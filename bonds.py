import matplotlib.pyplot as plt
from datetime import datetime, timedelta, date
from scipy import interpolate
import utils
import bond
from interest_rate import interest_rate
import matplotlib.image as mpimg
import io
from dateutil.relativedelta import relativedelta
from scipy.interpolate import CubicSpline
import numbers
import pandas as pd
import numpy as np
from matplotlib.ticker import FormatStrFormatter


class bonds:
    def __init__(self, bond_list, country):
        self.bond_list = bond_list
        self.bond_list.sort(key = lambda x : x.get_maturity_in_years(), reverse = False)
        self.interest_rate_list = []
        self.country = country

    def calculate_curve(self):
        self.start_time = datetime.now().strftime("%I:%M %p on %d - %B - %Y")
        # First, sort the bonds by maturity
        self.bond_list.sort(key = lambda x : x.get_maturity_in_years(), reverse = False)
        # Second apply boostrap method to calculate interest rates

        for bond in self.bond_list:

            if bond.get_cupon() is None:

                if bond.get_maturity_in_years() < 1:
                    # T-bill (emision with no cupons)
                    interest = utils.short_t_bill_interest(bond.get_full_price(), bond.get_days_till_maturity())
                    self.interest_rate_list.append(interest_rate(interest, bond.get_maturity()))

                else:
                    # T-bill (emision with no cupons)
                    interest = utils.long_t_bill_interest(bond.get_full_price(), bond.get_days_till_maturity())
                    self.interest_rate_list.append(interest_rate(interest, bond.get_maturity()))

            else:
                #print("Complex bond")
                full_price = bond.get_full_price()
                # Iterate over all cupons except last one
                for cupon_payment_date, cupon in bond.get_payments_dataframe().iloc[:-1,:].iterrows():
                    cupon_value = cupon["Cupon Payment"]
                    days_count = (cupon_payment_date - datetime.combine(date.today(), datetime.min.time())).days
                    interest = self.get_interest_rate(cupon_payment_date)
                    cupon_present_value = utils.present_value_act_365(cupon_value, days_count, interest)
                    full_price = full_price - cupon_present_value

                last_payment = bond.get_payments_dataframe().iloc[-1,:]["Cupon Payment"]
                interest = utils.bonds_interest(full_price, bond.get_days_till_maturity(), last_payment)
                self.interest_rate_list.append(interest_rate(interest, bond.get_maturity()))

            self.interpolate()


    def interpolate(self):
        self.interest_rate_list.sort(key = lambda x : utils.toTimestamp(x.maturity), reverse = False)
        interest = [element.interest for element in self.interest_rate_list]
        maturity = [utils.toTimestamp(element.maturity) for element in self.interest_rate_list]

        new_interest=[]
        new_maturity=[]

        for int, mat in zip (interest, maturity):
            if isinstance(int, numbers.Number) and isinstance(mat, numbers.Number):
                if np.isfinite(int) and np.isfinite(mat) and not mat in new_maturity:
                    new_interest.append(int)
                    new_maturity.append(mat)
        #print(interest)
        if len(new_interest) > 1:
            self.interpolation = CubicSpline(new_maturity, new_interest)

    def get_interest_rate(self, date):
        #print(date)
        #print("Date type "+str(type(date.to_pydatetime())))
        #print(self.interest_rate_list[0].maturity)
        if hasattr(self, "interpolation"):
            return self.interpolation(utils.toTimestamp(date.to_pydatetime()))
        else:
            return 0

    def plot_curve(self):
        interest = [element.interest for element in self.interest_rate_list]
        maturity = [(element.maturity - datetime.combine(date.today(), datetime.min.time())).days / 365 for element in self.interest_rate_list]
        #print(interest)
        plt.plot(maturity, interest)
        plt.show()
        plt.title(self.start_time)

    #def curve_to_byte(self):
        # interest = [element.interest for element in self.interest_rate_list]
        # maturity = [(element.maturity - datetime.combine(date.today(), datetime.min.time())).days / 365 for element in self.interest_rate_list]
        # plt.plot(maturity, interest)
        # bytes_image = io.BytesIO()
        # plt.plot(maturity, interest)
        # plt.savefig(bytes_image, format='png')
        # bytes_image.seek(0)
        # return bytes_image

    def curve_to_byte(self, resolution=500):
        # """Return filename of plot of the damped_vibration function."""
        # interest = [element.interest for element in self.interest_rate_list]
        # maturity = [(element.maturity - datetime.combine(date.today(), datetime.min.time())).days / 365 for element in self.interest_rate_list]

        start = date.today()
        self.interest_rate_list.sort(key = lambda x : utils.toTimestamp(x.maturity), reverse = False)
        end = self.interest_rate_list[-1].maturity
        maturity = pd.date_range(start, end, 1000)
        interest = list(map(lambda x:  self.get_interest_rate(x) * 100, maturity))

        mat = list(map(lambda x: (x - datetime.combine(date.today(), datetime.min.time())).days/365, maturity))

        bytes_image = None

        plt.clf()
        #plt.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        plt.plot(mat, interest)
        plt.ylabel("Interest rate (%)")
        plt.xlabel("Maturity in years")
        plt.title("Country: "+str(self.country).capitalize() +", Calibration time: "+ str(self.start_time))

        # Make Matplotlib write to BytesIO file object and grab
        # return the object's string
        bytes_image = io.BytesIO()
        plt.savefig(bytes_image, format='png')
        bytes_image.seek(0)
        return bytes_image
