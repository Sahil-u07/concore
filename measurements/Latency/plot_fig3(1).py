import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def generate_comparison_plot():
    """
    Loads latency data for ZeroMQ and Mediator protocols,
    and generates a comparative violin plot.
    """
    try:
        # Load the ZeroMQ latency data
        df_zmq = pd.read_csv('zeromq_latencies.csv')
        df_zmq['Protocol'] = 'ZeroMQ'
        
        # Load the Mediator latency data
        df_mediator = pd.read_csv('mediator_latencies.csv')
        df_mediator['Protocol'] = 'Mediator'
        
    except FileNotFoundError as e:
        print(f"Error: Could not find a required CSV file. Make sure both 'zeromq_latencies.csv' and 'mediator_latencies.csv' are in the same directory.")
        print(f"Details: {e}")
        return

    # Combine both dataframes into a single one for plotting
    df_combined = pd.concat([df_zmq, df_mediator], ignore_index=True)

    # Create the violin plot
    print("Generating plot...")
    plt.figure(figsize=(10, 8))
    sns.violinplot(
        x='Protocol', 
        y='Latency (ms)', 
        data=df_combined,
        palette={'ZeroMQ': '#4CAF50', 'Mediator': '#F44336'}
    )

    # Add plot details for the research paper
    plt.title('Figure 3: Latency Distribution of Distributed Protocols', fontsize=16, pad=20)
    plt.xlabel('Communication Protocol', fontsize=12)
    plt.ylabel('Round-Trip Latency (ms)', fontsize=12)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.grid(True, which='major', linestyle='--', linewidth='0.5', color='grey')
    
    # Save the figure for your paper
    plt.savefig('figure3_latency_comparison.png', dpi=300)
    print("Plot saved as 'figure3_latency_comparison.png'")
    
    # Display the plot
    plt.show()

if __name__ == '__main__':
    generate_comparison_plot()