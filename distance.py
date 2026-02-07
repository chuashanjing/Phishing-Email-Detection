def distance_checker(rows, cols):

    table = []

    #11 times
    for i in range(len(rows)+1):
        row = []
        #11 times
        for j in range(len(cols)+1):
            #row will have 11 0s
            row.append(0)
        #put the 11 0s into table array
        """
        [
        "", g, o, o, g, l, e, ., c, 0, m
    "" [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        g [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        o [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        o [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        g [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        l [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        e [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        . [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        c [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        o [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        m [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        ]
        """
        table.append(row)

    #fill up first row
    for i in range(len(rows)+1):
        table[i][0] = i

    #fill up first column
    for j in range(len(cols)+1):
        table[0][j] = j


    for i in range(1, len(rows)+1):
        for j in range(1, len(cols)+1):
            #based on levenshtein formula
            #if value of i and j is the same, lev(i,j) = 0 
            if rows[i-1] == cols[j-1]:
                cost = 0
            else:
                cost = 1

            #loop through every row and column combination
            table[i][j] = min(
                #deletion formula
                table[i-1][j] + 1,
                #insertion formula
                table[i][j-1] + 1,
                #substitution formula
                table[i-1][j-1] + cost
            )

    """
    result:
    [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 
    [1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 
    [2, 1, 0, 1, 2, 3, 4, 5, 6, 7, 8], 
    [3, 2, 1, 0, 1, 2, 3, 4, 5, 6, 7], 
    [4, 3, 2, 1, 0, 1, 2, 3, 4, 5, 6], 
    [5, 4, 3, 2, 1, 0, 1, 2, 3, 4, 5], 
    [6, 5, 4, 3, 2, 1, 0, 1, 2, 3, 4], 
    [7, 6, 5, 4, 3, 2, 1, 0, 1, 2, 3], 
    [8, 7, 6, 5, 4, 3, 2, 1, 0, 1, 2], 
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 1, 2], 
    [10, 9, 8, 7, 6, 5, 4, 3, 2, 2, 1]
    ] 
    last row last column is the distance value
    """


    return table[-1][-1]
