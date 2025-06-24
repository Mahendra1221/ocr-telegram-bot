import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import pytesseract
from PIL import Image
import re
import os

TOKEN = "YOUR_BOT_TOKEN_HERE"

def extract_details(text):
    text = text.replace('\n', ' ')
    lines = text.split('\n')
    name = ""
    number = ""
    student_class = ""

    for line in lines:
        line = line.strip()
        if any(noise in line.lower() for noise in ["google", "youtube", "search", "dashboard", "maps", "pm", "am"]):
            continue
        if "@gmail" in line:
            continue

        if "+91" in line or "Mob" in line or re.search(r'\b[6-9]\d{9}\b', line):
            number_match = re.search(r'(\+91[-\s]?|Mob[:\s]?)?(\d{10})', line)
            if number_match:
                number = number_match.group(2)

        class_match = re.search(r'\b(9th|10th|11th|12th)\b', line, re.IGNORECASE)
        if class_match:
            student_class = class_match.group(1)

        if len(line) > len(name) and not any(x in line for x in [number, student_class]) and not line.isdigit():
            name = line

    return name.strip(), number.strip(), student_class.strip()

def process_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return extract_details(text)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me an image, and I’ll extract details!")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    file_path = f"{photo.file_id}.jpg"
    await file.download_to_drive(file_path)
    
    name, number, student_class = process_image(file_path)
    os.remove(file_path)
    
    message = f"Name - {name}\nNumber - {number}\nClass - {student_class}\nAmount - \nTransaction ID / UTR -"
    await update.message.reply_text(message)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()