import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

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

