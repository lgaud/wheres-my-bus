from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Estimate(Base):
    __tablename__ = 'estimates'

    estimate_id = Column(Integer, primary_key=True)
    trip_id = Column(Integer, ForeignKey('trips.id'))
    stop_id = Column(Integer)
    estimate_processing_time = Column(DateTime)
    adjusted_schedule_time = Column(Integer)
    adjustment_age = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)

    trip = relationship("Trip", back_populates="estimates")

    def __repr__(self):
        return "<Estimate(trip_id='%s', stop_id='%s' estimate_processing_time='%s', adjusted_schedule_time='%s', adjustment_age='%s', latitude ='%s', longitude='%s')>" % (
            self.trip_id, self.stop_id, self.estimate_processing_time, self.adjusted_schedule_time, self.adjustment_age, self.latitude, self.longitude)


class Trip(Base):
    __tablename__ = 'trips'

    id = Column(Integer, primary_key=True)
    route = Column(String) # Routes are mostly numbers, but e.g. 86C
    route_label = Column(String)
    start_time = Column(Time)

    estimates = relationship("Estimate", order_by = Estimate.estimate_id, back_populates = "trip")

    def __repr__(self):
        return "<Trip(route='%s', route_label='%s', start_time='%s')>" % (
            self.route, self.route_label, self.start_time)


# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///ocbusdata.db')

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)