import os

def generate_avatar(audio_path, image_path, output_dir="output/avatar"):

    os.makedirs(output_dir, exist_ok=True)

    command = f"""
    python SadTalker/inference.py \
    --driven_audio "{audio_path}" \
    --source_image "{image_path}" \
    --result_dir "{output_dir}" \
    --enhancer gfpgan
    """

    os.system(command)

    # Return latest generated video
    files = os.listdir(output_dir)
    files = [f for f in files if f.endswith(".mp4")]

    if not files:
        return None

    latest_video = sorted(files)[-1]

    return os.path.join(output_dir, latest_video)