import matplotlib.pyplot as plt

# --- Enter your collected data here ---
throughput_mediator = 15.7     # messages/sec
throughput_zmq = 25432.1       # messages/sec
# -------------------------------------

protocols = ['Mediator', 'ZeroMQ']
values = [throughput_mediator, throughput_zmq]
colors = ['#F44336', '#4CAF50']

plt.figure(figsize=(8.27, 11.69))  # A4 size in inches

bars = plt.bar(protocols, values, color=colors)

# Add plot details
plt.ylabel('Throughput (Messages/Second)', fontsize=14)
plt.title('Figure 6: Maximum Throughput Comparison', fontsize=18, pad=25)
plt.xticks(fontsize=12)
plt.yscale('log')  # log scale for large differences
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Add text labels on top of the bars
for bar in bars:
    yval = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2.0,
        yval,
        f'{yval:,.0f}',
        va='bottom',
        ha='center',
        fontsize=12
    )

plt.tight_layout()

# Save the figure as PDF
plt.savefig('throughput_comparison.pdf', format='pdf')
print("Plot saved as 'throughput_comparison.pdf'")

plt.show()