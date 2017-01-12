#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import bleach


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    curr = conn.cursor()
    curr.execute("DELETE FROM matches ;")
    conn.commit()
    conn.close()

    conn = connect()
    curr = conn.cursor()
    curr.execute("UPDATE players SET wins = 0;")
    conn.commit()
    conn.close()


def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    curr = conn.cursor()
    curr.execute("DELETE FROM players ;")
    conn.commit()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    curr = conn.cursor()
    curr.execute("SELECT COUNT(*) FROM players ;")
    result = curr.fetchone()
    conn.close()
    return result[0]


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    curr = conn.cursor()
    # name = bleach.clean(name)
    curr.execute(" INSERT INTO players (name) VALUES(%s);", (name,))
    # result = curr.fetchone()
    conn.commit()
    conn.close()


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
    conn = connect()
    curr = conn.cursor()
    query = """ SELECT p.id, p.name, COALESCE(p.wins, 0),
            COALESCE(COUNT(m.id) ,0) AS matches FROM
            players AS p  LEFT JOIN matches AS m ON p.id = m.winner OR
            p.id = m.loser GROUP BY p.id ORDER BY p.wins DESC;
    """
    curr.execute(query)
    standings = [(str(row[0]), str(row[1]),
                  int(row[2]), int(row[3]))
                 for row in curr.fetchall()]
    conn.close()
    return standings


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    data = (winner, loser,)
    conn = connect()
    curr = conn.cursor()
    curr.execute(" INSERT INTO matches (winner, loser) VALUES(%s, %s);", data)
    conn.commit()
    conn.close()

    data = (winner,)
    conn = connect()
    curr = conn.cursor()
    curr.execute(
        "UPDATE players SET wins = COALESCE(wins, 0) + 1 WHERE id = %s ", data)
    # results = curr.fetchone()
    conn.commit()
    conn.close()
    # print 'results'
    # print results


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
    conn = connect()
    curr = conn.cursor()
    query = """SELECT a.id, a.name, b.id, b.name FROM
            (SELECT DISTINCT * FROM (SELECT id, name, wins, row_number()
            OVER(ORDER BY wins DESC) AS row FROM players GROUP BY id )AS
            sta1 WHERE row % 2 =1) AS a,
            (SELECT DISTINCT * FROM (SELECT id, name, wins, row_number()
            OVER(ORDER BY wins DESC) AS row FROM players GROUP BY id) AS
            sta2 WHERE row % 2 =0 ) AS b WHERE CAST (a.row AS INTEGER) =
            (CAST (b.row AS INTEGER) - 1) AND a.row < b.row ORDER BY a.wins;
    """
    curr.execute(query)
    pairings = [(str(row[0]), str(row[1]),
                 str(row[2]), str(row[3]))
                for row in curr.fetchall()]
    conn.close()
    return pairings
