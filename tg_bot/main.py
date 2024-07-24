import os
import zipfile
from zipfile import ZipFile

from telegram.ext import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ultralytics import YOLO
from PIL import Image
from responses import *

from dotenv import dotenv_values
from pathlib import Path


config = dotenv_values(".env")

TOKEN = config.get("TOKEN")
model = YOLO("ml/best.pt")


def create_dirs():
    os.mkdir('media')
    for folder in ['images', 'zips']:
        # print(folder)
        os.makedirs(os.path.join('media', folder))
        if folder == 'images':
            for version in ['annotated', 'raw']:
                os.makedirs(os.path.join('media', folder, version))


def remove_dir(directory):
    directory = Path(directory)
    for item in directory.iterdir():
        if item.is_dir():
            remove_dir(item)
        else:
            item.unlink()
    directory.rmdir()


def run_yolo(yolo, image_url, conf=0.25, iou=0.7):
    results = yolo(image_url, conf=conf, iou=iou)
    res = results[0].plot()[:, :, [2, 1, 0]]
    return Image.fromarray(res)


def start_command(update, context):
    keyboard = [
        [InlineKeyboardButton("Загрузить фотографию", callback_data='photo')],
        [InlineKeyboardButton("Загрузить zip-архив", callback_data='zip')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(responses['start'], reply_markup=reply_markup)


def button_callback(update, context):
    query = update.callback_query
    callback_data = query.data.split('|')
    action = callback_data[0]
    if action == 'photo':
        query.edit_message_text(
            text="Пожалуйста, загрузите фотографию.")
    elif action == 'zip':
        query.edit_message_text(
            text="Пожалуйста, загрузите Ваш zip-файл. Убедитесь в том, что его размер не превышает 20 МБ")


def image_handler(update, context):
    chat_id = update.message.chat_id
    file = update.message.photo[-1].get_file()

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Подождите, обработка фотографии займет несколько секунд...')

    create_dirs()
    img_path = os.path.join('media/images', 'raw', f'{file.file_unique_id}.jpg')
    file.download(img_path)
    img = run_yolo(model, img_path)
    img.save(os.path.join('media/images', 'annotated', f'{file.file_unique_id}.jpg'), format="JPEG")
    context.bot.send_photo(chat_id=chat_id, photo=open(os.path.join('media/images', 'annotated',
                                                           f'{file.file_unique_id}.jpg'), 'rb'))
    remove_dir(Path('media/'))


def zip_handler(update, context):

    create_dirs()
    chat_id = update.message.chat_id
    file = update.message.document.get_file()
    zip_path = os.path.join('media/zips', update.message.document.file_name)
    file.download(zip_path)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(os.path.join('media/images', 'raw'))

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Подождите, обработка архива может занять некоторое время...')

    raw_images = os.path.join('media', 'images', 'raw')
    raw_images = [os.path.join(raw_images, i) for i in os.listdir(raw_images)]

    for raw_image in raw_images:
        if Path(raw_image).suffix.lower() in ['.jpg', '.png', '.jpeg']:
            annotated_image = run_yolo(model, raw_image)
            annotated_image.save(os.path.join('media/images', 'annotated',
                                              os.path.basename(raw_image)), format="JPEG")

            with ZipFile('media/zips/processed.zip', 'a') as cur_zipfile:
                cur_zipfile.write(
                    os.path.join('media/images', 'annotated', os.path.basename(raw_image)),
                    os.path.basename(raw_image)
                )
    try:
        with open('media/zips/processed.zip', 'rb') as document:
            context.bot.send_document(chat_id, document)

    except FileNotFoundError:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='К сожалению, в данном архиве нет фотографий подходящего формата.')

    remove_dir(Path('media/'))


def main():
    print("Started")
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start_command))
    # dp.add_handler(CommandHandler("info", start_command))
    dp.add_handler(MessageHandler(Filters.photo, image_handler))
    dp.add_handler(MessageHandler(Filters.document.zip, zip_handler))
    dp.add_handler(CallbackQueryHandler(button_callback))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
