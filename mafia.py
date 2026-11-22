from telebot import TeleBot
import db
from time import sleep
Token = "8841044733:AAFqEBIC7a648iCeDOmrbKDzvb_61_A9v6A"

bot = TeleBot(Token)
game = False
night = True

def get_killed(night):
    if not night:
        username_killed = db.citizen_kill()
        return  f'Из города выпинали {username_killed}'
    username_killed = db.mafia_kill()
    return f'Мафия забрала жизнь {username_killed}'


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,'Чтобы начать игру, напишите "Готов играть"')

@bot.message_handler(func=lambda x: x.text.lower() == 'готов играть' and x.chat.type == 'private')
def send_text(message):
    bot.send_message(message.chat.id, f'{message.from_user.first_name} играет')
    bot.send_message(message.from_user.id, 'Вы добавлены в игру')
    db.insert_player(player_id=message.from_user.id, username=message.from_user.first_name)

@bot.message_handler(commands=['game'])
def game(message):
    global game
    players_id = db.players_idd()
    players_num = db.players_numm()
    if players_num < 4:
        bot.send_message(message.chat.id, 'Недостаточно игроков для игры')
    else:
        roles = db.roles_list
        db.player_role()
        mafia_list = db.mafia_player()
        if mafia_list != []:
            for i in mafia_list:
                bot.send_message(message.chat.id, f'{i} - мафия')
        else:
            bot.send_message(message.chat.id, "Мафии нет")
        role = db.role_player(message.from_user.id)
        bot.send_message(message.from_user.id, f"Ваша роль - {role}")
        game = True
    game_loop(message)

@bot.message_handler(commands = ['kick'])
def kick(message):
    global game, night
    if game == True:
        username = ' '.join(message.text.split(' ')[1:])
        usernames = db.all_alive()
        player = message.from_user.first_name
        if night == False:
            if not username in usernames:
                bot.send_message(message.chat.id, 'Игрок вне игры')
                return
            if player in usernames:
                voted = db.vote('citizen_vote', username, message.from_user.id)
                if voted == True:
                    bot.send_message(message.chat.id, "Ваш голос принят к сведению")
                    return   
                bot.send_message(message.chat.id, 'Права голоса на даннный момент у вас отсутствует')
                return
            bot.send_message(message.chat.id, 'Вы померли')
            return
        bot.send_message(message.chat.id, 'Сейчас ночь, все спят, незя')

@bot.message_handler(commands = ['kill'])
def kill(message):
    global game, night
    if game == True:
        username = ' '.join(message.text.split(' ')[1:])
        usernames = db.all_alive()
        player = message.from_user.first_name
        role = db.role_player(message.from_user.id)
        if role == 'mafia':
            if night == True:
                if not username in usernames:
                    bot.send_message(message.chat.id, 'Игрок вне игры')
                    return
                if player in usernames:
                    voted = db.vote('mafia_vote', username, message.from_user.id)
                    if voted == True:
                        bot.send_message(message.chat.id, "Ваш голос принят к сведению")
                        return   
                    bot.send_message(message.chat.id, 'Права голоса на даннный момент у вас отсутствует')
                    return
                bot.send_message(message.chat.id, 'Вы померли')
                return
            bot.send_message(message.chat.id, 'Ты глупи, чтобы днем убивать?')
            return
        bot.send_message(message.chat.id, 'Ты не мафия, тебе нельзя убивать')

def game_loop(message):
    global night, game
    if game == True:
        bot.send_message(message.chat.id, 'Добро Пожаловать в дурдом! Вам даётся 2 минуты на знакомство')
        sleep(5)
        while game == True:
            dead = db.all_dead()
            alive = db.all_alive()
            alive = '\n'.join(alive)
            
            if night:
                bot.send_message(message.chat.id, 'Город засыпает, просыпается мафия')
            else:
                bot.send_message(message.chat.id, "Наступает день, город просыпается")
            bot.send_message(message.chat.id, f'В игре:\n{alive}')
            winner = db.check_winner()
            if winner != None:
                bot.send_message(message.chat.id, f'Победила(-и) {winner}')
                db.clear(dead=True)
                game = False
            sleep(120)
            kill = get_killed(night)
            bot.send_message(message.chat.id, kill)
            night = not night




if __name__ == '__main__':
    bot.polling(none_stop=True)

