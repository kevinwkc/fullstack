-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.
/*
psql
create database tournament;
\c tournament;
psql 
\i tournament.sql 
*/
DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament;

drop table if exists player;
CREATE TABLE PLAYER(
id serial primary key,
name varchar(40) 
/* ,
win integer,
matches integer  --how many matches */
);

drop table if exists matches;
create table matches (
matches_id serial primary key,
id_prim integer references player (id), --always the winner
id_sec integer references player (id), --always the loser
tie boolean default false
);

drop view if exists wincounter;
-- create winscounter view which joins matches and players tables to
-- count the number of wins by player.
CREATE VIEW wincounter
AS
  SELECT player.id,
         player.name,
         COUNT(matches.id_prim) AS win
  FROM   player
         LEFT JOIN matches
                ON player.id = matches.id_prim and matches.tie = false
  GROUP  BY player.id;
  
drop view if exists matchcounter;  
CREATE VIEW matchcounter
AS
  SELECT player.id,
         player.name,
         COUNT(matches.matches_id) AS matches
  FROM   player
         LEFT JOIN matches
                ON player.id = matches.id_prim or player.id=matches.id_sec
  GROUP  BY player.id;
  