def count_nodes_in_file(filepath):
    """Count the number of lines (nodes) in a text file."""
    try:
        with open(filepath, 'r') as f:
            return len(f.readlines())
    except FileNotFoundError:
        return 0