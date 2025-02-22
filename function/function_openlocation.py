import os

def open_file_location():
    # Get documents folder path
    documents_path = os.path.join(os.path.expanduser("~"), "Documents")
    output_dir = os.path.join(documents_path, "audio-edita")
    
    # Create directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Open the directory
    os.startfile(output_dir)