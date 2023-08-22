from ossapi import OssapiAsync

from WYSIBot import config
from score_tracker.ScoreBeatmapSet import ScoreBeatmapSet


class ScoreBeatmap:
    def __init__(self, beatmap_id, version, difficulty_rating, max_combo):
        self.beatmap_id = beatmap_id
        self.version = version
        self.difficulty_rating = difficulty_rating
        self.max_combo = max_combo

    @staticmethod
    async def get_beatmap_and_beatmap_set(beatmap_id):
        osu_api = OssapiAsync(config["client_id"], config["client_secret"])

        beatmap = await osu_api.beatmap(beatmap_id)
        beatmap_set = beatmap._beatmapset

        try:
            mapper = (await osu_api.user(beatmap.user_id)).username
        except ValueError:
            mapper = ""

        beatmap = ScoreBeatmap(beatmap_id, beatmap.version, beatmap.difficulty_rating, beatmap.max_combo)
        beatmap_set = ScoreBeatmapSet(beatmap_set.id, beatmap_set.title, beatmap_set.artist, beatmap_set.covers.list, mapper)

        return beatmap, beatmap_set