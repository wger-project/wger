import sqlite3
from itertools import permutations

'''
This script automates adding exercise variations to the database.
Do not need to run again. Has already been ran.
'''

exercise_variation_ids = {
    "Deadlifts": [
        105, 161, 209,
        328, 351, 381
    ],
    "Shoulder Raises": [
        148, 149, 233,
        237, 306, 421
    ],
    "Shoulder Press": [
        119, 123, 152,
        155, 190, 227,
        228, 229, 329
    ],
    "Calf Raises": [
        102, 103, 104,
        776
    ],
    "Bench Press": [
        100, 101, 163,
        192, 210, 211,
        270, 399
    ],
    "Pushups": [
        168, 182, 260,
        302, 790
    ],
    "Chest Fly": [
        122, 145, 146,
        206
    ],
    "Crunches": [
        91, 92, 93,
        94, 176, 416,
        95, 170
    ],
    "Kicks": [
        303, 631, 125,
        126, 166
    ],
    "Squats": [
        111, 160, 185,
        191, 300, 342,
        346, 355, 387,
        389, 407, 650,
        795
    ],
    "Lunges": [
        112, 113, 346,
        405
    ],
    "Leg Curls": [
        117, 118, 154,
        792
    ],
    "Leg Press": [
        114, 115, 130,
        788
    ],
    "Bicep Curls": [
        74, 80, 81,
        86, 129, 138,
        193, 205, 208,
        275, 298, 305,
        768
    ],
    "Tricep Extensions": [
        89, 90, 274,
        344
    ],
    "Tricep Presses": [
        84, 85, 88,
        186, 217, 218,
        386
    ],
    "Dips": [
        82, 83, 162,
        360
    ]
}

conn = sqlite3.connect('database.sqlite')
c = conn.cursor()

# Gets all variations of exercises and pairs them together
def get_exercise_permutations(exercise):
    perms = permutations(exercise, 2)
    return list(perms)


for i in exercise_variation_ids:
    exercise_perms = get_exercise_permutations(exercise_variation_ids[i])
    c.executemany('''INSERT INTO exercises_exercise_variations(from_exercise_id, to_exercise_id)
                     VALUES(?, ?)''', exercise_perms)

#conn.commit()
#conn.close()