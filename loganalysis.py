import pandas as pd
import matplotlib.pyplot as plt

# Load the data from the provided log file
file_path = 'pico_log.txt'

# Define a function to parse the lines
def parse_line(line):
    parts = line.split()
    timestamp = " ".join(parts[:2])
    x, y = parts[-2].strip(','), parts[-1]
    return timestamp, float(x), float(y)

# Read and parse the log file
with open(file_path, 'r') as file:
    lines = file.readlines()
    data = [parse_line(line) for line in lines if line.strip()]

# Create a DataFrame
df = pd.DataFrame(data, columns=['timestamp', 'x', 'y'])
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

# Get the integrated values at the end
integrated_x = filtered_df['x_cumsum'].iloc[-1]
integrated_y = filtered_df['y_cumsum'].iloc[-1]

#integrated val * pixel size of camera * motion scale * 1000nm/micron
x_nm = integrated_x * 3.8 * 0.8 * 1000
y_nm = integrated_y * 3.8 * 0.8 * 1000
print(integrated_x, integrated_y)

# Plot the integrated (cumulative sum) data
plt.figure(figsize=(14, 6))
plt.plot(filtered_df.index, filtered_df['x_cumsum'], label='Cumulative X', marker='o', linestyle='-')
plt.plot(filtered_df.index, filtered_df['y_cumsum'], label='Cumulative Y', marker='o', linestyle='-')
plt.title('Cumulative Sum of X and Y Coordinates Over Time (17:10 - 17:45)')
plt.xlabel('Time')
plt.ylabel('Cumulative Value')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
