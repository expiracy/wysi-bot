from WYSIBot import osu_api


class BeatmapSet:
    def __init__(self, beatmap_set_id, title, artist, image, mapper):
        self.beatmap_set_id = beatmap_set_id
        self.title = title
        self.artist = artist
        self.image = image
        self.mapper = mapper

    @classmethod
    async def from_id(cls, beatmap_set_id):
        try:
            beatmap_set = await osu_api.beatmapset(beatmap_set_id)
        except ValueError:
            return None

        return BeatmapSet(beatmap_set_id, beatmap_set.title, beatmap_set.artist, beatmap_set.covers.list,
                          beatmap_set.creator)
