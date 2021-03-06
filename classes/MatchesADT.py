from modules.data_processing import get_json
from modules.data_processing import player_profile
from modules.data_processing import previous_encounters
import datetime


class Matches:
    """
    Class that represents the ADT called Matches based on stack.
    """
    def __init__(self, gender, items=[]):
        """
        Initialize a new empty stack.
        0 for female, 1 for male.
        """
        self.items = items
        self.rankings_path = "../data/men_rankings.txt" if gender else "../data/women_rankings.txt"
        self.rankings_len = 501 if gender else 500

    def add(self, item):
        """
        Adds a new match to the stack.
        """
        self.items.append(item)

    def pop(self):
        """
        Remove and return a match from the stack.
        """
        return self.items.pop()

    def is_empty(self):
        """
        Return bool whether the stack is empty.
        """
        return self.items == []

    def process_match(self):
        """
        Pop the match from stack and process it.
        """
        match = self.pop()

        data = get_json("/tennis-t2/en/matches/{}/summary.json?api_key=8vfgwpuch3rpnauqm9cbzp7d".format(match))

        tournament = data["sport_event"]["tournament"]["id"]
        tournament_data = get_json(
            "/tennis-t2/en/tournaments/{}/info.json?api_key=8vfgwpuch3rpnauqm9cbzp7d".format(tournament))

        surface = tournament_data["info"]["surface"]
        if surface not in ["Red clay", "Grass", "Hardcourt outdoor", "Hardcourt indoor"]:
            return None

        profile1, profile2 = player_profile(data["sport_event"]["competitors"][0]["id"], self.rankings_path), \
                             player_profile(data["sport_event"]["competitors"][1]["id"], self.rankings_path)

        rank1, rank2 = profile1[2], profile2[2]
        if rank1 == 0 or rank2 == 0:
            return None
        rank_data = round((rank1 / self.rankings_len + (1 - rank2 / self.rankings_len)) / 2, 3)

        surface_stats1, surface_stats2 = profile1[3][surface], profile2[3][surface]
        surface_data = round(((1 - surface_stats1) + surface_stats2) / 2, 3)

        date = datetime.datetime.strptime(data["sport_event"]["scheduled"][:10], "%Y-%m-%d")
        previous_data = previous_encounters(profile1[0], profile2[0], date)

        try:
            winner = 0 if data["sport_event_status"]["winner_id"] == profile1[0] else 1
        except KeyError as ke:
            print(ke)
            return None

        return [profile1[0], profile1[1].replace(",", ""), profile2[0], profile2[1].replace(",", ""), match,
                str(rank_data), str(surface_data), str(previous_data), str(winner)]

    def from_file(self, path):
        """
        Add matches from file to stack.
        :param path: file path
        :return:
        """
        matches = []

        with open(path) as f:
            for line in f:
                matches.append(line.strip())
        self.items = matches

    def process_and_write(self, path):
        """
        Process all the matches and write to file.
        :param path: file path
        :return:
        """
        for i in range(len(self.items)):
            processed = self.process_match()
            print(processed)
            with open(path, "a+") as f:
                if processed:
                    f.write(",".join(processed) + "\n")

    def __eq__(self, other):
        """
        (Matches) -> bool
        Compare two Matches ADT.
        :param other: Matches ADT object
        :return: bool whether objects are equal
        """
        return self.items == other.items and self.rankings_path == other.rankings_path

    def __str__(self):
        """
        Return string representation of object.
        :return:
        """
        return str(self.items)

    def __len__(self):
        """
        Return length of the stack.
        """
        return len(self.items)
