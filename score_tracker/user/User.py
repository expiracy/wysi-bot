from WYSIBot import osu_api


class User:
    def __init__(self, username, id, pp, accuracy, image=""):
        self.username = username
        self.id = id
        self.pp = pp
        self.accuracy = accuracy
        self.image = image

    @staticmethod
    async def fetch_user(osu_id, session=None):
        try:
            return await osu_api.user(osu_id, mode="osu")
        except ValueError:
            return None

    def __str__(self):
        return f"[**{self.username}**](https://osu.ppy.sh/u/{self.id})"
