-- Table definitions for the tournament project.

-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.

-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

CREATE DATABASE tournament;

CREATE TABLE players(id SERIAL PRIMARY KEY, name VARCHAR(40) NOT NULL);

CREATE TABLE matches(id SERIAL PRIMARY KEY, winner INT REFERENCES players (id), loser INT References players (id));

CREATE VIEW standings AS SELECT x.id, x.name, x.wins, o.matches FROM (SELECT p1.id, COALESCE(COUNT(m.id) ,0) AS matches FROM players AS p1  LEFT JOIN matches AS m ON p1.id = m.winner OR p1.id = m.loser GROUP BY p1.id ORDER BY p1.id) AS o JOIN (SELECT p2.id, p2.name, COALESCE(count(m.winner), 0) AS wins FROM players AS p2  LEFT JOIN matches AS m ON p2.id = m.winner GROUP BY p2.id ORDER BY p2.id DESC) AS x ON o.id = x.id ORDER BY x.wins;

CREATE VIEW parings AS SELECT a.id AS id1, a.name AS name1, b.id AS id2, b.name AS name2 FROM
            (SELECT DISTINCT * FROM (SELECT id, name, wins, row_number()
            OVER(ORDER BY wins DESC) AS row FROM standings )AS
            sta1 WHERE row % 2 =1) AS a,
            (SELECT DISTINCT * FROM (SELECT id, name, wins, row_number()
            OVER(ORDER BY wins DESC) AS row FROM standings ) AS
            sta2 WHERE row % 2 =0 ) AS b WHERE CAST (a.row AS INTEGER) =
            (CAST (b.row AS INTEGER) - 1) AND a.row < b.row ORDER BY a.wins;