from datetime import datetime, timedelta, date
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta

class bond:
    def __init__(self, init_price, maturity, coupon):
        self.price = init_price
        self.maturity = maturity
        self.coupon = coupon
        self.maturity = datetime.strptime(maturity, '%d/%m/%Y')
        self.coupon_calculation()

    def coupon_calculation(self):
        self.payments = pd.DataFrame(columns=["Cupon Payment"])

        if self.coupon is not None:
            # Cupon is in percentage so divide by percentage and multyply by nominal
            self.payments.loc[self.maturity] = (self.coupon/100) * 100 + 100
            today = date.today()
            paymentDate = self.maturity

            while True:
                paymentDate = paymentDate - relativedelta(years=1)
                if paymentDate.date() < today:
                    break
                else:
                    self.payments.loc[paymentDate] = (self.coupon/100) * 100
        else:
            # No cupons just nominal:
            self.payments.loc[self.maturity] = 100


    def get_cupon(self):
        return self.coupon

    def get_payments_dataframe(self):
        return self.payments.sort_index(ascending=True)

    def get_maturity_in_years(self):
        return relativedelta(self.maturity.date(), date.today()).years + relativedelta(self.maturity.date(), date.today()).months / 12

    # Get ex-cupon price
    def get_actual_price(self):
        return self.price

    def set_actual_price(self, price):
        self.price = price

    def get_days_till_maturity(self):
        return (self.maturity - datetime.combine(date.today(), datetime.min.time())).days

    def get_maturity(self):
        return self.maturity

    # the price we have is ex-cupon compute real Price
    def get_full_price(self):
        if self.get_maturity_in_years() < 1.5:
            days_after_last_cupon = 360 - ((self.get_payments_dataframe().iloc[0].name - datetime.combine(date.today(), datetime.min.time())).days)
            accrued_interest =  days_after_last_cupon / 360 * (0 if self.coupon is None else self.coupon)
        else:
            days_after_last_cupon = 365 - ((self.get_payments_dataframe().iloc[0].name - datetime.combine(date.today(), datetime.min.time())).days)
            accrued_interest =  days_after_last_cupon / 365 * (0 if self.coupon is None else self.coupon)

        # accrued_interest is in base of 100
        # Hay excupon para t-bill?
        return self.price + accrued_interest
