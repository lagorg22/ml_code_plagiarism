import os
import shutil

def get_unique_filename(target_dir, filename, used_names):
    """
    Generate a unique filename by appending a suffix if the name is already used.
    
    Args:
        target_dir (str): The directory where the file will be placed.
        filename (str): The original filename.
        used_names (set): Set of filenames already used in the target directory.
    
    Returns:
        str: A unique filename.
    """
    base, ext = os.path.splitext(filename)
    target_filename = filename
    counter = 1
    
    while target_filename in used_names or os.path.exists(os.path.join(target_dir, target_filename)):
        target_filename = f"{base}_{counter}{ext}"
        counter += 1
    
    return target_filename

def flatten_all_repositories(parent_dir, extensions, target_dir=None):
    """
    Flatten all repositories (subdirectories) in the parent_dir by copying all code files
    to a single flattened directory.
    
    Args:
        parent_dir (str): Path to the directory containing the repositories.
        extensions (list): List of file extensions (e.g., ['.py', '.java']) to include.
        target_dir (str, optional): Destination directory. If None, creates 'flattened_all' in parent_dir.
    """
    # Check if parent_dir is a valid directory
    if not os.path.isdir(parent_dir):
        print(f"Error: {parent_dir} is not a directory or does not exist.")
        return
    
    # Set default target directory if not specified
    if target_dir is None:
        target_dir = os.path.join(parent_dir, 'codefiles')
    
    # Create the target directory if it doesn’t exist
    os.makedirs(target_dir, exist_ok=True)
    
    # Keep track of used filenames to handle conflicts
    used_names = set()
    
    # Process each subdirectory in parent_dir
    for repo_name in os.listdir(parent_dir):
        repo_path = os.path.join(parent_dir, repo_name)
        if os.path.isdir(repo_path):
            print(f"Processing directory: {repo_path}")
            # Walk through all directories and subdirectories
            for root, dirs, files in os.walk(repo_path):
                for file in files:
                    # Check if the file has a specified extension (case-insensitive)
                    if os.path.splitext(file)[1].lower() in extensions:
                        source_file = os.path.join(root, file)
                        # Generate a unique filename
                        unique_filename = get_unique_filename(target_dir, file, used_names)
                        target_file = os.path.join(target_dir, unique_filename)
                        # Copy the file with metadata
                        shutil.copy2(source_file, target_file)
                        used_names.add(unique_filename)
                        print(f"Copied {source_file} to {target_file}")
    
    print(f"All code files have been flattened into {target_dir}")

if __name__ == "__main__":
    # Example usage
    parent_dir = './'  # Replace with your directory path
    extensions = ['.py', '.java', '.c', '.cc', '.cpp', '.h', '.js', '.xml', '.html']  # Define code file extensions
    
    flatten_all_repositories(parent_dir, extensions)