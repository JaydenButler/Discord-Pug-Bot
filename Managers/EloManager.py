K = 20

def get_expected_score(team1, team2):
    ratingDiff = team2 - team1
    denominator = 1 + 10 ** (ratingDiff / 400)
    return 1 / denominator

def get_elo_change(expected_score):
    return K * (1 - expected_score)

x = get_expected_score(1000, 1000)

print("Expected score is " + str(round(x, 3)))
print("Elo gain is " + str(round(get_elo_change(x), 1)))
