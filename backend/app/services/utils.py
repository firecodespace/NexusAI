def wordsToNumber(words):
    map = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
        "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
        "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
        "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
        "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90, "hundred": 100,
        "thousand": 1000
    }

    tokens = words.lower().replace(",", "").replace("-", " ").split()
    total = 0
    current = 0

    for word in tokens:
        if word in map:
            val = map[word]
            if val == 100:
                current *= val
            elif val == 1000:
                current *= val
                total += current
                current = 0
            else:
                current += val
        else:
            continue

    total += current
    return total
