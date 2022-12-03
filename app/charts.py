import database
import sqlalchemy as db
from sqlalchemy import text
from matplotlib import pyplot as plt
import utils
from pprint import pprint
from datetime import date
import pathlib

def data_from_now():
    query = text("""SELECT * FROM v_from_now""")
    results = database.connection.execute(query)
    dates = []
    start_hours = []
    price = []
    for row in results:
        dates.append(row.date)
        start_hours.append(f"{row.date}-{row.start_hour}")
        price.append(row.sek_per_kwh)
    
    return dates, start_hours, price

def create_chart():
    chart_file_path = pathlib.Path(__file__).parent.joinpath("day_ahead_chart.png")
    dates, start_hours, price = data_from_now()
    x = start_hours
    y = price
    plt.xkcd()
    plt.rc('xtick', labelsize=4)
    plt.xticks(rotation=90)
    plt.bar(x, y)
    plt.title(f"Prices per kWH for {dates[0]}")
    plt.xlabel("Hour")
    plt.ylabel("Sek per kWh")
    
    plt.savefig(str(chart_file_path))
    utils.print_message(f"Created day ahead chart {chart_file_path}")
    # plt.show()
