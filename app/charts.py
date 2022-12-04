import sys
import database
import sqlalchemy as db
from sqlalchemy import text
from matplotlib import pyplot as plt
import utils
from pprint import pprint
from datetime import datetime
import pathlib

class DateTimeText:
    def __init__(self, start: str):
        self.start_hour = start
        self.start_date_time_obj = datetime.strptime(self.start_hour, "%Y-%m-%d-%H")
    
    def time_text(self):
        time_text = self.start_date_time_obj.strftime("%H:%M")
        
        return time_text
    
    def date_text(self):
        date_text = self.start_date_time_obj.strftime("%Y-%m-%d")
        
        return date_text
    
    def date_time_text(self):
        dt_text = self.start_date_time_obj.strftime("%Y-%m-%d %H:%M")
        
        return dt_text

    def day_month_time_text(self):
        dmt_text = self.start_date_time_obj.strftime("%-d %b %H:%M")
        
        return dmt_text

class ChartTitle(DateTimeText):
    def __init__(self, start: str, end: str):
        self.start_hour = start
        self.end_hour = end
        self.start_date_time_obj = datetime.strptime(self.start_hour, "%Y-%m-%d-%H")
        self.end_date_time_obj = datetime.strptime(self.end_hour, "%Y-%m-%d-%H")
    
    def end_date_text(self):
        mt_text = self.end_date_time_obj.strftime("%-d %b %H:%M")
        
        return mt_text

    def chart_title(self):
        title_text = f"Electricity prices between {self.day_month_time_text()} - {self.end_date_text()}"
    
        return title_text
        
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
    
    start_hours_text = []
    for start_hour in start_hours:
        ct = DateTimeText(start_hour)
        start_hours_text.append(ct.day_month_time_text())
    
    # start_hours_text = [ChartText(start_hour) for start_hour in start_hours]
        
    x = start_hours_text
    y = price
    
    chart_text = DateTimeText(start=start_hours[0])
    chart_title = ChartTitle(start=start_hours[0], end=start_hours[-1])
    
    # plt.xkcd()
    plt.rc('xtick', labelsize=8)
    plt.xticks(rotation=65)
    plt.bar(x, y)
    plt.title(chart_title.chart_title())
    plt.xlabel("Hour")
    plt.ylabel("Sek per kWh")
    plt.tight_layout()
    plt.savefig(str(chart_file_path))
    utils.print_message(f"Created day ahead chart {chart_file_path}")
    # plt.show()

if __name__ == "__main__":
    create_chart()
    # ct = ChartText("2022-12-04-1")
    # print(ct.start_date_time_obj)
    # print(ct.time_text())
    # print(ct.date_text())
    # print(ct.date_time_text())
    # print(ct.day_month_time_text())