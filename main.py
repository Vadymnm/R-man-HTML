from typing import List, Type

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, init_db
from models import  Table, Reservation, ReservationCreate
from datetime import datetime, timedelta

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi import WebSocket, WebSocketDisconnect
import json, asyncio

# import os
# print("Current directory:", os.getcwd())
# print("Static folder exists:", os.path.exists("static"))
# print("index.html exists:", os.path.exists("static/index.html"))


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Инициализация базы данных
init_db()

time1 = (datetime.now())
print(time1)
time_value = time1.time()
print(f"Время: {time_value}")

# Dependency для получения сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================================================

@app.post("/tables/")
def create_table(name: str, seats: int, location: str, db: Session = Depends(get_db)):
    db_table = Table(name=name, seats=seats, location=location)
    db.add(db_table)
    db.commit()
    db.refresh(db_table)
    return db_table

# ----------------------------------------------
@app.get("/tables/")
def read_tables(skip: int = 0, limit: int = 12, db: Session = Depends(get_db)):
    tables = db.query(Table).offset(skip).limit(limit).all()
    print(tables)
    return tables

# ----------------------------------------------
@app.delete("/tables/")
def delete_tables(name, db: Session = Depends(get_db)):
    # Получаем экземпляр объекта по number
    del_table = db.query(Table).filter_by(name=name).first()
    if del_table:
        db.delete(del_table)  # Удаляем экземпляр
        db.commit()           # Фиксируем изменения
        print("Строка успешно удалена.")
    else:
        print("Объект не найден.")
        return "Объект не найден."

# =========================================================

@app.post("/reservations/")
def create_reservation(customer_name: str, table_name: str, reservation_time: datetime,
                       duration_minutes: int, db: Session = Depends(get_db)):
    ''' Enter reservation_time in following format:  YYYY-MM-DD hh:mm:ss '''
    ''' Проверка наличия таблицы заказов '''
    db_table = db.query(Reservation)
    if db_table is None:
        raise HTTPException(status_code=404, detail="Table not found")

    ''' Проверка возможности заказа выбранного  столика '''
    '''Запрос  наличия записи в таблицы по признаку  "table_name" '''
    record = db.query(Reservation).filter(Reservation.table_name == table_name).all()

    '''Проверка времени действия резервирования'''
    if record:
        for rec in record:
            print(f"table_name: {rec.table_name}, reservation_time: {rec.reservation_time}, duration_minutes: {rec.duration_minutes}")
            tbl = table_name
            res_time = reservation_time
            dur_time = duration_minutes
            print(tbl, res_time, dur_time)
        if tbl == table_name:
            print("***  Этот  столик пока  занят!!! ****")
    time_now = datetime.now()
    print(time_now)
    time_now = time_now.replace(microsecond=0)
    print(time_now)
    if record:
        if (res_time + timedelta(minutes=dur_time)) < time_now:
            print(time_now, (res_time + timedelta(minutes=dur_time)))
            print('Столик зарезервирован, но время истекло. Пожалуйста, удалите просроченный заказ и повторите!!!')
            return 'Столик зарезервирован, но время истекло. Пожалуйста, удалите просроченный заказ и повторите!!!'
        else:
            print(' == Этот  столик  пока  занят!!!!')
            return '  == Этот  столик  пока  занят!!!!'

    db_reservation = Reservation(customer_name=customer_name, table_name=table_name,
                                 reservation_time=reservation_time, duration_minutes=duration_minutes)
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

# ----------------------------------------------
@app.get("/reservations/")
def Check_reservations(skip: int = 0, limit: int = 12, db: Session = Depends(get_db)):
    time_now = datetime.now()
    time_now = time_now.replace(microsecond=0)
    print(time_now)
    reservations = db.query(Reservation).offset(skip).limit(limit).all()

    print(f"Найдено бронирований: {len(reservations)}")
    print("-" * 50)
    for i, reservation in enumerate(reservations, 1):
        print(f"{i}. ID: {reservation.id}")
        print(f"   Заказчик: {reservation.customer_name}")
        print(f"   Стол: {reservation.table_name}")
        print(f"   Дата, время: {reservation.reservation_time}")
        print(f"   Длительность: {reservation.duration_minutes}")
        print("-" * 30)

    for i, reservation in enumerate(reservations, 1):
        if (reservation.reservation_time + timedelta(minutes=reservation.duration_minutes)) < time_now:
            print(time_now, reservation.table_name, (reservation.reservation_time + timedelta(minutes=reservation.duration_minutes)))
            print('Столик зарезервирован, но время истекло.  Удаляем просроченный заказ!!!')
            del_reservations = db.query(Reservation).filter_by(table_name=reservation.table_name).first()
            if del_reservations:
                db.delete(del_reservations)  # Удаляем экземпляр
                db.commit()  # Фиксируем изменения
                print("Заказ успешно удален.")

    return reservations

# ****************************************************

# ----------------------------------------------
@app.delete("/reservations/")
def delete_reservations(table_name, db: Session = Depends(get_db)):
    # Получаем экземпляр объекта по number
    del_reservations = db.query(Reservation).filter_by(table_name=table_name).first()
    if del_reservations:
        db.delete(del_reservations)  # Удаляем экземпляр
        db.commit()  # Фиксируем изменения
        print("Заказ успешно удален.")
    else:
        print("Объект не найден.")


#   #################################################################
#   #################################################################
#   #################################################################


#@app.put("api/tables/{table_id}/reservations")
#def update_reservation( table_id: int, reservation: ReservationCreate, db: Session = Depends(get_db)):
# @app.put("/reservations/")
# def update_reservation(table_name: str, reservation: ReservationCreate, db: Session = Depends(get_db)):
#     print("Проверяем, что столик существует")
# #    table = db.query(Table).filter(table_id==table_id).first()
#     table = db.query(Table).filter(table_name == table_name).first()
#     print(table)
#     print("--------------")
#     print(f"   ID: {table.id}")
#     print(f"   Name: {table.name}")
#     print(f"   Seats: {table.seats}")
#     print(f"   Location: {table.location}")
#     print("-" * 30)
#     if not table:
#         raise HTTPException(status_code=404, detail="Table not found")
#
#     # Создаём запись о бронировании
# #    new_res = ReservationCreate(table_name == table_name)
#     new_res = ReservationCreate(table_name=table_name, status=reservation.status)
# #    new_res = Reservation(customer_name=customer_name, table_name=table_name,
# #                                 reservation_time=reservation_time, duration_minutes=duration_minutes)
#     db.add(new_res)
#     db.commit()
#     db.refresh(new_res)
#     return new_res


#   #################################################################
#   #################################################################


# --------- 1. Отдаём статику (html/css/js) ----------
app.mount("/static", StaticFiles(directory="static"), name="static")

# --------- 2. Готовим «красивый» вывод столов -------
@app.get("/api/tables-map")
def tables_map(db: Session = Depends(get_db)):
    """
    Возвращает ВСЕ столы + их текущий статус:
    free / reserved / busy. Статус вычисляется на лету.
    """
#    from datetime import datetime
#    now = datetime.utcnow()
    now = datetime.now()
    print(now)
    out = []
    for t in db.query(Table).all():
        status = "free"
        for r in t.reservations:
            print('****',now, r.table_name, r.reservation_time)
            if r.reservation_time <= now <= (r.reservation_time + timedelta(minutes=r.duration_minutes)):
                status = "busy"
                break
            if r.reservation_time > now:
                status = "reserved"
        out.append({
            "id": t.id,
            "x": t.x,          # если поля x,y нет – добавьте их в модель
            "y": t.y,
            "places": t.name,
            "status": status
        })
    return out

# --------- 3. WebSocket «live board» -----------------
clients = set()

async def broadcast(event: str, table_id: int):
    msg = json.dumps({"event": event, "table_id": table_id})
    # копия, чтобы не менять set во время итерации
    for ws in list(clients):
        try:
            await ws.send_text(msg)
        except:
            clients.discard(ws)

@app.websocket("/ws")
async def ws_endpoint(websocket):
    await websocket.accept()
    clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()  # keep-alive
    except WebSocketDisconnect:
        clients.discard(websocket)

