"""A class to store tables.

Sample Usage:
    table = SgTable()
    table.Append([1, 2, 3])
    table.Append([2, 4, 6])
    table.Append([3, 6, 9])
    for row in table:
        print(row)
    print(table[1])
    table[1] = [2, 2, 2]
    print(ta