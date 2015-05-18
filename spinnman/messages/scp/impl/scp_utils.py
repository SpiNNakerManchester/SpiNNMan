
# A dict of (read address, read length) -> read type
address_length_dtype = {
    (i, j): (2 if (i == j == 0) else
             (1 if (i % 2 == j % 2 == 0) else
              0))
    for i in range(4) for j in range(4)
}
