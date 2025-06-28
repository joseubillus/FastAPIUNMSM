from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, String, Integer, Float
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel
from typing import List

DATABASE_URL = "mysql+pymysql://root:@localhost:3306/bdapifast"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Producto(Base):
    __tablename__ = "producto"
    id = Column(String, primary_key=True, index=True)
    nom = Column(String, index=True)
    pre = Column(Float)
    rang = Column(Integer)
    img = Column(String)

Base.metadata.create_all(bind=engine)

class ProductoSchema(BaseModel):
    id: str
    nom: str
    pre: float
    rang: int
    img: str

    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()


@app.get("/productos/", response_model=List[ProductoSchema])
def listar_productos(db: Session = Depends(get_db)):
    productos = db.query(Producto).all()
    return productos

##################################################################
####----------------------Factura-----------------------------####
class Factura(Base):
    __tablename__ = "facturas"
    cod_fac = Column(String(20), primary_key=True, index=True)
    cod_ped = Column(Integer)
    id_emp = Column(Integer)
    fecha_fac = Column(String(10))  # o Date si estás usando fechas reales
    hora_fac = Column(String(8))    # o Time
    sub_fac = Column(Float)
    igv_fac = Column(Float)
    total_fac = Column(Float)
    act_fac = Column(Integer)

from datetime import date, time, timedelta

class FacturaSchema(BaseModel):
    cod_fac: str
    cod_ped: int
    id_emp: int
    fecha_fac: date    # Cambiar de str a date
    hora_fac: str      # Cambiar de str a timedelta
    sub_fac: float
    igv_fac: float
    total_fac: float
    act_fac: int

    class Config:
        from_attributes = True


@app.get("/facturas/", response_model=List[FacturaSchema])
def listar_facturas(db: Session = Depends(get_db)):
    facturas = db.query(Factura).all()
    resultado = []
    for f in facturas:
        resultado.append({
            "cod_fac": f.cod_fac,
            "cod_ped": f.cod_ped,
            "id_emp": f.id_emp,
            "fecha_fac": f.fecha_fac.isoformat(),           # convertir a string
            "hora_fac": str(f.hora_fac),                    # convertir timedelta a string
            "sub_fac": f.sub_fac,
            "igv_fac": f.igv_fac,
            "total_fac": f.total_fac,
            "act_fac": f.act_fac
        })
    return resultado


@app.get("/facturas/{cod_fac}", response_model=FacturaSchema)
def obtener_factura_por_codigo(cod_fac: str, db: Session = Depends(get_db)):
    factura = db.query(Factura).filter(Factura.cod_fac == cod_fac).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return factura


from datetime import date

from datetime import timedelta

@app.get("/facturas/fecha/{fecha_fac}", response_model=List[FacturaSchema])
def obtener_facturas_por_fecha(fecha_fac: date, db: Session = Depends(get_db)):
    facturas = db.query(Factura).filter(Factura.fecha_fac == fecha_fac).all()
    if not facturas:
        raise HTTPException(status_code=404, detail="No se encontraron facturas en esa fecha")

    resultado = []
    for f in facturas:
        # Convertir timedelta (hora_fac) a string formato HH:MM:SS
        hora_str = str(timedelta(seconds=f.hora_fac.total_seconds()))
        resultado.append({
            "cod_fac": f.cod_fac,
            "cod_ped": f.cod_ped,
            "id_emp": f.id_emp,
            "fecha_fac": f.fecha_fac.isoformat(),
            "hora_fac": hora_str,
            "sub_fac": f.sub_fac,
            "igv_fac": f.igv_fac,
            "total_fac": f.total_fac,
            "act_fac": f.act_fac
        })
    return resultado


from sqlalchemy import asc

@app.get("/facturas/anio-mes/{anio}/{mes}", response_model=List[FacturaSchema])
def obtener_facturas_por_anio_mes(anio: int, mes: int, db: Session = Depends(get_db)):
    mes_formato = f"{anio}-{mes:02d}"  # ejemplo: '2023-01'
    facturas = db.query(Factura).filter(
        Factura.fecha_fac.like(f"{mes_formato}%")
    ).order_by(asc(Factura.fecha_fac)).all()

    if not facturas:
        raise HTTPException(status_code=404, detail="No se encontraron facturas en ese mes y año")

    return [{
        "cod_fac": f.cod_fac,
        "cod_ped": f.cod_ped,
        "id_emp": f.id_emp,
        "fecha_fac": f.fecha_fac,
        "hora_fac": str(f.hora_fac),
        "sub_fac": f.sub_fac,
        "igv_fac": f.igv_fac,
        "total_fac": f.total_fac,
        "act_fac": f.act_fac
    } for f in facturas]


############################################################################################
#################------------- IA - Machine Learning-------------###########################
#Instalar xgboost
#.\.venv\Scripts\python.exe -m pip install xgboost
from sqlalchemy.orm import Session
from sqlalchemy import extract
from datetime import datetime, timedelta
import pandas as pd
import joblib
import calendar

@app.get("/prediccion/{anio}/{mes}")
def predecir_ventas_mes_siguiente(anio: int, mes: int, db: Session = Depends(get_db)):
    # 1. Consultar facturas del mes especificado
    facturas = db.query(Factura).filter(
        extract('year', Factura.fecha_fac) == anio,
        extract('month', Factura.fecha_fac) == mes
    ).all()

    if not facturas:
        raise HTTPException(status_code=404, detail="No se encontraron facturas para ese mes")

    # 2. Crear DataFrame y asegurar tipo datetime
    data = [{
        'Fecha': f.fecha_fac,
        'Ventas': f.total_fac
    } for f in facturas]

    df = pd.DataFrame(data)
    df['Fecha'] = pd.to_datetime(df['Fecha'])              # Convertir a datetime
    df = df.groupby('Fecha')['Ventas'].sum().reset_index()
    df.set_index('Fecha', inplace=True)
    df = df.sort_index()

    # 3. Crear variables de entrada
    df['dayofweek'] = df.index.dayofweek
    df['month'] = df.index.month
    df['day'] = df.index.day
    df['lag1'] = df['Ventas'].shift(1)
    df['rolling_mean7'] = df['Ventas'].rolling(window=7).mean()
    df['rolling_std7'] = df['Ventas'].rolling(window=7).std()
    df.dropna(inplace=True)

    if len(df) < 14:
        raise HTTPException(status_code=400, detail="Datos insuficientes para predecir el mes siguiente (mínimo 14 días)")

    # 4. Calcular mes siguiente
    if mes == 12:
        next_year = anio + 1
        next_month = 1
    else:
        next_year = anio
        next_month = mes + 1

    days_in_next_month = calendar.monthrange(next_year, next_month)[1]
    future_dates = pd.date_range(start=datetime(next_year, next_month, 1), periods=days_in_next_month)

    # 5. Cargar modelo entrenado
    try:
        model = joblib.load("modelo_xgboost_facturas_2023.pkl")  # Ajusta la ruta si es necesario
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Modelo no encontrado en el servidor")

    # 6. Predecir día a día
    last_known = df.copy()
    predicciones = []

    for date in future_dates:
        lag1 = last_known['Ventas'].iloc[-1]
        rolling_mean7 = last_known['Ventas'].tail(7).mean()
        rolling_std7 = last_known['Ventas'].tail(7).std()

        row = pd.DataFrame({
            'dayofweek': [date.dayofweek],
            'month': [date.month],
            'day': [date.day],
            'lag1': [lag1],
            'rolling_mean7': [rolling_mean7],
            'rolling_std7': [rolling_std7]
        }, index=[date])

        pred = model.predict(row)[0]
        predicciones.append({
            "fecha": date.strftime("%Y-%m-%d"),
            "prediccion_ventas": round(float(pred), 2)  # Conversión para evitar error de serialización
        })

        new_row = pd.DataFrame({
            'Ventas': [pred],
            'dayofweek': [date.dayofweek],
            'month': [date.month],
            'day': [date.day],
            'lag1': [lag1],
            'rolling_mean7': [rolling_mean7],
            'rolling_std7': [rolling_std7]
        }, index=[date])

        last_known = pd.concat([last_known, new_row])

    return {
        "anio": next_year,
        "mes": next_month,
        "predicciones": predicciones
    }




if __name__ == "__main__":
    import uvicorn
    #uvicorn.run(app, host="127.0.0.1", port=8000)
    uvicorn.run(app, host="192.168.0.14", port=8080)

#Instalar
#pip install PyMySQL
#pip install uvicorn