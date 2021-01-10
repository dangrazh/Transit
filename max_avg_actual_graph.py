from matplotlib import pyplot as plt
import numpy as np

hours_of_day = [
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
]

max = [
    50,
    20,
    80,
    90,
    100,
    120,
    125,
    130,
    400,
    240,
    235,
    200,
    200,
    250,
    300,
    500,
    250,
    200,
    152,
    120,
    100,
    80,
    60,
    50,
]
avg = [
    42,
    17,
    68,
    76,
    85,
    102,
    106,
    110,
    120,
    125,
    130,
    120,
    110,
    130,
    140,
    145,
    140,
    120,
    115,
    102,
    85,
    68,
    51,
    42,
]
actual = [
    40,
    15,
    65,
    70,
    80,
    100,
    95,
    100,
    110,
    115,
    122,
    117,
    105,
    120,
    126,
    123,
    120,
    115,
    110,
    100,
    80,
    65,
    50,
    40,
]

# working with styles
# print(plt.style.available)  # to show the available styles
# 'Solarize_Light2', '_classic_test_patch', 'bmh', 'classic', 'dark_background', 'fast', 'fivethirtyeight', 'ggplot', 'grayscale', 'seaborn', 'seaborn-bright', 'seaborn-colorblind', 'seaborn-dark', 'seaborn-dark-palette', 'seaborn-darkgrid', 'seaborn-deep', 'seaborn-muted', 'seaborn-notebook', 'seaborn-paper', 'seaborn-pastel', 'seaborn-poster', 'seaborn-talk', 'seaborn-ticks', 'seaborn-white', 'seaborn-whitegrid', 'tableau-colorblind10'
plt.style.use("ggplot")
# plt.xkcd()  # do the graph comic style...

# set the size
plt.figure(figsize=(16, 9))

print("potting graph")

# plot the max area 1st
plt.fill_between(hours_of_day, max, color="#ffcc00", label="90 days max")
# plot the avg area 2nd
plt.fill_between(hours_of_day, avg, color="#99cc33", label="90 days avg")
# plot the actual line last
plt.plot(
    hours_of_day,
    actual,
    color="#444444",
    linestyle=":",
    # marker=".",
    linewidth=2,
    label="current day",
)

plt.xlabel("Time of Day")
plt.xticks(np.arange(1, 25, step=1))

plt.ylabel("No of Order")
plt.title("Volume Metrix")
plt.legend()

print("saving graph")
plt.savefig("P:/Dani/Programming/Python/matplotlib/plot_volumes.png")

print("showing graph")
plt.show()