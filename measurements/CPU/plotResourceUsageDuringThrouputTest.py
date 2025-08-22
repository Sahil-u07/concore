import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load all data and calculate averages
try:
    avg_cpu_sender_zmq = pd.read_csv('sender_usage.csv')['cpu_percent'].mean()
    avg_mem_sender_zmq = pd.read_csv('sender_usage.csv')['memory_mb'].mean()
    
    avg_cpu_sender_mediator = 25.5 # Example value
    avg_mem_sender_mediator = 60.2 # Example value

except FileNotFoundError:
    print("One or more CSV files not found. Using placeholder data.")
    avg_cpu_sender_zmq, avg_mem_sender_zmq = 15.0, 45.0
    avg_cpu_sender_mediator, avg_mem_sender_mediator = 25.5, 60.2

# Prepare data for plotting
data = {
    'Protocol': ['Mediator', 'ZeroMQ', 'Mediator', 'ZeroMQ'],
    'Metric': ['CPU Usage (%)', 'CPU Usage (%)', 'Memory Usage (MB)', 'Memory Usage (MB)'],
    'Value': [avg_cpu_sender_mediator, avg_cpu_sender_zmq, avg_mem_sender_mediator, avg_mem_sender_zmq]
}
df_plot = pd.DataFrame(data)

# Create the grouped bar chart
plt.figure(figsize=(8.27, 11.69))  # A4 size in inches (210mm x 297mm)
sns.barplot(x='Metric', y='Value', hue='Protocol', data=df_plot, palette={'Mediator': '#F44336', 'ZeroMQ': '#4CAF50'})

plt.xlabel('Performance Metric', fontsize=14)
plt.ylabel('Average Usage', fontsize=14)
plt.legend(title='Protocol', fontsize=12, title_fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()

# Save to PDF
plt.savefig("resource_utilization.pdf", format="pdf")
plt.show()