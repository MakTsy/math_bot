import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pathlib import Path
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler


TOKEN_FILE = 'token.txt'
TOKEN = Path(TOKEN_FILE).read_text().strip()
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open("DataBase_bot").sheet1


class Data:
    def __init__(self):
        self.mainList = sheet.col_values(2)
        self.firstList = sheet.col_values(3)
        self.secondList = sheet.col_values(4)

    def search_main(self, sometext):
        chek = 0
        ind = -100
        size = 0
        for i in self.mainList:
            if i.find(sometext.lower()) > -1 and chek == 0:
                ind = self.mainList.index(i)
                size = 1
                chek = 1
            elif i == '' and chek == 1:
                size += 1
            elif i != '' and chek == 1:
                return ind, size
            else:
                pass
        return ind, size

    def search_first(self, sometext):
        chek = 0
        ind = -100
        size = 0
        for i in self.firstList:
            if i.find(sometext.lower()) > -1 and chek == 0:
                ind = self.firstList.index(i)
                size = 1
                chek = 1
            elif i == '' and chek == 1:
                size += 1
            elif i != '' and chek == 1:
                return ind, size
            else:
                pass
        return ind, size


    def search_second(self, sometext):
        for i in self.secondList:
            if i.find(sometext.lower()) > -1:
                return self.secondList.index(i)+1
        return -100


def start(update, context):
    msg = update.message
    print(msg.chat.first_name)
    msg.bot.send_message(msg.chat_id, text=f'Привет {msg.chat.first_name}, надеюсь этот бот как-то поможет тебе. '
    f'С жалобами и предложениеми пишите @maktsy', reply_markup = telegram.ReplyKeyboardMarkup([['Начать']], True))


def common(update, context):
    msg = update.message
    print(msg.chat.first_name)
    if msg.text == 'Начать':
        msg.bot.send_message(msg.chat_id, text=f'Введите полное или частичное название темы',
                             reply_markup=telegram.ReplyKeyboardRemove())
    elif msg.text.find("Все.") is 0:
        real = msg.text[4:]
        new = Data()
        indM, sizeM = new.search_main(real)
        if indM < 0:
            indF, sizeF = new.search_first(real)
            if indF < 0:
                ind = new.search_second(real)
                if ind < 0:
                    msg.bot.send_message(msg.chat_id, text=f'Произошел сбой')
                else:
                    photo = sheet.cell(ind, 5).value
                    msg.bot.send_photo(msg.chat_id, photo=photo)
            else:
                for i in range(sizeF):
                    photo = sheet.cell(indF+i+1, 5).value
                    msg.bot.send_photo(msg.chat_id, photo=photo)
        else:
            for i in range(sizeM):
                photo = sheet.cell(indM + i+1, 5).value
                msg.bot.send_photo(msg.chat_id, photo=photo)

    else:
        new = Data()

        indM, sizeM = new.search_main(msg.text)
        if indM < 0:
            print(indM, sizeM)
            indF, sizeF = new.search_first(msg.text)
            if indF < 0:
                ind = new.search_second(msg.text)
                if ind < 0:
                    msg.bot.send_message(msg.chat_id, text=f'еще не выучил')
                else:
                    photo = sheet.cell(ind, 5).value
                    msg.bot.send_photo(msg.chat_id, photo=photo)
            else:
                msg.bot.send_message(msg.chat_id, text=f'понятие оказалось довально обширным, можно выбрать тему более'
                f' узкую, а также можно показать все материаллы')
                lii = [f'Все.{sheet.cell(indF+1, 3).value}']
                for i in range(sizeF):
                    if sheet.cell(indF + i + 1, 4).value != '':
                        lii.append(f'{sheet.cell(indF + i + 1, 4).value}')
                        msg.bot.send_message(msg.chat_id, text=f'№{i + 1} {sheet.cell(indF + i + 1, 4).value}',
                                             reply_markup=telegram.ReplyKeyboardMarkup([lii], True, True))
        else:
            msg.bot.send_message(msg.chat_id, text=f'понятие оказалось довально обширным, можно выбрать тему более'
            f' узкую, а также можно показать все материаллы')
            lii = [f'Все.{sheet.cell(indM+1, 2).value}']
            for i in range(sizeM):
                if sheet.cell(indM+i+1, 3).value != '':
                    lii.append(f'{sheet.cell(indM+i+1, 3).value}')
                    msg.bot.send_message(msg.chat_id, text=f'№{i+1} {sheet.cell(indM+i+1, 3).value}',
                                         reply_markup=telegram.ReplyKeyboardMarkup([lii], True, True))


def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(None, common))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
