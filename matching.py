import logging
import heapq
from game import Game


def match(requests, k=5):
    print(f"matching with: {requests}")
    users = list(requests.keys())
    available_games = list(set([game for user in requests for game in requests[user]]))
    game_to_index = {game: i for i, game in enumerate(available_games)}
    results = set()
    for user in requests:
        playable_games = requests[user]
        to_add = set()
        for playable_game in playable_games:
            if len(results) == 0:
                to_add.add((playable_game,))
            else:
                for result in results:
                    to_add.add(result + (playable_game,))
        results = to_add

    result_heap = []
    for result in results:
        score = 0
        game_counter = [0] * len(available_games)
        for game in result:
            game_counter[game_to_index[game]] += 1
        for i, game_count in enumerate(game_counter):
            player_order = available_games[i].players
            if game_count > 0:
                bounded_count = game_count % (max(player_order))
                if bounded_count == 0:
                    bounded_count = max(player_order)
                if bounded_count not in player_order:
                    score = -1
                    break
                else:
                    score += player_order.index(bounded_count)
        if score >= 0:
            heapq.heappush(result_heap, (score, id(result), result))
    out = []
    while k and result_heap:
        result = heapq.heappop(result_heap)
        # out.append((result[0], result[2]))
        out.append((result[0], {game: set() for game in available_games}))
        for user_idx, game in enumerate(result[2]):
            # out[-1][1][users[user_idx]] = game
            out[-1][1][game].add(users[user_idx])
        k -= 1
    print(out)
    return out


if __name__ == "__main__":
    A = Game("A", "3 2")
    B = Game("B", "3")
    C = Game("C", "2")
    D = Game("D", "2")
    requests = {
        1: {A, B},
        2: {A, C},
        3: {B},
        4: {A, B},
        5: {B, C},
        6: {A, D}
    }
    print(match(requests))
