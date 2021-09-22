"""Group and generate a list of SgTable's."""

import table as tb


class SgGrouping:
    """Group and generate a list of SgTable's."""

    @staticmethod
    def GenerateGroups(table, groups):
        num_groups = len(groups)
        groups_dict = {}
        for row in table:
            key = tuple