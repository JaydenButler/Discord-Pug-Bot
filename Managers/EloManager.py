K = 30

def get_expected_score(team1, team2):

    team1total = 0
    for player in team1.players:
        team1total = team1total + player.mmr

    team2total = 0
    for player in team2.players:
        team2total = team2total + player.mmr
    
    ratingDiff = team2total - team1total
    denominator = 1 + 10 ** (ratingDiff / 400)
    return 1 / denominator

def get_win_elo_change(expected_score):
    return K * (1 - expected_score)

def get_loss_elo_change(expected_score):
    return -(K * expected_score)

def get_expected_score_per_player(player, otherTeam):
    otherTeamAvg = otherTeam

    ratingDiff = otherTeamAvg - player
    denominator = 1 + 10 ** (ratingDiff / 400)
    expectedScore =  1 / denominator
    return expectedScore