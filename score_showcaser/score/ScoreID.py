from score_showcaser.score.Mods import Mods


class ScoreID:
    def __init__(self, discord_id=-1, beatmap_id=-1, mods=""):
        self.discord_id = discord_id
        self.beatmap_id = beatmap_id

        if not mods:
            mods = Mods("")

        self.mods = mods
