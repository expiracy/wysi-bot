class Mods:
    mod_order = ["HD", "DT", "NC", "HT", "HR", "FL", "EZ", "FL", "SD", "RL", "SO", "PF", "NF"]

    mod_values = {"": 0}

    for i in range(0, len(mod_order)):
        mod_values[mod_order[i]] = 1 << i

    def __init__(self, mods):
        if type(mods) == int:
            self.code = mods
            self.string = self.decode(mods)

        elif type(mods) == str:
            if mods == "No Mod" or mods == "NM":
                mods = ""

            self.string = mods
            self.code = self.encode(mods)
        else:
            self.string = ""
            self.code = 0

    def __hash__(self):
        return int(self)

    @staticmethod
    def encode(mods):
        if mods == "No Mod":
            return 0

        conditional_mods = dict(
            DT={'NC', 'HT'},
            NC={'DT', 'HT'},
            HT={'DT', 'NC'},
            SD={'PF'},
            PF={'SD'}
        )

        res = 0

        impossible = set()

        i = 0

        while i < len(mods):

            mod = mods[i: i + 2]

            if mod in impossible or mod not in Mods.mod_values:
                return -1

            if mod in conditional_mods:
                impossible = impossible.union(conditional_mods[mod])

            impossible.add(mod)

            res += Mods.mod_values[mod]

            i += 2

        return res

    @staticmethod
    def decode(code):
        res = ""
        i = 0

        while code > 0:
            if 1 & code == 1:
                res += Mods.mod_order[i]

            i += 1
            code >>= 1

        return res

    def __str__(self):
        return "No Mod" if self.string == "" else self.string

    def __int__(self):
        return self.code


if __name__ == '__main__':
    x = Mods.encode("HDDTHR")
    print(x)
    print(Mods.decode(x))
