#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")

def execOnly(sql):
    '''run the sql w/o need of result'''
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()

def deleteMatches():
    """Remove all the match records from the database."""
    sql='TRUNCATE TABLE matches'
    execOnly(sql)


def deletePlayers():
    """Remove all the player records from the database."""
    sql='TRUNCATE TABLE player cascade'
    execOnly(sql)
    
def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('SELECT count(*) FROM player')
    result = cursor.fetchone() #fetchall()
    #for data in result:
    #  print(data[0], data[1], data[2], data[3])
    cnt = result[0]
    cursor.close()
    conn.close()
    return cnt

def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    cursor = conn.cursor()
    newplayer = 'INSERT INTO player (  name) VALUES (%s)'

    player1 = ( name,) #need a comma at the end for psycopg2!!
    try:
        cursor.execute(newplayer, player1)
        conn.commit()
    except:
        print('Sorry, there was a problem adding new player')
    else:
        print('Data values added!')
    cursor.close()
    conn.close()    

def execAll(sql, t=(0,)):
    '''execute sql return result template'''
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(sql, t)
    result = cursor.fetchall() #fetchall()
    #for data in result:
    #  print(data[0], data[1], data[2], data[3])
    
    cursor.close()
    conn.close()
    return result    

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    return execAll('SELECT p.id, p.name, w.win, m.matches \
                  FROM player p \
                  LEFT JOIN wincounter w \
                  ON p.id = w.id \
                  LEFT JOIN matchcounter m \
                  ON p.id = m.id \
                  ORDER BY win DESC')

def CRUD(conn, cursor, sql, p):
    '''execute sql template'''
    try:
        cursor.execute(sql,p)
        conn.commit()
    except Exception, err:
    
        print('Sorry, there was a problem CRUD: '+str(err))
    else:
        print('Data values added!')

def reportMatch(winner, loser, tie=False):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    
    conn = connect()
    cursor = conn.cursor()

    if tie:
      matches = 'INSERT INTO matches (  id_prim, id_sec, tie) VALUES (%s, %s, true)'
    else:
      matches = 'INSERT INTO matches (  id_prim, id_sec) VALUES (%s, %s)'

    wl = ( winner, loser,) #need a comma at the end for psycopg2!!
    CRUD(conn,cursor, matches, wl)
    
    cursor.close()
    conn.close()    
 
 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    result = []
    standings = playerStandings()
    # id, name, win, match =zip(*standings)
    
    # for w in range(0, max(win)+1):
    
    i = len(standings)-1
    while i > 0:
      result.append((standings[i-1][0:2]+standings[i][0:2]))
      i-=2
      
    if len(standings) %2 ==1:
        result.append((standings[0][0:2]+[-1, 'bye']))

    #import itertools
    #import pdb

    
    # for p in range(0,4):
      # kv = execAll('SELECT id, name FROM player WHERE win = %s', (p,))
      # total=len(kv)
      # pair = total / 2
      # #pdb.set_trace()
      # if  total > 1:
        # for i in range(0, pair):          
          # result.append(kv[i]+ kv[total-1-i])
      # elif total == 1: # 0
        # result.append(kv[0]+(-1, 'bye'))
      
      # kv_arr = zip(*kv)      
      # for id1, id2 in list(itertools.combinations(kv_arr[0], 2)):
        # result.append(tuple(itertools.ifilter(lambda x: x[0] == id1, kv)) + tuple(itertools.ifilter(lambda x: x[0] == id2, kv)))
    return result
    

