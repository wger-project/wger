# Standard Library
import sqlite3


'''
This script automates adding exercise variations to the database.
Do not need to run again. Has already been ran.
'''

exercise_variation_ids = {
    # Rows
    1: [
        106, 108, 109,
        110, 142, 202,
        214, 339, 340,
        362, 412, 670
    ],
    # Lat Pulldowns
    2: [
        187, 188, 204,
        212, 213, 215,
        216, 424
    ],
    # Deadlifts
    3: [
        105, 161, 209,
        328, 351, 381
    ],
    # Shoulder Raises
    4: [
        148, 149, 233,
        237, 306, 421
    ],
    # "Shoulder Press"
    5: [
        119, 123, 152,
        155, 190, 227,
        228, 229, 329
    ],
    # "Calf Raises"
    6: [
        102, 103, 104,
        776
    ],
    # "Bench Press"
    7: [
        100, 101, 163,
        192, 210, 211,
        270, 399
    ],
    # "Pushups"
    8: [
        168, 182, 260,
        302, 790
    ],
    # "Chest Fly"
    9: [
        122, 145, 146,
        206
    ],
    # "Crunches"
    10: [
        91, 92, 93,
        94, 176, 416,
        95, 170
    ],
    # "Kicks"
    11: [
        303, 631, 125,
        126, 166
    ],
    # "Squats"
    12: [
        111, 160, 185,
        191, 300, 342,
        346, 355, 387,
        389, 407, 650,
        795
    ],
    # "Lunges"
    13: [
        112, 113, 346,
        405
    ],
    # "Leg Curls"
    14: [
        117, 118, 154,
        792
    ],
    # "Leg Press"
    15: [
        114, 115, 130,
        788
    ],
    # "Bicep Curls"
    16: [
        74, 80, 81,
        86, 129, 138,
        193, 205, 208,
        275, 298, 305,
        768
    ],
    # "Tricep Extensions"
    17: [
        89, 90, 274,
        344
    ],
    # "Tricep Presses"
    18: [
        84, 85, 88,
        186, 217, 218,
        386
    ],
    # "Dips"
    19: [
        82, 83, 162,
        360
    ]
}

conn = sqlite3.connect('database.sqlite')
c = conn.cursor()

for i in exercise_variation_ids:
    c.execute('''INSERT INTO
                 exercises_variation(id)
                 VALUES(?)''', (i,))
    for j in exercise_variation_ids[i]:
        # print((j, i))
        c.execute(
            '''UPDATE
               exercises_exercise
               SET variations_id = ?
               WHERE id = ?''', (i, j)
        )

# conn.commit()
# conn.close()
