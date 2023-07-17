from monitoring import ProductMonitoring
from database import DataBase
from fastapi import FastAPI
app = FastAPI()
database = DataBase()

@app.on_event("startup")
async def startup_event():
    thread = ProductMonitoring()
    thread.start()
    
@app.post("/add_product")
async def add_product_on_monitor(url):
    database.insert_product(url)

@app.get("/monitoring_products")
async def get_monitoring_products():
    return database.select_all_monitoring()

@app.delete("/delete_product")
async def delete_product(url):
    database.delete_product(url)

@app.get("/product_history")
async def get_product_history(url):
    return database.select_product_history(url)
