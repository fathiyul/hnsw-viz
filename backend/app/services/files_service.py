import glob
import os 

def delete_png_files(q=None):
    fname_pattern = f'*.png'
    if q is not None:
        fname_pattern = f'*{q}*.png'
    search_pattern = os.path.join('visualizations/', fname_pattern)
    for file_path in glob.glob(search_pattern):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")