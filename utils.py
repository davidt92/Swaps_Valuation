import calendar

# maturity less than 1 year
def short_t_bill_interest(price, days_till_maturity, nominal=100):
    return (nominal/price - 1) * 360 / days_till_maturity


# maturity between 1 year and 18 months
def long_t_bill_interest(price, days_till_maturity, nominal=100):
    return ((nominal/price) ** (360 / days_till_maturity)) - 1

#
def bonds_interest(price, days_till_maturity, last_payment):
    return ((last_payment/price) ** (365 / days_till_maturity)) - 1

# Compute the present value of a payment
def present_value_act_365(payment_value, days, interest_rate):
    #print(interest_rate)
    return payment_value / (1 + interest_rate) ** (days/365)


def toTimestamp(d):
  return calendar.timegm(d.timetuple())
