import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    
    return (
        f"Available Routes:<br/><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&ltstart&gt<br/>"
        f"/api/v1.0/&ltstart&gt/&ltend&gt"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    prcp_query = session.query(Measurement.date, Measurement.prcp).filter(Measurement.prcp != 'None').filter(Measurement.date >= '2016-08-23').order_by(Measurement.date).all()
    
    all_precipitation = []
    for date, prcp in prcp_query:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations_query = session.query(Measurement.station, Station.name, Station.name, Station.name, func.count(Measurement.id).label('count')).filter(Measurement.station == Station.station).group_by(Measurement.station).order_by(func.count(Measurement.id).desc()).all()
    all_stations = list(np.ravel(stations_query))
    
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    tobs_query = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= '2016-08-18').all()
    all_tobs = list(np.ravel(tobs_query))

    return jsonify(all_tobs)

session = Session(engine)
def calc_temps(start_date, end_date):   
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

@app.route("/api/v1.0/<start>")
def start_date(start):
    end_date = session.query(func.max(Measurement.date)).all()[0][0]
    temps = calc_temps(start,end_date)
    temps_list = list(np.ravel(temps))
    
    return (
        f"Lowest Temperature: {temps_list[0]}<br/>"
        f"Average Temperature: {temps_list[1]}<br/>"
        f"Highest Temperature: {temps_list[2]}<br/>"
    )


@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):   
    temps = calc_temps(start,end)
    temps_list = list(np.ravel(temps))

    return (
        f"Lowest Temperature: {temps_list[0]}<br/>"
        f"Average Temperature: {temps_list[1]}<br/>"
        f"Highest Temperature: {temps_list[2]}<br/>"
    )

if __name__== '__main__':
    app.run(debug=True)
