from threading import Thread
from database import DataBase
from time import sleep

database = DataBase()


class ProductMonitoring(Thread):
    def run(self, *args, **kwargs):
        while True:
            database.update_table()
            sleep(300)