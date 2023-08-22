import os
import sqlite3
import threading

from googlesearch import search
from ossapi import Beatmap

from score_tracker.OsuModCoder import OsuModCoder
from score_tracker.UserScore import UserScore
import csv


class DatabaseManager:
    def __init__(self):
        self.connection = sqlite3.connect('score_tracker.db')
        self.cursor = self.connection.cursor()

        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS BeatmapSets (
                beatmap_set_id INTEGER PRIMARY KEY,
                title VARCHAR(128),
                artist VARCHAR(128),
                image VARCHAR(255),
                mapper VARCHAR (32)
            );
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Beatmaps (
                beatmap_id INTEGER PRIMARY KEY,
                version VARCHAR(32),
                difficulty FLOAT,
                max_combo INTEGER,
                beatmap_set_id INTEGER,
                FOREIGN KEY (beatmap_set_id) REFERENCES BeatmapSets(beatmap_set_id)
            );
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Scores (
                discord_id INTEGER NOT NULL,
                beatmap_id INTEGER NOT NULL,
                mods INTEGER NOT NULL,
                pp FLOAT,
                accuracy DECIMAL(5, 2),
                combo INTEGER,
                ar FLOAT,
                cs FLOAT,
                PRIMARY KEY(discord_id, beatmap_id, mods),
                FOREIGN KEY(beatmap_id) REFERENCES Beatmaps(beatmap_id)
            );
        ''')

        self.connection.commit()

    def get_score(self, discord_id, beatmap_id, mods):
        self.cursor.execute('''
            SELECT mods, pp, accuracy, combo, ar, cs
            FROM Scores
            WHERE discord_id=? AND beatmap_id=? AND mods=?;
        ''', (discord_id, beatmap_id, mods))

        return self.cursor.fetchone()

    def get_beatmap_set(self, beatmap_set_id):
        self.cursor.execute('''
            SELECT *
            FROM BeatmapSets
            WHERE beatmap_set_id=?;
        ''', (beatmap_set_id,))

        return self.cursor.fetchone()

    def get_beatmap(self, beatmap_id):
        self.cursor.execute('''
            SELECT *
            FROM Beatmaps
            WHERE beatmap_id=?;
        ''', (beatmap_id,))

        return self.cursor.fetchone()

    def add_beatmap(self, beatmap: Beatmap):
        self.cursor.execute('''
            INSERT INTO Beatmaps
            VALUES (?, ?, ?, ?, ?);
        ''', (beatmap.id, beatmap.version, beatmap.difficulty_rating, beatmap.max_combo, beatmap._beatmapset.id))

        self.connection.commit()

    def add_beatmap_set(self, beatmap_set, mapper):
        self.cursor.execute('''
            INSERT INTO BeatmapSets
            VALUES (?, ?, ?, ?, ?);
        ''', (beatmap_set.id, beatmap_set.title, beatmap_set.artist, beatmap_set.covers.list, mapper))

        self.connection.commit()

    def add_score(self, score: UserScore, discord_id):
        print("Added score")
        self.cursor.execute('''
            INSERT OR REPLACE INTO Scores
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        ''', (discord_id, score.beatmap_id, score.mods, score.pp, score.accuracy, score.combo, score.ar, score.cs))

        self.connection.commit()

    def get_scores(self, discord_id):
        self.cursor.execute('''
            SELECT Scores.beatmap_id, mods, pp, accuracy, combo, ar, cs, 
                    version, difficulty, max_combo, 
                    Beatmaps.beatmap_set_id, title, artist, image, mapper 
            FROM Scores, Beatmaps, BeatmapSets
            WHERE discord_id=? AND Scores.beatmap_id=Beatmaps.beatmap_id AND Beatmaps.beatmap_set_id=BeatmapSets.beatmap_set_id
            ORDER BY PP DESC;
        ''', (discord_id,))

        return self.cursor.fetchall()











