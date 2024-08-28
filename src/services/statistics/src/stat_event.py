
from pandas import DataFrame


class StatEvent:
    """
    Event class with general event data and methods for init Group class
    """

    def __init__(self, legs_df: DataFrame, dispersions: dict):
        self.df = legs_df
        self.dispersions = dispersions

    def get_group_frame(self, group_name):
        """
        Extract group df from event legs df by group name.
        """
        group_indexes = [i for i in self.df.index.to_list() if f"^{group_name}" in i]
        return self.df.loc[group_indexes, :].dropna(axis=1, how='all')

    def get_group_dispersions(self, group_name: str):
        """
        Return dict with group dispersions
        """
        return self.dispersions[group_name]

    def get_sex_leg_leaderboard(self, leg: str) -> list:
        pass


