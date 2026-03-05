from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

from pydantic import BaseModel

'''Определяем модели таблиц базы данных'''

class Table(Base):
    __tablename__ = 'tables'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    seats = Column(Integer, nullable=False)
    location = Column(String, unique=True, nullable=False )
    x = Column(Integer, default=0)
    y = Column(Integer, default=0)

    reservations = relationship("Reservation", back_populates="table")

class Reservation(Base):
    __tablename__ = 'reservations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_name = Column(String, nullable=False)
    table_name = Column(String, ForeignKey('tables.name'))
    # Установка текущего времени по умолчанию:
    reservation_time = Column(DateTime, nullable=False,
                              default=datetime.datetime.now())
    duration_minutes = Column(Integer, nullable=False)

    table = relationship("Table", back_populates="reservations")

class ReservationCreate(BaseModel):
    status: str          # "available", "booked", "reserved"
