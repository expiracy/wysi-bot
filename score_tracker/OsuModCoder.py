class OsuModCoder:
    mod_order = ["HD", "DT", "NC", "HT", "HR", "FL", "EZ", "FL", "SD", "RL", "SO", "PF", "NF"]

    mod_values = dict()

    for i in range(0, len(mod_order)):
        mod_values[mod_order[i]] = 1 << i

    @staticmethod
    def encode(mods):
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

            if mod in impossible or mod not in OsuModCoder.mod_values:
                return -1

            if mod in conditional_mods:
                impossible = impossible.union(conditional_mods[mod])

            impossible.add(mod)

            res += OsuModCoder.mod_values[mod]

            i += 2

        return res

    @staticmethod
    def decode(val):
        res = ""
        i = 0

        while val > 0:
            if 1 & val == 1:
                res += OsuModCoder.mod_order[i]

            i += 1
            val >>= 1

        return res


if __name__ == '__main__':
    x = OsuModCoder.encode("HDDTHR")
    print(x)
    print(OsuModCoder.decode(x))
