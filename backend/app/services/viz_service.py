import matplotlib.pyplot as plt
import os

def plot_data(arrays):
    plt.figure(figsize=(10, 10))
    plt.scatter(arrays[:, 0], arrays[:, 1], c='blue', label='Data points')
    plt.legend()
    plt.title("Query Visualization")
    
    os.makedirs("visualizations", exist_ok=True)
    file_path = 'visualizations/data_visualization.png'
    plt.savefig(file_path, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    visualization_path = os.path.basename(file_path)

    return visualization_path