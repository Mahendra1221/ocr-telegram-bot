import telebot
import easyocr
import re
from PIL import Image
import numpy as np
import io

TOKEN = "8071817525:AAFPJfV6j-JT4hgujpli2lCPZdbwtMFLpBY"
bot = telebot.TeleBot(TOKEN)
reader = easyocr.Reader(['en'])

# Smart Extraction Logic
def extract_details(texts):
    name, number, cls = "", "", ""
    
    # Words to ignore in name
    skip_words = ["google", "maps", "youtube", "search", "dashboard", "back", "am", "pm", "converse", "clear filters", "content", "marketing", "leads", "superhot", "hot", "cold", "qualified"]

    for t in texts:
        t_clean = t.strip()

        # Skip unwanted lines
        if any(word in t_clean.lower() for word in skip_words):
            continue
        if "@gmail" in t_clean or ".com" in t_clean:
            continue
        
        # Name Extraction: Take largest good quality text first
        if not name and t_clean[0].isalpha() and len(t_clean.split()) <= 5:
            name = t_clean

        # Number Extraction
        if not number and re.search(r"(\+91[-\s]?[6-9]\d{9})", t_clean):
            number = re.search(r"(\+91[-\s]?[6-9]\d{9})", t_clean).group(1)

        # Class Extraction
        if not cls and re.search(r"\b(9th|10th|11th|12th)\b", t_clean):
            cls = re.search(r"\b(9th|10th|11th|12th)\b", t_clean).group(1)

    # Final Output
    return f"Name - {name}\nNumber - {number}\nClass - {cls}\nAmount - \nTransaction ID / UTR -"

# Handler for photo/document
@bot.message_handler(content_types=['photo', 'document'])
def handle_image(message):
    try:
        file_id = message.photo[-1].file_id if message.photo else message.document.file_id
        file_info = bot.get_file(file_id)
        file = bot.download_file(file_info.file_path)

        image = Image.open(io.BytesIO(file)).convert("RGB")
        img_np = np.array(image)
        img_cv = img_np[:, :, ::-1].copy()

        result = reader.readtext(img_cv, detail=0)
        output = extract_details(result)

        bot.reply_to(message, output)

    except Exception as e:
        bot.reply_to(message, "Error occurred: " + str(e))

# Start the bot
bot.polling()
