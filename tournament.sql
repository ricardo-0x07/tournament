-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

CREATE DATABASE tournament;

CREATE TABLE players(id SERIAL PRIMARY KEY, name VARCHAR(40) NOT NULL, wins INT NULL);

CREATE TABLE matches(id SERIAL PRIMARY KEY, winner INT REFERENCES players (id), winner_score INT NULL, loser INT References players (id), loser_score INT NULL);
