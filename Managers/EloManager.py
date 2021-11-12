K = 30

player1 = 1450
player2 = 1550
player3 = 1675

player4 = 1400
player5 = 1600
player6 = 1550


def get_expected_score(team1, team2):
    team1total = team1["total"]
    team2total = team2["total"]
    
    ratingDiff = team2total - team1total
    denominator = 1 + 10 ** (ratingDiff / 400)
    return 1 / denominator

def get_win_elo_change(expected_score):
    return K * (1 - expected_score)

def get_loss_elo_change(expected_score):
    return K * expected_score

def get_expected_score_per_player(team1, team2):
    team2avg = int(team2["total"]) / 3
    playerGains = []

    for player in team1["players"]:
        ratingDiff = team2avg - player["mmr"]
        denominator = 1 + 10 ** (ratingDiff / 400)
        expectedScore =  1 / denominator
        playerGains.append(expectedScore)
    return playerGains


team1 = {
    "total": player1 + player2 + player3,
    "players":[
        {
            "mmr": player1
        },
        {
            "mmr": player2
        },
        {
            "mmr": player3
        },
    ]
}

team2 = {
    "total": player4 + player5 + player6,
    "players":[
        {
            "mmr": player4
        },
        {
            "mmr": player5
        },
        {
            "mmr": player6
        },
    ]
}

x = get_expected_score(team1, team2)

eloChange = round(get_win_elo_change(x), 1)

# print(f"Team 1: {team1['total']}\nTeam 2: {team2['total']}")
# print("Expected score is " + str(round(x, 3)))
# print("Elo gain is " + eloChange)

playerExpectedScoresTeam1 = get_expected_score_per_player(team1, team2)

print(f"\n===== Team 1 - {team1['total'] } (WINNER) =====")
i = 1
for score in playerExpectedScoresTeam1:
    eloChange = round(get_win_elo_change(score), 1)
    print(f"Player {i} original: {team1['players'][i - 1]['mmr']}")
    print(f"Player {i} gained: +{eloChange}\n")
    i = i + 1
print(f"Team 1 total elo: {team1['total']}")

playerExpectedScoresTeam2 = get_expected_score_per_player(team2, team1)

print(f"\n===== Team 2 - {team2['total'] } (LOSER) =====")
i = 1
for score in playerExpectedScoresTeam2:
    eloChange = round(get_win_elo_change(score), 1)
    print(f"Player {i} original: {team2['players'][i - 1]['mmr']}")
    print(f"Player {i} gained: +{eloChange}\n")
    i = i + 1
print("\n\n")
