import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def generate_comparison_plot():
    """
    Loads latency data for ZeroMQ and Mediator protocols,
    and generates a comparative violin plot saved as A4 PDF.
    """
    try:
        df_zmq = pd.read_csv('zeromq_latencies.csv')
        df_zmq['Protocol'] = 'ZeroMQ'
        
        df_mediator = pd.read_csv('mediator_latencies.csv')
        df_mediator['Protocol'] = 'Mediator'
        
    except FileNotFoundError as e:
        print("Error: Missing latency CSV file(s). Place 'zeromq_latencies.csv' and 'mediator_latencies.csv' in the same directory.")
        print(f"Details: {e}")
        return

    df_combined = pd.concat([df_zmq, df_mediator], ignore_index=True)

    print("Generating plot...")
    plt.figure(figsize=(8.27, 11.69))  # A4 size in inches

    sns.violinplot(
        x='Protocol', 
        y='Latency (ms)', 
        data=df_combined,
        palette={'ZeroMQ': '#4CAF50', 'Mediator': '#F44336'}
    )

    plt.xlabel('Communication Protocol', fontsize=14)
    plt.ylabel('Round-Trip Latency (ms)', fontsize=14)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.grid(True, which='major', linestyle='--', linewidth=0.5, color='grey')

    plt.tight_layout()
    plt.savefig('latency_comparison.pdf', format='pdf')
    print("Plot saved as 'latency_comparison.pdf'")

    plt.show()

if __name__ == '__main__':
    generate_comparison_plot()