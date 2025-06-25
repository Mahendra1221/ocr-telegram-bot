import telebot
import easyocr
import cv2
import numpy as np
import re
from PIL import Image
from io import BytesIO

# 🔐 Replace with your own token
TOKEN = "8071817525:AAFPJfV6j-JT4hgujpli2lCPZdbwtMFLpBY"

bot = telebot.TeleBot(TOKEN)
reader = easyocr.Reader(['en'])

IGNORED_WORDS = ['google', 'maps', 'youtube', 'pm', 'am', 'battery', 'search', 'dashboard', 'back',
                 'filter', 'call', 'view', 'clear', 'superhot', 'hot', 'qualified', 'mid hot']
VALID_CLASSES = ['9th', '10th', '11th', '12th']

def clean_text(text):
    text = text.strip()
    text = re.sub(r'[^\w\s@+-.]', '', text)
    return text.lower()

def extract_details_from_image(img):
    image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    results = reader.readtext(image)

    name = ""
    number = ""
    class_name = ""

    possible_names = []

    for (bbox, text, prob) in results:
        text_clean = clean_text(text)

        if not text_clean or any(word in text_clean for word in IGNORED_WORDS):
            continue

        # 📍 Number detection
        if re.search(r"\+91[-\s]?\d{10}", text_clean) or "mob" in text_clean:
            number = re.findall(r"\+91[-\s]?\d{10}", text_clean)
            if number:
                number = number[0]
            continue

        # 🎓 Class detection
        if any(cls in text_clean for cls in VALID_CLASSES):
            for cls in VALID_CLASSES:
                if cls in text_clean:
                    class_name = cls
                    break
            continue

        # 📛 Name logic — ignore emails, unwanted short words
        if "@gmail" in text_clean or len(text_clean) < 3:
            continue

        # 🧠 Take all possible names for now
        possible_names.append((text, prob, bbox[0][0]))

    # 💡 Select the largest font or left-most as Name
    if possible_names:
        possible_names.sort(key=lambda x: (-x[1], x[2]))  # sort by confidence desc, then left position
        name = possible_names[0][0]

    # 🧼 Final formatting
    name = name.strip()
    number = number.strip()
    class_name = class_name.strip()

    return name, number, class_name

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    image = Image.open(BytesIO(downloaded_file))

    name, number, class_name = extract_details_from_image(image)

    # ✅ FIXED FORMAT (2 lines always blank at end)
    response = f"""Name - {name}
Number - {number}
Class - {class_name}
Amount -
Transaction ID / UTR -"""

    bot.reply_to(message, response)

print("🤖 Bot is running...")
bot.infinity_polling()
