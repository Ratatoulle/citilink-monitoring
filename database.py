from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.orm import DeclarativeBase, Session, Mapped, mapped_column, relationship
from sqlalchemy import create_engine, Integer, String
from sqlalchemy import MetaData, Table, Column
from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine.url import URL
from dataclasses import dataclass
from time import strftime, sleep
from citilink_parser import CitilinkParser, validate_url
import concurrent.futures


class Base(DeclarativeBase):
    pass


class Product(Base):

    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    price: Mapped[int] = mapped_column(Integer)
    url: Mapped[str] = mapped_column(String)
    history: Mapped[dict[str:int]] = mapped_column(JSONB)
    
    def __repr__(self):
        return f"Product(id={self.id}, name={self.name}, price={self.price}, url={self.url}, history={self.history})"


@dataclass
class DataBase:
    
    DATABASE_INFO = {
        'drivername': 'postgresql',
        'host': 'localhost',
        'port': '5432',
        'username': 'postgres',
        'password': '321123',
        'database': 'postgres',
        'query': "",
    }
    
    def __init__(self):
        self.info = self.DATABASE_INFO
        self.db_url = URL.create(**self.info)
        self.engine = create_engine(self.db_url, echo=True)
        self.session = Session(self.engine)
        self.updating_session = Session(self.engine)
     
    metadata = MetaData()
    
    products_table: Table = Table(
        "products",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String),
        Column("price", Integer),
        Column("url", String),
        Column("history", JSONB),
        extend_existing=True,
    )       
    
    def update_table(self):
        with self.updating_session as session:
            products = self.select_all_monitoring()
            urls = [product.url for product in products]
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.map(self.insert_product, urls)

    def insert_product(self, url):
        # validate_url(url)
        parser = CitilinkParser()
        data = parser.parse(url)
        product_name = data['name']
        product_price = data['price']
        current_time = strftime("%d.%m.%y|%H:%M:%S")
        product = Product(
            name=product_name,
            price=product_price,
            url=url,
            history={current_time: product_price}
        )
        select_product_stmt = (
            select(Product).where(Product.url == product.url)
        )        
        element = self.session.scalar(select_product_stmt)
        if element:
            element.history.update({current_time: product_price})
            flag_modified(element, "history")
        else:
            self.session.add(product)  
        self.session.commit()
        
    def select_all_monitoring(self):
        select_all_stmt = select(Product)
        result = self.session.scalars(select_all_stmt)
        self.session.commit()
        return result.all()
        
    def delete_product(self, url):
        delete_from_products_stmt = (
            delete(Product).
            where(Product.url == url)
        )
        self.session.execute(delete_from_products_stmt)
        self.session.commit()
        
    def select_product_history(self, url):
        select_history_stmt = (
            select(Product).where(Product.url == url)
        )
        result = self.session.scalar(select_history_stmt)
        self.session.commit()
        if result == None:
            return "No such product"
        else: 
            return result.history