import sqlalchemy as db
from datetime import datetime
import pathlib

def create_database():
    metadata.create_all(engine)

db_file_path = pathlib.Path(__file__).parent.joinpath("electricity.db")
# engine = db.create_engine("sqlite:///electricity.db")
engine = db.create_engine(f"sqlite:///{db_file_path}")
connection = engine.connect()
metadata = db.MetaData()
day_ahead = db.Table(
        "day_ahead_electricity_prices", metadata,
        db.Column("id", db.Integer(), primary_key=True),
        db.Column("date_start_hour", db.Integer(), index=True, unique=True),
        db.Column("date", db.Date()),
        db.Column("start_hour", db.Integer()),
        db.Column("end_hour", db.Integer()),
        db.Column("sek_per_kwh", db.Float())
    )
def current_date_start_hour():
    now = datetime.now().strftime("%Y%m%d%H")
    
    return int(now)

def latest_price_data():
    query = db.select([day_ahead.columns.date, day_ahead.columns.start_hour, day_ahead.columns.end_hour, day_ahead.columns.sek_per_kwh]).where(day_ahead.columns.date_start_hour >= current_date_start_hour())
    ResultProxy = connection.execute(query)
    ResultSet = ResultProxy.fetchall()
    
    return ResultSet
    # for row in ResultSet:
    #     print(row.date, row.start_hour, row.end_hour, row.sek_per_kwh)


if __name__ == "__main__":
    # create_database()
    # print(current_date_start_hour())
    
    # query = db.select([day_ahead.columns.date, day_ahead.columns.start_hour, day_ahead.columns.end_hour, day_ahead.columns.sek_per_kwh]).where(day_ahead.columns.date_start_hour >= current_date_start_hour())
    # ResultProxy = connection.execute(query)
    # ResultSet = ResultProxy.fetchall()
    lpd = latest_price_data()
    print(lpd[0].start_hour)