import sqlalchemy as db

def create_database():
    metadata.create_all(engine)

engine = db.create_engine("sqlite:///electricity.db")
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

# if __name__ == "__main__":
create_database()