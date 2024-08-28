import pandas as pd
from pandas import Series, Timedelta

from src.services.results.src.res_group import ResGroup


class ResRunner:
    """
    Class for one runner on certain event. Can calculate personal statistics on event
    """

    def __init__(self, name: str, group: ResGroup):
        self.name = f"{name.upper()}^{group.name}"
        self.group = group
        self.course = group.get_runner_course(runner=self.name)
        self.df = group.get_runner_data(runner=self.name, course=self.course)
        self.result = group.df.loc[self.name, "RES"]

    def calc_course_general_time(self) -> Series:
        """
        Calculating general times on course by sum leg times.
        Include cases when part of legs is missing.
        """

        # Check if some legs are missed
        timecut_points = [n for n, value in enumerate(self.df) if value is pd.NaT]

        # if no missed legs timecut point is end of course index
        if not timecut_points:
            timecut_points = [len(self.course)]

        general_times = {}
        for n, leg in enumerate(self.course):
            # iterate while first missed point
            if n < timecut_points[0]:
                general_times.setdefault(leg, self.df[:n + 1].sum())

            # fill missed part by void values
            elif timecut_points[0] <= n <= timecut_points[-1]:
                general_times.setdefault(leg, pd.NaT)

            # After missed part calculate general time from result backwards to point
            elif n > timecut_points[-1]:
                general_times.setdefault(leg, self.result - self.df[n + 1:].sum())

        return Series(general_times)

    def get_splits(self) -> Series:
        """
        Get personal splits on legs
        """
        return self.df

    # Event methods
    def calc_leg_backlog(self, leg) -> Timedelta:
        """
        Calculate backlog on leg for certain user between all athlets in provided dataframe
        """
        # find user and leader splits
        user_split = self.df.loc[self.name, leg]
        leader_board = self.group.get_leg_leaderboard(leg)

        # If user leg are missed
        if user_split is pd.NaT:
            return pd.NaT

        # If only user on leg
        if user_split != pd.NaT and len(leader_board) == 1:
            return user_split

        # Common case when some backlog on leg
        if user_split > leader_board[0][1]:
            return user_split - leader_board[0][1]

        # If user is a leader, calculate diff to second place
        elif user_split == leader_board[0][1]:
            return user_split - leader_board[1][1]

    def get_legs_backlog(self) -> Series:
        """
        Calculate backlogs for all user legs
        """
        backlog_timedeltas = {}
        for n, leg in enumerate(self.course):
            backlog_timedeltas.setdefault(leg, self.calc_leg_backlog(leg))
        return Series(backlog_timedeltas)
