import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import datetime as dt

# File path to the log file
file_path = 'pico_log.txt'

# Function to parse a line from the log file
def parse_line(line):
    parts = line.split()
    timestamp = " ".join(parts[:2])
    x, y = parts[-2].strip(','), parts[-1]
    return timestamp, float(x), float(y)

# Function to read and parse the log file
def read_log_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    data = [parse_line(line) for line in lines if line.strip()]
    return pd.DataFrame(data, columns=['timestamp', 'x', 'y'])

# Initialize the plot
fig, ax = plt.subplots(figsize=(14, 6))
x_cumsum_line, = ax.plot([], [], label='Cumulative X', marker='o', linestyle='-')
y_cumsum_line, = ax.plot([], [], label='Cumulative Y', marker='o', linestyle='-')
ax.set_title('Cumulative Sum of X and Y Coordinates Over Time (17:10 - 17:45)')
ax.set_xlabel('Time')
ax.set_ylabel('Cumulative Value')
ax.legend()
plt.xticks(rotation=45)
plt.tight_layout()

# Function to update the plot
def update(frame):
    # Read the log file and create DataFrame
    df = read_log_file(file_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Set timestamp as index
    df.set_index('timestamp', inplace=True)

    # Filter data between 17:10 and 17:45
    start_time = '17:10'
    end_time = '17:45'
    filtered_df = df.between_time(start_time, end_time)

    # Filter out x or y values that are between -2 and 2
    filtered_df = filtered_df[(filtered_df['x'] < -2) | (filtered_df['x'] > 2) |
                              (filtered_df['y'] < -2) | (filtered_df['y'] > 2)]

    # Compute the cumulative sum (integration) of x and y
    filtered_df['x_cumsum'] = filtered_df['x'].cumsum()
    filtered_df['y_cumsum'] = filtered_df['y'].cumsum()

    # Update plot data
    x_cumsum_line.set_data(filtered_df.index, filtered_df['x_cumsum'])
    y_cumsum_line.set_data(filtered_df.index, filtered_df['y_cumsum'])

    # Adjust plot limits
    ax.relim()
    ax.autoscale_view()

# Create the animation
ani = FuncAnimation(fig, update, interval=1000)  # Update every second (1000 ms)

# Show the plot
plt.show()
