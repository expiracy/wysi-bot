import sqlite3

from score_tracker import ScoreMods
from score_tracker.ScoreBeatmap import ScoreBeatmap
from score_tracker.ScoreBeatmapSet import ScoreBeatmapSet


class Database:
    def __init__(self):
        self.connection = sqlite3.connect('score_tracker.db')
        self.cursor = self.connection.cursor()

        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                discord_id INTEGER PRIMARY KEY,
                osu_id INTEGER,
                osu_username VARCHAR(32)
            );
        ''')

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
            CREATE TABLE IF NOT Exists Tracking (
                discord_id INTEGER, 
                osu_id INTEGER,
                PRIMARY KEY (discord_id, osu_id),
                FOREIGN KEY (discord_id) REFERENCES User(discord_id),
                FOREIGN KEY (osu_id) REFERENCES User(osu_id)
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
                speed FLOAT,
                PRIMARY KEY(discord_id, beatmap_id, mods),
                FOREIGN KEY(beatmap_id) REFERENCES Beatmaps(beatmap_id),
                FOREIGN KEY(discord_id) REFERENCES Users(discord_id)
            );
        ''')

        self.connection.commit()

    def get_score(self, discord_id: int, beatmap_id: int, mods: ScoreMods):
        self.cursor.execute('''
            SELECT mods, pp, accuracy, combo, ar, cs, speed
            FROM Scores
            WHERE discord_id=? AND beatmap_id=? AND mods=?;
        ''', (discord_id, beatmap_id, int(mods)))

        return self.cursor.fetchone()

    def get_beatmap_set(self, beatmap_set_id: int):
        self.cursor.execute('''
            SELECT *
            FROM BeatmapSets
            WHERE beatmap_set_id=?;
        ''', (beatmap_set_id,))

        return self.cursor.fetchone()

    def remove_score(self, discord_id, beatmap_id, mods):
        self.cursor.execute('''
            DELETE FROM Scores
            WHERE discord_id=? AND beatmap_id=? AND mods=?;
        ''', (discord_id, beatmap_id, int(mods)))

        self.connection.commit()

    def remove_scores(self, discord_id: int):
        self.cursor.execute('''
            DELETE FROM Scores
            WHERE discord_id=?;
        ''', (discord_id,))

        self.connection.commit()

    def get_beatmap(self, beatmap_id: int):
        self.cursor.execute('''
            SELECT *
            FROM Beatmaps
            WHERE beatmap_id=?;
        ''', (beatmap_id,))

        return self.cursor.fetchone()

    def add_beatmap(self, beatmap: ScoreBeatmap, beatmap_set_id: int):
        if self.get_beatmap(beatmap.beatmap_id):
            return

        self.cursor.execute('''
            INSERT INTO Beatmaps
            VALUES (?, ?, ?, ?, ?);
        ''', (beatmap.beatmap_id, beatmap.version, beatmap.difficulty_rating, beatmap.max_combo, beatmap_set_id))

        self.connection.commit()

    def add_beatmap_set(self, beatmap_set: ScoreBeatmapSet):
        if self.get_beatmap_set(beatmap_set.beatmap_set_id):
            return

        self.cursor.execute('''
            INSERT INTO BeatmapSets
            VALUES (?, ?, ?, ?, ?);
        ''', (beatmap_set.beatmap_set_id, beatmap_set.title, beatmap_set.artist, beatmap_set.image, beatmap_set.mapper))

        self.connection.commit()

    def add_tracked(self, discord_id, osu_id):
        self.cursor.execute('''
            INSERT OR REPLACE INTO Tracking
            VALUES (?, ?);
        ''', (discord_id, osu_id))

        self.connection.commit()

    def remove_tracked(self, discord_id, osu_id):
        self.cursor.execute('''
            DELETE FROM Tracking
            WHERE discord_id=? AND osu_ID=?;
        ''', (discord_id, osu_id))

        self.connection.commit()

    def get_tracked(self, discord_id):
        self.cursor.execute('''
            SELECT osu_id FROM Tracking
            WHERE discord_id=?;
        ''', (discord_id,))

        return self.cursor.fetchall()

    def add_score(self, score, discord_id, keep_highest=False):
        existing_score = self.get_score(discord_id, score.beatmap.beatmap_id, score.mods)

        if not keep_highest or not existing_score or score.pp > existing_score[1]:
            print(f"Added score: {score.beatmap_set.title}")
            self.cursor.execute('''
                INSERT OR REPLACE INTO Scores(discord_id, beatmap_id, mods, pp, accuracy, combo, ar, cs, speed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            ''', (
            discord_id, score.beatmap.beatmap_id, int(score.mods), score.pp, score.accuracy, score.combo, score.ar,
            score.cs, score.speed))

            self.connection.commit()

            return True

        return False

    def get_scores(self, discord_id: int):
        self.cursor.execute('''
            SELECT Scores.beatmap_id, mods, pp, accuracy, combo, ar, cs, speed,
                    version, difficulty, max_combo, 
                    Beatmaps.beatmap_set_id, title, artist, image, mapper 
            FROM Scores, Beatmaps, BeatmapSets
            WHERE discord_id=? AND Scores.beatmap_id=Beatmaps.beatmap_id AND Beatmaps.beatmap_set_id=BeatmapSets.beatmap_set_id
            ORDER BY PP DESC;
        ''', (discord_id,))

        return self.cursor.fetchall()

    def get_discord_id(self, osu_username):
        self.cursor.execute('''
            SELECT discord_id FROM Users
            WHERE osu_username=?;
        ''', (osu_username,))

        return self.cursor.fetchone()

    def get_osu_username(self, discord_id):
        self.cursor.execute('''
            SELECT osu_username FROM Users
            WHERE discord_id=?;
        ''', (discord_id,))

        return self.cursor.fetchone()

    def add_user(self, discord_id, osu_id, osu_username):
        self.cursor.execute('''
            INSERT OR REPLACE INTO Users
            VALUES (?, ?, ?);
        ''', (discord_id, osu_id, osu_username))

        self.connection.commit()
