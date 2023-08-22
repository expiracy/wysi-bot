class UserScore:
    def __init__(self, beatmap_id, mods, pp, accuracy, combo, ar, cs):
        self.beatmap_id = beatmap_id
        self.mods = mods
        self.pp = pp
        self.accuracy = accuracy
        self.combo = combo
        self.ar = ar
        self.cs = cs

    def __str__(self):
        return f"Beatmap ID: {self.beatmap_id}\nMods: {self.mods}\nPP: {self.pp}\nAccuracy: {self.accuracy}\nCombo: {self.combo}"