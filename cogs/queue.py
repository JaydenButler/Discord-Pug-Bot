from logging import lastResort
import random


class Player():
    def __init__(self, discordID):
        self.id = discordID

class Queue():
    def __init__(self):
        self.players = []
    
    def AddPlayer(self, player):
        self.players.append(player)

    def RemovePlayer(self, player):
        self.players.remove(player)  

    def GetQueueSize(self):
        if not self.players:
            return 0;
        else:
            return len(self.players)

    def DoQueuePop(self):
        playersToAdd = self.GetQueueSize() - 1

        teamOne = Team()
        teamTwo = Team()

        lastTeamAdded = 2;

        while playersToAdd >= 0:
            num = random.randint(0, playersToAdd)
            
            currentPlayer = self.players[num]
            
            if lastTeamAdded == 2:
                teamOne.AddPlayer(currentPlayer)
                self.RemovePlayer(currentPlayer)
                lastTeamAdded = 1
            elif lastTeamAdded == 1:
                teamTwo.AddPlayer(currentPlayer)
                self.RemovePlayer(currentPlayer)
                lastTeamAdded = 2

            playersToAdd -= 1

        return [teamOne, teamTwo]

class Match():
    def __init__(self, teamOne, teamTwo):
        self.TeamOne = teamOne
        self.TeamTwo = teamTwo
        self.MatchNum = 1

class Team():
    def __init__(self):
        self.players = []

    def AddPlayer(self, player):
        self.players.append(player)

    def GetPlayers(self):
        return self.players













