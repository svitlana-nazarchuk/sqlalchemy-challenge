# 1. import Flask
from flask import Flask, jsonify
from sqlalchemy import create_engine, func, inspect
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session


engine = create_engine("sqlite:///Data/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()
Measurement = Base.classes.measurement
Station = Base.classes.station
#session = Session(engine)

# 2. Create an app, being sure to pass __name__
app = Flask(__name__)


# Home page.
# List all routes that are available.
@app.route("/")
def welcome():
    return (f"Welcome to the Home page!</br>"
            f"Available routes:</br>"
            f"/api/v1.0/precipitation  - for precipitation</br>"
            f"/api/v1.0/stations - for the list of available stations</br>"
            f"/api/v1.0/tobs - for the list of temperature observations (tobs) for the previous year</br>"
            f"/api/v1.0/<start> - for the list of the minimum temperature, the average temperature, and the max temperature for a given start date, "
            F"after / put start date in a format yyyy-mm-dd</br>"
            f"/api/v1.0/<start>/<end> - for the list of the minimum temperature, the average temperature, and the max temperature for a given start and end dates, "
            F"after the first/ put start date, and after the second / put the end date in a format yyyy-mm-dd</br>") 


#Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
#Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    session = Session(engine)
    
    precipitation=session.query(Measurement.date, Measurement.prcp).all()
    precipitation_dict = [u._asdict() for u in precipitation]
    
    session.close()
    
    return jsonify(precipitation_dict)


#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    stations=session.query(Station.name, Station.station).all()
    stations_dict = [u._asdict() for u in stations]
    
    session.close()

    return jsonify(stations_dict)

#Query for the dates and temperature observations from a year 
#from the last data point. Return a JSON list of Temperature Observations
#  (tobs) for the previous year.
@app.route("/api/v1.0/tobs")
def temperature():
    session = Session(engine)

    last_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    #print(last_date)
    last_year=int(last_date[0][0:4])
    query_year=last_year-1
    query_date=str(query_year)+last_date[0][4:10]
    

    temperature=session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date>=query_date).all()
    temperature_dict = [u._asdict() for u in temperature]

    session.close()

    return jsonify(temperature_dict)

#Return a JSON list of the minimum temperature, the average temperature, 
# and the max temperature for a given start or start-end range.
#When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all 
# dates greater than and equal to the start date.

@app.route("/api/v1.0/<start>")
def start_date(start):

    session=Session(engine)

    last_date=session.query(Measurement.date).\
        order_by(Measurement.date.desc()).first()
    #print(last_date)
    first_date=session.query(Measurement.date).\
        order_by(Measurement.date.asc()).first()
    #print(first_date)
    if (start < first_date[0]) or (start > last_date[0]):
        return jsonify({"error": f"Date has be between {first_date[0]} and {last_date[0]}, and in a format yyyy-mm-dd"}), 404
    else:

        tmin = session.query(Measurement.tobs).filter(Measurement.date>=start).\
        order_by(Measurement.tobs.asc()).first()
        
        tmax = session.query(Measurement.tobs).filter(Measurement.date>=start).\
        order_by(Measurement.tobs.desc()).first()
        
        tavg = session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
        
        session.close()
        
        return jsonify(tmin[0], tavg[0][0], tmax[0])

#When given the start and the end date, calculate the `TMIN`, `TAVG`, 
# and `TMAX` for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session=Session(engine)

    last_date=session.query(Measurement.date).\
        order_by(Measurement.date.desc()).first()
    #print(last_date)
    first_date=session.query(Measurement.date).\
        order_by(Measurement.date.asc()).first()
    #print(first_date)
    if (start < first_date[0]) or (start > last_date[0]):
        return jsonify({"error": f"Dates has be between {first_date[0]} and {last_date[0]}, and in a format yyyy-mm-dd"}), 404
    elif (end < first_date[0]) or (end > last_date[0]):
        return jsonify({"error": f"Dates has be between {first_date[0]} and {last_date[0]}, and in a format yyyy-mm-dd"}), 404
    elif (end < start):
        return jsonify({"error": f"Start_date can not be later than end_date."}), 404
    else:
        
        tmin = session.query(Measurement.tobs).filter(Measurement.date>=start).\
        filter(Measurement.date<=end).order_by(Measurement.tobs.asc()).first()
        
        tmax = session.query(Measurement.tobs).filter(Measurement.date>=start).\
        filter(Measurement.date<=end).order_by(Measurement.tobs.desc()).first()
        
        tavg = session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date<=end).all()
        
        session.close()
        
        return jsonify(tmin[0], tavg[0][0], tmax[0])


if __name__ == "__main__":
    app.run(debug=True)
