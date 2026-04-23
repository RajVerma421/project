from flask import Flask, render_template, request, send_from_directory, url_for
from dotenv import load_dotenv
from Script_generator import Script
from tts_local import text_to_speech
from splitText import split_text
from video_generator import create_dynamic_video

import os
import wave

load_dotenv()
app = Flask(__name__)

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Output folders
AUDIO_DIR = os.path.join(BASE_DIR, "output", "audio")
VIDEO_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)


#  Route to serve video files
@app.route('/video/<filename>')
def serve_video(filename):
    return send_from_directory(VIDEO_DIR, filename)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate_script", methods=["POST"])
def generate_script():
    topic = request.form.get("topic")
    content_type = request.form.get("type")
    emotion = request.form.get("emotion")

    if not topic or not content_type or not emotion:
        return render_template("index.html", script="Fill all fields")

    try:
        # Step 1: Generate script
        script_response = Script(content_type, topic, emotion)[:300]

        # Step 2: Split text
        chunks = split_text(script_response)

        audio_files = []

        # Step 3: Generate audio chunks
        for i, chunk in enumerate(chunks):
            filename = os.path.join(AUDIO_DIR, f"audio_{i}.wav")
            audio_path = text_to_speech(chunk, filename)
            audio_files.append(audio_path)

        # Step 4: Merge audio files
        final_audio = os.path.join(AUDIO_DIR, "final_audio.wav")

        with wave.open(final_audio, 'wb') as outfile:
            for i, file in enumerate(audio_files):
                with wave.open(file, 'rb') as infile:
                    if i == 0:
                        outfile.setparams(infile.getparams())
                    outfile.writeframes(infile.readframes(infile.getnframes()))

        #  Debug check (optional)
        print("Final audio exists:", os.path.exists(final_audio))

        # Step 5: Create video
        video_output = os.path.join(VIDEO_DIR, "final_video.mp4")

        video_path = create_dynamic_video(
            script=script_response,
            audio_file=final_audio,
            output_path=video_output    
        )

        #  Send only filename to frontend
        video_filename = os.path.basename(video_path)

        return render_template(
            "index.html",
            script=script_response,
            audio_files=audio_files,
            video_file=video_filename
        )

    except Exception as e:
        print("Error:", str(e))
        return render_template("index.html", script=f"Error: {str(e)}")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)