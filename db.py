import sqlite3
from random import shuffle
players_id = []
players_num = 0

db_path = r"C:\Users\lizko\рабочая папка\Telebot\mafia\db.db"


def role_player(player_id):
    global db_path
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    sql = f"SELECT role FROM players WHERE player_id = '{player_id}'"
    cur.execute(sql)
    roles = [row[0] for row in cur.fetchall()]
    role = roles[0]
    con.close()
    return role


def mafia_player():
    global db_path
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    sql = f"SELECT username FROM players WHERE role = 'mafia' AND dead = 0"
    cur.execute(sql)
    mafia_list = [row[0] for row in cur.fetchall()]
    con.close()
    return mafia_list

def citizen_player():
    global db_path
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    sql = f"SELECT username FROM players WHERE NOT role = 'mafia' AND dead = 0"
    cur.execute(sql)
    citizen_list = [row[0] for row in cur.fetchall()]
    con.close()
    return citizen_list


def insert_player(player_id, username):
    global db_path
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    sql = f"INSERT INTO players (player_id, username) VALUES ('{player_id}', '{username}')"
    cur.execute(sql)
    con.commit()
    con.close()




def players_numm():
    global db_path, players_id, players_num
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    sql = f"SELECT player_id FROM players"
    cur.execute(sql)
    players_id = [row[0] for row in cur.fetchall()]
    players_num = len(players_id)
    con.close()
    return players_num

def players_idd():
    global db_path, players_id, players_num
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    sql = f"SELECT player_id FROM players"
    cur.execute(sql)
    players_id = [row[0] for row in cur.fetchall()]
    shuffle(players_id)
    con.close()
    return players_id
    

players_num = players_numm()
players_id = players_idd()


def roles_list(players_num):
    mafia_num = 0
    roles = ['sherif', 'doctor', 'citizen', 'citizen']
    if players_num == 5 or players_num == 6:
        mafia_num = 1
    elif players_num >= 7 and players_num <= 9:
        mafia_num = 2
    elif players_num >= 10:
        mafia_num = 3
    citizen_num = players_num - (4 + mafia_num)
    for i in range(citizen_num):
        roles.append('citizen')
    for i in range(mafia_num):
        roles.append('mafia')
    return roles
        

roles = roles_list(players_num)


def player_role():
    global roles, players_id, db_path
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    for role, player_id in zip(roles, players_id):
        sql = f"UPDATE players SET role = '{role}' WHERE player_id = '{player_id}'"
        cur.execute(sql)
        con.commit()
    con.close()

def vote(type, username, player_id):
    con = sqlite3.connect(db_path)
    cur = con.cursor() 
    sql = f"SELECT username FROM players WHERE player_id = '{player_id}' and dead = '0' and voted = '0'"
    cur.execute(sql)
    player = cur.fetchone()
    if player is None:
        con.close()
        return False
    else:
        sql = f'UPDATE players SET "{type}" = "{type}" + 1 WHERE username = "{username}"'
        cur.execute(sql)
        con.commit()
        sql = f'UPDATE players SET "voted" = "voted" + 1 WHERE player_id = {player_id}'
        cur.execute(sql)
        con.commit()
        con.close()
        return True
    

def mafia_kill():
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    sql = f'SELECT MAX(mafia_vote) FROM players'
    cur.execute(sql)
    max_votes = cur.fetchone()[0]
    sql = f"SELECT COUNT(*) FROM players WHERE dead = 0 and role = 'mafia'"
    cur.execute(sql)
    mafia_alive = cur.fetchone()[0]
    username_killed = "никого"
    if max_votes == mafia_alive:
        cur.execute(f'SELECT username FROM players WHERE mafia_vote = {max_votes}')
        username_killed = cur.fetchone()[0]
        cur.execute(f'UPDATE players SET dead = 1 WHERE username = "{username_killed}"')
        con.commit()
    con.close()
    return username_killed

def citizen_kill():
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    sql = f"SELECT MAX(citizen_vote) FROM players"
    cur.execute(sql)
    max_votes = cur.fetchone()[0]
    sql = f'SELECT COUNT(*) FROM players WHERE citizen_vote = {max_votes}'
    cur.execute(sql)
    max_votes_count = cur.fetchone()[0]
    username_killed = 'никого'
    if max_votes_count == 1:
        sql = f'SELECT username FROM players WHERE citizen_vote = {max_votes}'
        cur.execute(sql)
        username_killed = cur.fetchone()[0]
        sql = f"UPDATE players SET dead = 1 WHERE username = '{username_killed}'"
        cur.execute(sql)
        con.commit()
    con.close()
    return username_killed


def all_alive():
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    sql = f"SELECT username FROM players WHERE dead = 0"
    cur.execute(sql)
    alive_list = [row[0] for row in cur.fetchall()]
    con.close()
    return alive_list

def check_winner():
    mafia_list = mafia_player()
    mafias = len(mafia_list)
    citizen_list = citizen_player()
    citizens = len(citizen_list)
    if mafias >= citizens:
        return 'Мафия'
    if mafias == 0:
        return 'Граждане'
    return

def clear(dead = False):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    sql = f"UPDATE players SET citizen_vote = 0, mafia_vote = 0, voted = 0, role = '' "
    if dead:
        sql += ', dead = 0'
    cur.execute(sql)
    con.commit()
    con.close

def all_dead():
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    sql = f"SELECT username FROM players WHERE dead = 1"
    cur.execute(sql)
    dead_list = [row[0] for row in cur.fetchall()]
    con.close()
    return dead_list