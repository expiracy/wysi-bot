import asyncio
import os
import sqlite3

import aiohttp

from score_showcaser.score.Beatmap import Beatmap
from score_showcaser.score.BeatmapSet import BeatmapSet
from score_showcaser.score.Mods import Mods
from score_showcaser.score.Score import Score
from score_showcaser.score.ScoreID import ScoreID
from score_showcaser.score.ScoreInfo import ScoreInfo
from score_showcaser.score.Scores import Scores
from score_showcaser.user.Profile import Profile
from score_showcaser.user.TrackedUsers import TrackedUsers
from score_showcaser.user.User import User
from wysibot import osu_api


class Database:
    def __init__(self):
        db_path = os.path.join('score_showcaser', 'score_tracker.db')
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                discord_id INTEGER PRIMARY KEY,
                osu_id INTEGER
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

    def get_score_info(self, score_id: ScoreID):
        self.cursor.execute('''
            SELECT pp, accuracy, combo, ar, cs, speed
            FROM Scores
            WHERE discord_id=? AND beatmap_id=? AND mods=?;
        ''', (score_id.discord_id, score_id.beatmap_id, int(score_id.mods)))

        score_info = self.cursor.fetchone()

        if not score_info:
            return None

        return ScoreInfo(*score_info)

    def get_beatmap_set(self, beatmap_set_id: int):
        self.cursor.execute('''
            SELECT *
            FROM BeatmapSets
            WHERE beatmap_set_id=?;
        ''', (beatmap_set_id,))

        beatmap_set = self.cursor.fetchone()

        if not beatmap_set:
            return None

        return BeatmapSet(*beatmap_set)

    def get_beatmap(self, beatmap_id: int):
        self.cursor.execute('''
            SELECT beatmap_id, version, difficulty, max_combo, beatmap_set_id
            FROM Beatmaps
            WHERE beatmap_id=?;
        ''', (beatmap_id,))

        beatmap = self.cursor.fetchone()

        if not beatmap:
            return None

        return Beatmap(*beatmap)

    async def get_tracked_users(self, discord_id):
        self.cursor.execute('''
            SELECT osu_id FROM Tracking
            WHERE discord_id=?;
        ''', (discord_id,))

        tracked_user_ids = self.cursor.fetchall()

        tracked_users = []

        async with aiohttp.ClientSession() as session:
            tasks = [User.fetch_user(osu_id[0], session) for osu_id in tracked_user_ids]
            results = await asyncio.gather(*tasks)

            for user in results:
                if user:
                    tracked_users.append(
                        User(user.username, user.id, user.statistics.pp, user.statistics.hit_accuracy, user.avatar_url)
                    )

        return TrackedUsers(tracked_users)

    def get_score(self, score_id: ScoreID):
        score_info = self.get_score_info(score_id)
        beatmap = self.get_beatmap(score_id.beatmap_id)
        beatmap_set = self.get_beatmap_set(beatmap.set_id)

        if not score_info:
            return None

        return Score(score_id, score_info, beatmap, beatmap_set)

    def remove_score(self, score_id):
        self.cursor.execute('''
            DELETE FROM Scores
            WHERE discord_id=? AND beatmap_id=? AND mods=?;
        ''', (score_id.discord_id, score_id.beatmap_id, int(score_id.mods)))

        self.connection.commit()

    def remove_scores(self, discord_id: int):
        self.cursor.execute('''
            DELETE FROM Scores
            WHERE discord_id=?;
        ''', (discord_id,))

        self.connection.commit()

    def add_beatmap(self, beatmap: Beatmap):
        self.cursor.execute('''
            INSERT OR REPLACE INTO Beatmaps
            VALUES (?, ?, ?, ?, ?);
        ''', (beatmap.id, beatmap.version, beatmap.difficulty_rating, beatmap.max_combo, beatmap.set_id))

        self.connection.commit()

    def add_beatmap_set(self, beatmap_set: BeatmapSet):

        self.cursor.execute('''
            INSERT OR REPLACE INTO BeatmapSets
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

    def get_scores(self, discord_id, title="Scores", search_term=""):
        if search_term:
            self.cursor.execute('''
               SELECT Scores.beatmap_id, mods, pp, accuracy, combo, ar, cs, speed,
                       version, difficulty, max_combo, 
                       Beatmaps.beatmap_set_id, title, artist, image, mapper 
               FROM Scores, Beatmaps, BeatmapSets
               WHERE discord_id=? AND Scores.beatmap_id=Beatmaps.beatmap_id AND Beatmaps.beatmap_set_id=BeatmapSets.beatmap_set_id 
                     AND (LOWER(title) LIKE '%' || ? || '%' OR LOWER(mapper) LIKE ? || '%')
               ORDER BY PP DESC, accuracy DESC;
           ''', (discord_id, search_term, search_term))
        else:
            self.cursor.execute('''
                SELECT Scores.beatmap_id, mods, pp, accuracy, combo, ar, cs, speed,
                        version, difficulty, max_combo, 
                        Beatmaps.beatmap_set_id, title, artist, image, mapper 
                FROM Scores, Beatmaps, BeatmapSets
                WHERE discord_id=? AND Scores.beatmap_id=Beatmaps.beatmap_id AND Beatmaps.beatmap_set_id=BeatmapSets.beatmap_set_id
                ORDER BY PP DESC, accuracy DESC;
            ''', (discord_id,))

        scores = self.cursor.fetchall()

        scores = [Score(ScoreID(discord_id, beatmap_id, Mods(mods)),
                        ScoreInfo(pp, accuracy, combo, ar, cs, speed),
                        Beatmap(beatmap_id, version, difficulty, max_combo, beatmap_set_id),
                        BeatmapSet(beatmap_set_id, title, artist, image, mapper))
                  for (
                      beatmap_id, mods, pp, accuracy, combo, ar, cs, speed, version, difficulty, max_combo,
                      beatmap_set_id,
                      title, artist, image, mapper) in scores]

        return Scores(scores, title)

    def add_score(self, score: Score, keep_highest=False):
        last_score_info = self.get_score_info(score.id)

        if not (not last_score_info or not keep_highest or (keep_highest and score.info.pp > last_score_info.pp)):
            print("Score not added")
            return False

        self.cursor.execute('''
            INSERT OR REPLACE INTO Scores(discord_id, beatmap_id, mods, pp, accuracy, combo, ar, cs, speed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        ''', (
            score.id.discord_id, score.id.beatmap_id, int(score.id.mods),
            score.info.pp, score.info.accuracy, score.info.combo, score.info.ar, score.info.cs, score.info.speed
        ))
        self.connection.commit()

        self.add_beatmap(score.beatmap)
        self.add_beatmap_set(score.beatmap_set)

        # print(f"Added score: {score.beatmap_set.title} [{score.beatmap.version}]")

        return True

    async def get_discord_id(self, osu_id_or_username):
        try:
            osu_id = (await osu_api.user(osu_id_or_username, mode="osu")).id
        except ValueError:
            return None

        self.cursor.execute('''
            SELECT discord_id FROM Users
            WHERE osu_id=?;
        ''', (osu_id,))

        discord_id = self.cursor.fetchone()

        if not discord_id:
            return None

        return discord_id[0]

    def get_osu_id(self, discord_id):
        self.cursor.execute('''
            SELECT osu_id FROM Users
            WHERE discord_id=?;
        ''', (discord_id,))

        osu_id = self.cursor.fetchone()

        if not osu_id:
            return None

        return osu_id[0]

    async def get_osu_usernames(self, discord_id):
        osu_id = self.get_osu_id(discord_id)
        user = await User.fetch_user(osu_id)
        return set(user.account_history).union({user.username})

    def get_osu_username(self, discord_id):
        self.cursor.execute('''
            SELECT osu_id FROM Users
            WHERE discord_id=?;
        ''', (discord_id,))

        username = self.cursor.fetchone()

        if not username:
            return None

        return username[0]

    def add_user(self, discord_id, osu_id):
        self.cursor.execute('''
            INSERT OR REPLACE INTO Users(discord_id, osu_id)
            VALUES (?, ?);
        ''', (discord_id, osu_id))

        self.connection.commit()

    def remove_user(self, discord_id):
        self.cursor.execute('''
            DELETE FROM Users
            WHERE discord_id=?;
        ''', (discord_id,))

        self.connection.commit()

    async def get_user_profile(self, discord_id, name=""):
        osu_id = self.get_osu_id(discord_id)
        user = await User.fetch_user(osu_id)

        image = ""

        if user:
            image = user.avatar_url

        scores = self.get_scores(discord_id)
        tracked_users = await self.get_tracked_users(discord_id)

        return Profile(scores, tracked_users, image, name)

    def remove_all_tracked(self, discord_id):
        self.cursor.execute('''
            DELETE FROM Tracking
            WHERE discord_id=?;
        ''', (discord_id,))

        self.connection.commit()
