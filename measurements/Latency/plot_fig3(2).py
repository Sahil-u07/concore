import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the collected data
try:
    df_zmq = pd.read_csv('zeromq_latencies.csv')
    df_zmq['Protocol'] = 'ZeroMQ' # Add a column to identify the protocol
except FileNotFoundError:
    print("Error: zeromq_latencies.csv not found. Please run the experiment first.")
    exit()

# It's good practice to filter out extreme outliers if they exist, 
# for example, values over a certain threshold that might be due to a one-off system lag.
# For now, we will plot all the data.

# Create the plot
plt.figure(figsize=(8, 7))
sns.violinplot(x='Protocol', y='Latency (ms)', data=df_zmq, palette=['#4CAF50'])

# Add details to the plot
plt.title('Latency Distribution of ZeroMQ Protocol', fontsize=16)
plt.xlabel('')
plt.ylabel('Round-Trip Latency (ms)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.xticks(fontsize=12)

# Calculate and print statistics to include in your paper
median_val = df_zmq['Latency (ms)'].median()
mean_val = df_zmq['Latency (ms)'].mean()
std_val = df_zmq['Latency (ms)'].std()

print(f"ZeroMQ Latency Stats:")
print(f"  - Median: {median_val:.4f} ms")
print(f"  - Mean:   {mean_val:.4f} ms")
print(f"  - Std Dev: {std_val:.4f} ms")

plt.show()