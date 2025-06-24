import telebot
import easyocr
import re
import cv2
import numpy as np
from PIL import Image
import requests
from io import BytesIO

# ⛔️ Directly paste your TOKEN here for now
TOKEN = '8071817525:AAFPJfV6j-JT4hgujpli2lCPZdbwtMFLpBY'
bot = telebot.TeleBot(TOKEN)

reader = easyocr.Reader(['en'], gpu=False)

@bot.message_handler(content_types=['photo'])
def handle_image(message):
    try:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        file = requests.get(f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}")
        image = Image.open(BytesIO(file.content)).convert('RGB')
        image_np = np.array(image)
        results = reader.readtext(image_np, detail=0)

        name = ""
        number = ""
        std_class = ""

        for line in results:
            text = line.strip()

            # Number detection
            if re.search(r"\+91[-\s]?\d{10}", text) or "Mob" in text:
                number = re.findall(r"\+91[-\s]?\d{10}", text)
                number = number[0] if number else text

            # Class detection
            if any(c in text for c in ["9th", "10th", "11th", "12th"]):
                std_class = text

            # Name detection (bold/larger words filtering)
            if (
                text not in ["Google", "YouTube", "Back", "Dashboard", "Search", "PM", "AM", "Maps", "Content", "Marketing", "Leads"]
                and not text.lower().endswith("@gmail.com")
                and len(text.split()) <= 5
                and len(text) > 3
            ):
                if name == "":
                    name = text

        reply = f"""Name - {name}
Number - {number}
Class - {std_class}
Amount - 
Transaction ID / UTR -"""

        bot.reply_to(message, reply)

    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

bot.infinity_polling(timeout=60, long_polling_timeout=60)
