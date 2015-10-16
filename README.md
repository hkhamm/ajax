# Brevet Checkpoint Time Calculator

Randonneuring is a long-distance cycling sport. A randonneuring event is 
called a randonnée or brevet. Brevets are composed of a series of checkpoints. 
Each checkpoint has an open and close time. A checkpoint's open or close 
time is the sum of those portions of a checkpoint's distance from the 
starting point that fall within a series of ranges. Each range increment has 
a corresponding minimum and maximum speed. (see Speeds Table)

## Speeds Table

| Control location (km) | Minimum Speed (km/hr) | Maximum Speed (km/hr) |
| --------------------- | --------------------- | --------------------- |
| 0 - 200               | 15                    | 34                    |
| 200 - 400             | 15                    | 32                    |
| 400 - 600             | 15                    | 30                    |
| 600 - 1000            | 11.428                | 28                    |
| 1000 - 1300           | 13.333                | 26                    |

## General Rules

1. Determine what range increment the current distance falls within. Note the
 min and max speeds and the low end of the range increment.
2. For open times: total += (current distance - low end) / max speed
3. For close times: total += (current distance - low end) / min speed
4. Set current distance -= (current distance - low end)
5. Repeat 1 - 4 until current distance is 0
6. Convert total into hours and minutes
7. Add hours and minutes to the starting datetime

## Special Rules

Final checkpoint closing times:
- 200 km: 13H30
- 300 km: 20H0
- 400 km: 27H00
- 600 km: 40H00
- 1000 km: 75H00

Final checkpoints are allowed to be up to 20% over the the brevet distance, 
however they still have the closing times listed above.