from typing import Optional

from pandas import DataFrame, Series

from src.services.results.src.res_event import ResEvent


class ResGroup:
    """
    Group class with group parameters and methods for calculate statistics
     on group legs(not course, because group can have several dispersions).

    Group init by group_name and event
    """

    def __init__(self, group_name: str, event: ResEvent):
        self.name = group_name.upper()
        self.df = event.get_group_frame(self.name)
        self.dispersions = event.get_group_dispersions(self.name)
        self.runners = self.df.index.to_list()
        self.legs = self.df.columns.to_list()

    def get_results(self) -> Series:
        """
        Return Series with group results.
        """
        return self.df.loc[self.runners, "RES"].sort_values()

    def get_legs_leaders(self) -> Series:
        """
        Find leader splits on each leg on course.
        """
        df = self.df
        legs = self.legs
        return Series({leg: df.loc[:, leg].sort_values()[0] for leg in legs})

    def get_biggest_backlogs_on_course(self) -> DataFrame:
        """
        Return DataFrame with persons biggest backlog on each course leg.
        """
        legs = self.legs
        # Get leader times on each leg
        leader_times = self.get_legs_leaders()
        # Find biggest splits on each leg
        biggest_splits = [self.get_leg_leaderboard(leg)[-1] for leg in legs]
        # By biggest splits find biggest backlogs
        biggest_backlogs = [(leg, biggest_splits[n][0], biggest_splits[n][1] - leader_times[n]) for n, leg in
                            enumerate(legs)]
        # Unite biggest backlogs to DF
        return DataFrame(biggest_backlogs).sort_values(by=2, ascending=False)

    def get_legs_with_biggest_std(self) -> Series:
        """
        Return series with legs sorted by std.
        """
        df = self.df
        course = self.legs
        return df[course].std().sort_values(ascending=False)

    def get_leaderboard_by_wins_on_legs(self) -> Series:
        """
        Calc leader board by wins on legs.
        """
        df = self.df
        course = self.legs
        leaders_on_legs = [list(df.loc[:, leg].sort_values().items())[0][0] for leg in course]
        return Series(leaders_on_legs).value_counts()

    def get_leg_leaderboard(self, leg: str) -> list:
        """
        Return list with leaderboard rows like a (name, split on leg)
        :param leg: 
        :return: 
        """
        return list(self.df.loc[:, leg].sort_values().items())

    def get_leaderboard_by_win_on_leg(self) -> DataFrame:
        """
        Calc leader board by difference between first and second place on leg.
        """
        legs = self.legs
        leaders_win_on_legs = []
        for leg in legs:
            leg_leaderboard = self.get_leg_leaderboard(leg)
            leader_gain = leg_leaderboard[1][1] - leg_leaderboard[0][1]
            leaders_win_on_legs.append((leg_leaderboard[0][0], leader_gain))
        return DataFrame(leaders_win_on_legs, index=legs).sort_values(by=1, ascending=False)

    # One runner related methods
    def get_runner_course(self, runner: str) -> Optional[list]:
        course = eval([key for key, names in self.dispersions if runner in names][0])
        if not course:
            raise ValueError(f"No {runner} course in {self.name} dispersions")
        return course

    def get_runner_data(self, runner: str, course: list) -> Series:
        """
        Getting runners row from group df
        :param runner: index in dataframe
        :param course: list with runner legs
        :return: pandas Series with runner's split on each leg
        """
        if runner not in self.df.index:
            raise IndexError(f"No {runner} in {self.name}")
        return self.df.loc[runner, course]
