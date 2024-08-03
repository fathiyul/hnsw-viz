import matplotlib.pyplot as plt
import os

def plot_data(arrays, query_vector=None):
    fname = 'data_visualization'
    plt.figure(figsize=(10, 10))
    plt.scatter(arrays[:, 0], arrays[:, 1], c='blue', label='Data points')
    if query_vector is not None:
        plt.scatter(query_vector[0], query_vector[1], c='red', s=100, label='Query')
        fname = 'query_vector'
    plt.legend()
    plt.title("Query Visualization")
    
    os.makedirs("visualizations", exist_ok=True)
    file_path = f'visualizations/{fname}.png'
    plt.savefig(file_path, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    visualization_path = os.path.basename(file_path)

    return visualization_path