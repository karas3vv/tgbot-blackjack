import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext

# колода карт
suits = ['♥', '♦', '♣', '♠']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
deck = [{'rank': rank, 'suit': suit} for suit in suits for rank in ranks]

# функция для подсчета очков
def calculate_score(cards):
    score = 0
    aces = 0
    for card in cards:
        if card['rank'] in ['J', 'Q', 'K']:
            score += 10
        elif card['rank'] == 'A':
            score += 11
            aces += 1
        else:
            score += int(card['rank'])
    while score > 21 and aces:
        score -= 10
        aces -= 1
    return score

# начало игры
def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    context.user_data[user_id] = {
        'deck': deck.copy(),
        'player_hand': [],
        'dealer_hand': []
    }

    # перемешиваем колоду
    random.shuffle(context.user_data[user_id]['deck'])

    # раздача карт
    for _ in range(2):
        context.user_data[user_id]['player_hand'].append(context.user_data[user_id]['deck'].pop())
        context.user_data[user_id]['dealer_hand'].append(context.user_data[user_id]['deck'].pop())

    player_score = calculate_score(context.user_data[user_id]['player_hand'])

    update.message.reply_text(
        f"Ваши карты: {', '.join([f'{card['rank']}{card['suit']}' for card in context.user_data[user_id]['player_hand']])}\n"
        f"Очки: {player_score}\n\n"
        f"Карта дилера: {context.user_data[user_id]['dealer_hand'][0]['rank']}{context.user_data[user_id]['dealer_hand'][0]['suit']}\n"
        f"Очки дилера: ?"
    )

    keyboard = [
        [InlineKeyboardButton("Взять карту", callback_data='hit')],
        [InlineKeyboardButton("Достаточно", callback_data='stand')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Что будешь делать?', reply_markup=reply_markup)

# обработка кнопок
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()

    if query.data == 'hit':
        context.user_data[user_id]['player_hand'].append(context.user_data[user_id]['deck'].pop())
        player_score = calculate_score(context.user_data[user_id]['player_hand'])

        if player_score > 21:
            query.edit_message_text(f"Ваши карты: {', '.join([f'{card['rank']}{card['suit']}' for card in context.user_data[user_id]['player_hand']])}\n"
                                    f"Очки: {player_score}\n\nПеребор! Вы проиграли.")
            context.user_data[user_id] = {}
        else:
            keyboard = [
                [InlineKeyboardButton("Взять карту", callback_data='hit')],
                [InlineKeyboardButton("Достаточно", callback_data='stand')]
            ]
            query.edit_message_text(f"Ваши карты: {', '.join([f'{card['rank']}{card['suit']}' for card in context.user_data[user_id]['player_hand']])}\n"
                                    f"Очки: {player_score}\n\nКарта дилера: {context.user_data[user_id]['dealer_hand'][0]['rank']}{context.user_data[user_id]['dealer_hand'][0]['suit']}\n"
                                    f"Очки дилера: ?", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'stand':
        while calculate_score(context.user_data[user_id]['dealer_hand']) < 17:
            context.user_data[user_id]['dealer_hand'].append(context.user_data[user_id]['deck'].pop())

        player_score = calculate_score(context.user_data[user_id]['player_hand'])
        dealer_score = calculate_score(context.user_data[user_id]['dealer_hand'])

        result = "Вы выиграли!" if dealer_score > 21 or player_score > dealer_score else "Ничья!" if player_score == dealer_score else "Вы проиграли."

        query.edit_message_text(f"Ваши карты: {', '.join([f'{card['rank']}{card['suit']}' for card in context.user_data[user_id]['player_hand']])}\n"
                                f"Очки: {player_score}\n\nКарты дилера: {', '.join([f'{card['rank']}{card['suit']}' for card in context.user_data[user_id]['dealer_hand']])}\n"
                                f"Очки дилера: {dealer_score}\n\n{result}")

        context.user_data[user_id] = {}

TOKEN = "7578779316:AAFlnYQuVcYJDnEbawmNFRObrTEgc8KNq3k"

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()

if __name__ == "__main__":
    main()