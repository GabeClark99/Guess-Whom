from enum import Enum
from discord.member import Member
import random

class Game:
    def __init__(self, roles: list[Member]):
        self.players: list[Member] = []
        self.player_to_role: dict[Member, Member] = {}
        self.role_pool = roles

    def add_player(self, player: Member) -> bool:
        if player in self.players:
            return True
        self.players.append(player)
        return True
    
    def remove_player(self, player: Member) -> bool:
        try:
            self.players.remove(player)
        except ValueError:
            return False
        
        # remove dict entries where this player was a role?
        return True
    
    def get_players(self) -> list[Member]:
        return self.players
    
    def assign_roles(self) -> None:
        n_players = len(self.players)
        n_roles = len(self.role_pool)
        if n_players > n_roles:
            raise Exception(f"Number of players ({n_players}) is greater than the number of roles ({n_roles})!")
        
        random.shuffle(self.role_pool)
        roles = self.role_pool[0:n_players]
        for i in range(n_players):
            t_player = self.players[i]
            t_role = roles[i]
            self.player_to_role[t_player] = t_role
        return
    
    def get_role(self, player: Member) -> Member:
        return self.player_to_role[player]
    
    def get_board(self, player: Member) -> dict[Member, Member]:
        board = self.player_to_role.copy()
        board.pop(player, None)
        return board

    def start(self) -> None:
        if len(self.players) < 2:
            raise Exception(f"Not enough players ({len(self.players)})!")
        
        self.assign_roles()
        return
    
    def end(self) -> None:
        self.players.clear()
        self.player_to_role.clear()
        return