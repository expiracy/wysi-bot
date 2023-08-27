from wysibot import osu_api


class Beatmap:
    def __init__(self, id, version, difficulty_rating, max_combo, set_id):
        self.id = id
        self.version = version
        self.difficulty_rating = difficulty_rating
        self.max_combo = max_combo
        self.set_id = set_id

    @classmethod
    async def from_id(cls, beatmap_id):
        try:
            beatmap = await osu_api.beatmap(beatmap_id)
        except ValueError:
            return None

        beatmap_set = beatmap._beatmapset

        return Beatmap(beatmap_id, beatmap.version, beatmap.difficulty_rating, beatmap.max_combo, beatmap_set.id)
