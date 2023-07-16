from telegram import Update
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    ContextTypes,
)
from dotenv import load_dotenv
from database import DataBase
from monitoring import ProductMonitoring
import os
import json

load_dotenv()
database = DataBase()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    thread = ProductMonitoring()
    thread.start()
    await update.message.reply_text(
        "Hello! This is Citilink Parser & Monitoring Bot.\n"
        "Here you can do multiple things, which are described above.\n"
        "Send /cancel to stop talking to me.\n\n"
    )

async def add_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: 
    if not context.args:
        await update.message.reply_text("Please, provide an URL of product after the command")
    else:
        url = context.args[0]
        database.insert_product(url)
        await update.message.reply_text("Product was successfully added!")
    
    
async def get_monitoring_products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    products = database.select_all_monitoring()
    for product in products:
        await update.message.reply_text(f"Name: {product.name}\n"
                                        f"Price: {product.price}\n"
                                        f"URL: {product.url}\n"
                                        f"History: {json.dumps(product.history, indent=4)}\n"
        )
    
async def delete_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Please, provide an URL of product after the command")
    else:
        url = context.args[0]
        database.delete_product(url)
        await update.message.reply_text("Product was successfully deleted!")
    
async def product_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Please, provide an URL of product after the command")
    else:
        url = context.args[0]
        product_history = database.select_product_history(url)
        await update.message.reply_text(json.dumps(product_history,indent=4))
    
def main():
    
    app = ApplicationBuilder().token(os.getenv('TOKEN')).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add_product", add_product))
    app.add_handler(CommandHandler("delete_product", delete_product))
    app.add_handler(CommandHandler("get_monitoring_products", get_monitoring_products))
    app.add_handler(CommandHandler("product_history", product_history))
    
    app.run_polling()

if __name__ == "__main__":
    main()