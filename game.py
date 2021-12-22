
def init_players(players: str) -> list[int]:
    ret = []
    counts = players.split(" ")
    for count in counts[:-1]:
        ret.append(int(count))
    count_range = counts[-1].split("-")
    if len(count_range) == 1:
        ret.append(int(count_range[0]))
    else:
        range_start = int(count_range[0])
        range_end = int(count_range[1])
        inc = 1 if range_start < range_end else -1
        for i in range(range_start, range_end+inc, inc):
            if i not in ret:
                ret.append(i)
    return ret


class Game:
    def __init__(self, name: str, players: str):
        self.name = name
        self.players = init_players(players)

    def __repr__(self):
        return f"{self.name}: {self.players}"



