class UserProfile:
    def __init__(self, scores):
        self.accuracy = 0
        self.raw_pp = 0
        self.weighted_pp = 0
        self.fcs = 0

        self.calculate_stats(scores)

    def calculate_stats(self, scores):

        factor = 1
        for score_index, score in enumerate(scores):

            self.weighted_pp += score.pp * factor
            self.accuracy += score.accuracy * factor
            factor *= 0.95

            if score.accuracy > 100:
                print(score.accuracy)

            self.raw_pp += score.pp

            if score.combo == score.beatmap.max_combo:
                self.fcs += 1

        self.accuracy *= 100 / (20 * (1 - 0.95 ** len(scores)))
        self.weighted_pp = round(self.weighted_pp, 1)
        self.accuracy = round(self.accuracy / len(scores), 2)