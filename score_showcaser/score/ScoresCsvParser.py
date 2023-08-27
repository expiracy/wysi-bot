import re
from difflib import SequenceMatcher
from io import StringIO

import pandas as pd
import requests

from score_showcaser.Database import Database
from score_showcaser.score.Beatmap import Beatmap
from score_showcaser.score.BeatmapSet import BeatmapSet
from score_showcaser.score.Mods import Mods
from score_showcaser.score.Score import Score
from score_showcaser.score.ScoreID import ScoreID
from score_showcaser.score.ScoreInfo import ScoreInfo
from score_showcaser.score.Scores import Scores
from wysibot import osu_api


class ScoresCsvParser:
    def __init__(self):
        pass

    def parse_mods(self, mods_string):
        split_mods_info = mods_string.split(', ')  # Allows you to put '{mods}, cs=x ar=x' in mod column

        if len(split_mods_info) == 1:
            mods, other = mods_string, ""
        else:
            mods, other = split_mods_info

        # Check for speed modifier
        if mods[-1] == 'x':
            if mods[-5].isalpha():
                speed = float(mods[-4:-1])
                mods = mods[:-4]
            else:
                speed = float(mods[-5:-1])
                mods = mods[:-5]
        else:
            speed = None

        # Check if ar and cs arg provided
        ar = re.findall("ar\d+.\d+", other)
        cs = re.findall("cs\d+.\d+", other)

        if ar:
            ar = float(ar[0][2:])
        else:
            ar = None

        if cs:
            cs = float(cs[0][2:])
        else:
            cs = None

        return Mods(mods), ar, cs, speed

    def parse_combo(self, combo_string):
        combo = re.findall('\d+', combo_string)

        if not combo:
            print(f"Error parsing combo: {combo}")

        return int(combo[0])

    def parse_difficulty(self, map_name):
        difficulty = re.findall("\[[^\]]+\]", map_name)

        if not difficulty:
            print(f"Error parsing difficulty for map: {map_name}")
            return None

        return difficulty[-1][1:-1]  # Remove [ ] around difficulty name

    async def parse_from_url(self, url, user):
        scores_list = []

        db = Database()
        response = requests.get(url)

        if not response:
            return False

        scores = pd.read_csv(StringIO(response.text))

        for row_index in range(len(scores)):
            map_name = scores['map'][row_index]

            if not map_name:
                break

            beatmaps = await osu_api.search_beatmapsets(map_name, explicit_content="show")
            beatmap_id = 0  # Defaulted to null int value

            difficulty = self.parse_difficulty(map_name)

            if not difficulty:
                continue

            combo = self.parse_combo(scores['combo'][row_index])

            if not combo:
                continue

            # Finds the beatmap from the name
            for beatmap_set in beatmaps.beatmapsets:
                beatmaps = beatmap_set.expand().beatmaps

                for beatmap in beatmaps:
                    if (beatmap.mode.value == "osu"
                            and SequenceMatcher(None, beatmap.version, difficulty).ratio() >= 0.8
                            and combo <= beatmap.max_combo):
                        beatmap_id = beatmap.id

            if not beatmap_id:
                print(f"Could not find map: {map_name}")
                continue

            mods, ar, cs, speed = self.parse_mods(scores['mods'][row_index])
            score_id = ScoreID(user.id, beatmap_id, mods)

            if db.get_score_info(score_id):
                continue

            pp = float(scores['pp'][row_index])
            accuracy = float(scores['accuracy'][row_index])

            score_info = ScoreInfo(pp, accuracy, combo, ar, cs, speed)
            beatmap = await Beatmap.from_id(beatmap_id)
            beatmap_set = await BeatmapSet.from_id(beatmap.set_id)

            score = Score(score_id, score_info, beatmap, beatmap_set)
            db.add_score(score)
            scores_list.append(score)

        return Scores(scores_list, f"Scores successfully parsed from CSV for user {user.name}")
