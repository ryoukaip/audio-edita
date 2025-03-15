import subprocess
import os

def convert_to_mp3(input_file, output_file):
    command = [
        "ffmpeg", "-y", "-i", input_file, "-b:a", "128k", "-vn", output_file
    ]
    try:
        subprocess.run(command, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error converting {input_file} to MP3:", e)

def check_similarity(file1, file2):
    command = ["audiomatch", "--length", "300", "./temp"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        output = result.stdout
        
        # Check if both temp files are in the output
        if "temp1.mp3" in output and "temp2.mp3" in output:
            print("it's similar")
        else:
            print("it's not similar")
    except subprocess.CalledProcessError as e:
        print("Error running audiomatch:", e)

def main():
    cwd = os.getcwd()  # Get the current working directory
    os.environ["PATH"] += os.pathsep + cwd  # Append it to the PATH
    print("Updated PATH:", os.environ["PATH"]) # Temporary add current working directory to PATH
    
    file1 = "st.mp3"
    file2 = "stbeat.mp3"
    os.makedirs("./temp", exist_ok=True)
    temp1 = "./temp/temp1.mp3"
    temp2 = "./temp/temp2.mp3"
    
    convert_to_mp3(file1, temp1)
    convert_to_mp3(file2, temp2)
    
    check_similarity(temp1, temp2)
    
    os.remove(temp1)
    os.remove(temp2)
    print("Temporary files deleted.")

# if __name__ == "__main__":
#     main()
