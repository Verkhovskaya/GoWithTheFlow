from enum import IntEnum

class ParseMode(IntEnum):
    ENTRANCES = 1
    EXITS = 2
    ENT_GUESS = 3
    EXT_GUESS = 4


def parse_txt(fileURL, imgHeight, imgWidth):
    mode = ParseMode.ENTRANCES

    entrances = []
    exits = []
    entrance_guesses = []
    exit_guesses = []
    with open(fileURL) as f:
        for line in f:
            if line.startswith('***'):
                mode += 1
                continue

            x, y = line.split()
            if mode == ParseMode.ENTRANCES:
                entrances.append((int(x), int(y)))
            elif mode == ParseMode.EXITS:
                exits.append((int(x), int(y)))
            elif mode == ParseMode.ENT_GUESS:
                entrance_guesses.append((int(x), int(y)))
            elif mode == ParseMode.EXT_GUESS:
                exit_guesses.append((int(x), int(y)))

    print(imgWidth)
    print(imgHeight)
    print(entrance_guesses)
    print(exit_guesses)
    entrance_guesses = transform_guesses(entrance_guesses, imgHeight, imgWidth)
    exit_guesses = transform_guesses(exit_guesses, imgHeight, imgWidth)
    return entrances, exits, entrance_guesses + exit_guesses


def transform_guesses(guesses, img_height, img_width):
    MARGIN_MULTIPLIER = 0.05
    outputs = []
    for guess in guesses:
        is_bottom_left_half = guess[1] > guess[0]
        is_top_left_half = img_height - guess[1] > guess[0]

        if is_bottom_left_half and is_top_left_half:
            # Left
            outputs.append((
                'left',
                guess[1] - MARGIN_MULTIPLIER*img_height,
                guess[1] + MARGIN_MULTIPLIER*img_height
            ))
        elif is_bottom_left_half and not is_top_left_half:
            # Bottom
            outputs.append((
                'bottom',
                guess[0] - MARGIN_MULTIPLIER*img_width,
                guess[0] + MARGIN_MULTIPLIER*img_width
            ))
        elif not is_bottom_left_half and is_top_left_half:
            # Top
            outputs.append((
                'top',
                guess[0] - MARGIN_MULTIPLIER*img_width,
                guess[0] + MARGIN_MULTIPLIER*img_width
            ))
        elif not is_bottom_left_half and not is_top_left_half:
            # Right
            outputs.append((
                'right',
                guess[1] - MARGIN_MULTIPLIER*img_height,
                guess[1] + MARGIN_MULTIPLIER*img_height
            ))
    return outputs
