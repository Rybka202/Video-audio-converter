import subprocess


def converter(input_file: str, output_file: str):
    ffmpeg_cmd = ["ffmpeg", "-i",
                  input_file, output_file]
    try:
        subprocess.run(ffmpeg_cmd, capture_output=True)
    except subprocess.CalledProcessError as e:
        print("Conversion failed!!!")