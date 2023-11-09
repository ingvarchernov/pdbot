import random
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dbmodel import SessionLocal, Groups, Countclick, Users
from sqlalchemy import func, and_

TOKEN: Final = '6132429387:AAHnTi3dTVSMRIEINhJhPncKs1EELTBBK1Y'
BOT_USERNAME: Final = '@Rada_Chortiv_bot'


# commands

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Нахер ти сюди зайшов? Ти хто такий?")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Що, занад-то тупий, да?")


async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я ще думаю, що сюди додати. Не їби голову!")


async def create_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    first_name = update.message.from_user.first_name
    group = update.message.chat.id

    session = SessionLocal()

    existing_user = [session.query(Users).filter_by(userid=user_id, usernames=username, firstname=first_name).first()]

    existing_group = [session.query(Groups).filter(Groups.groupid == group).first()]

    existing_znach = [record.user_ids for record in session.query(Countclick).all()]

    # створюємо нову групу, якщо групи в БД ще немає
    for groups in existing_group:
        if not groups:
            new_group = Groups(groupid=group)
            session.add(new_group)
            session.commit()
            print(f'User ({username}) was added to group ({group})')

    # створюємо нового користувача, якщо користувача в БД ще немає
    for user in existing_user:
        if not user and not user_id in existing_znach:  # якщо користувача не зареєстровано
            new_user = Users(userid=user_id, usernames=username, firstname=first_name, group_id=group)
            session.add(new_user)
            session.commit()
            print(f'User ({username}) with id ({user_id}) successfully added in {group}.')
            await update.message.reply_text(f'Тебе, підора, успішно зареєстровано ️‍🌈')
        elif user and not user_id in existing_znach:
            await update.message.reply_text(f'Даунітос, ти вже зареєстрований. Піся - відєбися!😤{group}')
            print(f'User another try to register')
        elif user_id in existing_znach:
            await update.message.reply_text(f'Десь я тебе, підора, вже бачив 🌈 {group}. Зареєструємось ще раз')
            new_user = Users(userid=user_id, usernames=username, firstname=first_name, group_id=group)
            session.add(new_user)
            session.commit()
            print(f'User ({username}) with id ({user_id}) successfully added in {group}.')
            print(f'We`ve got user, but in another group')


async def pdr_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = SessionLocal()

    user_count = session.query(func.count(Users.userid)).scalar()

    if user_count > 0:
        group_id = update.message.chat.id

        print(f'Group ID: {group_id}')

        # Якщо є користувачі, виберіть випадкового користувача
        random_user = session.query(Users).filter(Users.group_id == group_id).order_by(func.random()).first()

        print(f'Random User ID: {random_user.userid}')

        # Перевірте, чи користувач з вибраним id вже існує в таблиці Countclick
        existing_countclick_user = session.query(Countclick).filter(
            and_(Countclick.user_ids == random_user.userid, Countclick.group_id == group_id)
        ).first()

        if existing_countclick_user:
            # Якщо користувач існує, оновіть значення amountclick
            existing_countclick_user.amountclick += 1
            session.commit()

            print(
                f'Existing User: {existing_countclick_user.user_ids}, Amountclick: {existing_countclick_user.amountclick}')
            if random_user.usernames is not None:
                await update.message.reply_text(f'💖Сьогодні головного підора отримує @{random_user.usernames}. '
                                            f'\n🙈І його значення стає {existing_countclick_user.amountclick} 🏳️‍🌈🏳️‍🌈🏳️‍🌈')
            else:
                await update.message.reply_text(f'💖Сьогодні головного підора отримує {random_user.firstname}. '
                                                f'\n🙈І його значення стає {existing_countclick_user.amountclick} 🏳️‍🌈🏳️‍🌈🏳️‍🌈')
        else:
            # Якщо користувача не існує, додайте новий запис в таблицю Countclick
            countclick_data = Countclick(user_ids=random_user.userid, username=random_user.usernames,
                                         first_name=random_user.firstname, group_id=group_id, amountclick=1)
            session.add(countclick_data)
            session.commit()

            print(f'New User: {countclick_data.user_ids}, Amountclick: {countclick_data.amountclick}')

            if random_user.usernames is not None:
                await update.message.reply_text(f'💖Сьогодні головного підора отримує @{random_user.usernames}. '
                                                f'\n🙈І його значення стає {existing_countclick_user.amountclick} 🏳️‍🌈🏳️‍🌈🏳️‍🌈')
            else:
                await update.message.reply_text(f'💖Сьогодні головного підора отримує {random_user.firstname}. '
                                                f'\n🙈І його значення стає {existing_countclick_user.amountclick} 🏳️‍🌈🏳️‍🌈🏳️‍🌈')
    else:
        await update.message.reply_text('У таблиці Users немає користувачів.')


async def list_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = SessionLocal()

    chat_id = update.message.chat.id
    all_users = session.query(Countclick).filter(Countclick.group_id == chat_id).all()

    session.close()
    user_list = "\n".join(
        [f"\n🗿 Твоє пиздоцтво звучить як {user.first_name} 😈\n"
         f"🥸І маєш ти таку к-ть членів в роті: {user.amountclick} 🍆" for user in all_users])

    await update.message.reply_text(f'🔥На список кончєй невмирущих: 🔥 \n{user_list}')


# Responses

def handle_response(text: str) -> str:
    processed: str = text.lower()

    if 'ку' in processed:
        return 'Пашол нахуй!'
    if 'помощ' in processed:
        return 'Тупой. Натисни на help, овочина???'
    return 'Я твая нє панімать)'


# Обробка повідомлень надсилаємих користувачами.
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type  # отримуємо знаення типу чату, де використовується бот
    text = update.message.text
    grouptype = update.message.chat.id
    sender = update.message.from_user.first_name

    print(f'User ({sender}) in {message_type} with id ({grouptype}): {text}')

    if message_type == "supergroup" or message_type == "group":
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)
    await update.message.reply_text(response)

    print('Bot: ', response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CommandHandler('create', create_user_command))
    app.add_handler(CommandHandler('show', list_users_command))
    app.add_handler(CommandHandler('pidoras', pdr_command))

    # Message
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    # Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=1)
