# # from moviepy.video.VideoClip import TextClip, ColorClip
# # from moviepy.audio.io.AudioFileClip import AudioFileClip
# # from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
# # import os

# # def create_video(script, audio_file, output_path="output/final_video.mp4"):

# #     os.makedirs(os.path.dirname(output_path), exist_ok=True)

# #     # Load audio
# #     audio = AudioFileClip(audio_file)

# #     # Background
# #     bg = ColorClip(size=(720, 1280), color=(0, 0, 0), duration=audio.duration)

# #     # Text
# #     text_clip = TextClip(
# #         text=script,
# #         font_size=40,
# #         color='white',
# #         size=(700, 1000),
# #         method='caption'
# #     ).with_duration(audio.duration)

# #     text_clip = text_clip.with_position("center")

# #     # Combine
# #     video = CompositeVideoClip([bg, text_clip])
# #     video = video.with_audio(audio)

# #     # Export
# #     video.write_videofile(output_path, fps=24)

# #     return output_path




# from moviepy.video.VideoClip import TextClip, ColorClip, VideoClip
# from moviepy.audio.io.AudioFileClip import AudioFileClip
# from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
# from moviepy.video.fx import FadeIn, FadeOut
# from moviepy.audio.io import readers as _audio_readers
# import numpy as np
# from PIL import Image, ImageDraw
# import os


# _original_close = _audio_readers.FFMPEG_AudioReader.close

# def _safe_close(self):
#     try:
#         if not hasattr(self, "proc"):
#             self.proc = None
#         _original_close(self)
#     except Exception:
#         pass

# _audio_readers.FFMPEG_AudioReader.close = _safe_close



# def make_gradient_frame(t, width=720, height=1280):
#     img = np.zeros((height, width, 3), dtype=np.uint8)
#     r = int(10 + 20 * np.sin(0.3 * t))
#     g = int(5  + 15 * np.sin(0.2 * t + 1))
#     b = int(40 + 30 * np.sin(0.25 * t + 2))
#     for y in range(height):
#         ratio = y / height
#         img[y, :, 0] = int(r * (1 - ratio) + 5  * ratio)
#         img[y, :, 1] = int(g * (1 - ratio) + 10 * ratio)
#         img[y, :, 2] = int(b * (1 - ratio) + (b + 20) * ratio)
#     return img


# def make_particles_frame(t, width=720, height=1280, n=18):
#     img    = np.zeros((height, width, 4), dtype=np.uint8)
#     rng    = np.random.default_rng(42)
#     xs     = rng.integers(50, width - 50, size=n)
#     ys     = rng.integers(0, height,      size=n)
#     speeds = rng.uniform(30, 90,          size=n)
#     sizes  = rng.integers(4, 14,          size=n)
#     phases = rng.uniform(0, 2 * np.pi,   size=n)

#     pil  = Image.fromarray(img, mode="RGBA")
#     draw = ImageDraw.Draw(pil)
#     for i in range(n):
#         y = int((ys[i] - speeds[i] * t) % height)
#         x = int(xs[i] + 12 * np.sin(0.5 * t + phases[i]))
#         r = sizes[i]
#         a = int(120 + 100 * np.sin(0.8 * t + phases[i]))
#         draw.ellipse([x-r, y-r, x+r, y+r], fill=(180, 200, 255, a))
#     return np.array(pil)



# def make_line_frame(t, width=720, height=1280):
#     img  = np.zeros((height, width, 4), dtype=np.uint8)
#     pil  = Image.fromarray(img, mode="RGBA")
#     draw = ImageDraw.Draw(pil)
#     y = int(height * 0.75 + 30 * np.sin(0.4 * t))
#     a = int(160 + 80 * np.sin(0.6 * t))
#     draw.line([(40, y), (width - 40, y)], fill=(100, 180, 255, a), width=2)
#     return np.array(pil)



# def split_into_chunks(script, chunk_size=10):
#     words = script.split()
#     return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]



# def create_dynamic_video(
#     script,
#     audio_file,
#     output_path="output/final_video.mp4",
#     width=720,
#     height=1280,
#     fps=24,
# ):
#     os.makedirs(os.path.dirname(output_path), exist_ok=True)

 
#     audio    = AudioFileClip(audio_file)
#     duration = audio.duration


#     bg_clip = VideoClip(
#         lambda t: make_gradient_frame(t, width, height),
#         duration=duration
#     ).with_fps(fps)

#     particle_clip = VideoClip(
#         lambda t: make_particles_frame(t, width, height),
#         duration=duration
#     ).with_fps(fps)


#     line_clip = VideoClip(
#         lambda t: make_line_frame(t, width, height),
#         duration=duration
#     ).with_fps(fps)

  
#     words      = script.split()
#     title_text = " ".join(words[:5]) + ("..." if len(words) > 5 else "")
#     title_clip = (
#         TextClip(
#             text=title_text,
#             font_size=52,
#             color="white",
#             size=(680, None),
#             method="caption",
#             stroke_color="cyan",
#             stroke_width=1,
#         )
#         .with_duration(min(4.0, duration))
#         .with_start(0)
#         .with_position(("center", 200))
#         .with_effects([FadeIn(0.8), FadeOut(0.6)])
#     )

#     chunks         = split_into_chunks(script, chunk_size=10)
#     chunk_duration = duration / max(len(chunks), 1)
#     text_clips     = []

#     for i, chunk in enumerate(chunks):
#         start   = i * chunk_duration
#         end     = min((i + 1) * chunk_duration, duration)
#         seg_dur = end - start

#         def pos_fn(t, cd=chunk_duration):
#             offset = 30 * max(0, 1 - t / 0.4)
#             return ("center", int(560 + offset))

#         clip = (
#             TextClip(
#                 text=chunk,
#                 font_size=38,
#                 color="white",
#                 size=(660, None),
#                 method="caption",
#             )
#             .with_duration(seg_dur)
#             .with_start(start)
#             .with_effects([FadeIn(0.35), FadeOut(0.3)])
#             .with_position(pos_fn)
#         )
#         text_clips.append(clip)

#     # ── 6. Progress bar ─────────────────────────
#     bar_h = 6
#     def make_progress_frame(t):
#         img = np.zeros((bar_h, width, 4), dtype=np.uint8)
#         filled = int((t / duration) * width)
#         img[:, :filled, 0] = 100
#         img[:, :filled, 1] = 200
#         img[:, :filled, 2] = 255
#         img[:, :filled, 3] = 220
#         return img

#     progress_clip = (
#         VideoClip(make_progress_frame, duration=duration)
#         .with_fps(fps)
#         .with_position(("left", height - bar_h - 30))
#     )

#     # ── 7. Compose & export ─────────────────────
#     all_clips = (
#         [bg_clip, particle_clip, line_clip, title_clip]
#         + text_clips
#         + [progress_clip]
#     )

#     video = CompositeVideoClip(all_clips, size=(width, height))
#     video = video.with_audio(audio)

#     video.write_videofile(
#         output_path,
#         fps=fps,
#         codec="libx264",
#         audio_codec="aac",
#         threads=4,
#         preset="fast",
#         logger=None,
#     )

#     # ── Safe cleanup ────────────────────────────
#     try:
#         audio.close()
#     except Exception:
#         pass

#     print(f" Video saved → {output_path}")
#     return output_path


import os
import numpy as np
from PIL import Image, ImageDraw

from moviepy.video.VideoClip import TextClip, VideoClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx import FadeIn, FadeOut
from moviepy.audio.io import readers as _audio_readers


#  Fix MoviePy audio bug
_original_close = _audio_readers.FFMPEG_AudioReader.close

def _safe_close(self):
    try:
        if not hasattr(self, "proc"):
            self.proc = None
        _original_close(self)
    except Exception:
        pass

_audio_readers.FFMPEG_AudioReader.close = _safe_close


#  BACKGROUND GRADIENT
def make_gradient_frame(t, width=720, height=1280):
    img = np.zeros((height, width, 3), dtype=np.uint8)
    r = int(10 + 20 * np.sin(0.3 * t))
    g = int(5  + 15 * np.sin(0.2 * t + 1))
    b = int(40 + 30 * np.sin(0.25 * t + 2))

    for y in range(height):
        ratio = y / height
        img[y, :, 0] = int(r * (1 - ratio) + 5 * ratio)
        img[y, :, 1] = int(g * (1 - ratio) + 10 * ratio)
        img[y, :, 2] = int(b * (1 - ratio) + (b + 20) * ratio)

    return img


#  PARTICLES
def make_particles_frame(t, width=720, height=1280, n=18):
    img = np.zeros((height, width, 4), dtype=np.uint8)

    rng = np.random.default_rng(42)
    xs = rng.integers(50, width - 50, size=n)
    ys = rng.integers(0, height, size=n)
    speeds = rng.uniform(30, 90, size=n)
    sizes = rng.integers(4, 14, size=n)
    phases = rng.uniform(0, 2 * np.pi, size=n)

    pil = Image.fromarray(img, mode="RGBA")
    draw = ImageDraw.Draw(pil)

    for i in range(n):
        y = int((ys[i] - speeds[i] * t) % height)
        x = int(xs[i] + 12 * np.sin(0.5 * t + phases[i]))
        r = sizes[i]
        a = int(120 + 100 * np.sin(0.8 * t + phases[i]))
        draw.ellipse([x-r, y-r, x+r, y+r], fill=(180, 200, 255, a))

    return np.array(pil)


#  LINE EFFECT
def make_line_frame(t, width=720, height=1280):
    img = np.zeros((height, width, 4), dtype=np.uint8)
    pil = Image.fromarray(img, mode="RGBA")
    draw = ImageDraw.Draw(pil)

    y = int(height * 0.75 + 30 * np.sin(0.4 * t))
    a = int(160 + 80 * np.sin(0.6 * t))

    draw.line([(40, y), (width - 40, y)], fill=(100, 180, 255, a), width=2)

    return np.array(pil)


#  TEXT SPLIT
def split_into_chunks(script, chunk_size=10):
    words = script.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]


#  MAIN FUNCTION
def create_dynamic_video(
    script,
    audio_file,
    avatar_video="output/avatar.mp4",   # 🔥 NEW
    output_path="output/final_video.mp4",
    width=720,   
    height=1280,
    fps=24,
):

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    #  AUDIO
    audio = AudioFileClip(audio_file)
    duration = audio.duration

    #  BACKGROUND
    bg_clip = VideoClip(
        lambda t: make_gradient_frame(t, width, height),
        duration=duration
    ).with_fps(fps)

    particle_clip = VideoClip(
        lambda t: make_particles_frame(t, width, height),
        duration=duration
    ).with_fps(fps)

    line_clip = VideoClip(
        lambda t: make_line_frame(t, width, height),
        duration=duration
    ).with_fps(fps)

    #  AVATAR (SadTalker output)
    avatar_clip = None
    if avatar_video and os.path.exists(avatar_video):

        avatar = VideoFileClip(avatar_video)

        avatar_clip = (
            avatar
            .resized(height=500)
            .with_start(0)
            .with_position(("center", height - 550))
            .with_duration(duration)
        )

        # Optional zoom effect
        avatar_clip = avatar_clip.resized(lambda t: 1 + 0.02 * t)

    #  TITLE
    words = script.split()
    title_text = " ".join(words[:5]) + ("..." if len(words) > 5 else "")

    title_clip = (
        TextClip(
            text=title_text,
            font_size=52,
            color="white",
            size=(680, None),
            method="caption",
            stroke_color="cyan",
            stroke_width=1,
        )
        .with_duration(min(4.0, duration))
        .with_start(0)
        .with_position(("center", 200))
        .with_effects([FadeIn(0.8), FadeOut(0.6)])
    )

    #  TEXT ANIMATION
    chunks = split_into_chunks(script, 10)
    chunk_duration = duration / max(len(chunks), 1)
    text_clips = []

    for i, chunk in enumerate(chunks):

        start = i * chunk_duration
        seg_dur = min(chunk_duration, duration - start)

        def pos_fn(t):
            offset = 30 * max(0, 1 - t / 0.4)
            return ("center", int(560 + offset))

        clip = (
            TextClip(
                text=chunk,
                font_size=38,
                color="white",
                size=(660, None),
                method="caption",
            )
            .with_duration(seg_dur)
            .with_start(start)
            .with_effects([FadeIn(0.35), FadeOut(0.3)])
            .with_position(pos_fn)
        )

        text_clips.append(clip)

    #  PROGRESS BAR
    bar_h = 6

    def make_progress_frame(t):
        img = np.zeros((bar_h, width, 4), dtype=np.uint8)
        filled = int((t / duration) * width)
        img[:, :filled] = [100, 200, 255, 220]
        return img

    progress_clip = (
        VideoClip(make_progress_frame, duration=duration)
        .with_fps(fps)
        .with_position(("left", height - bar_h - 30))
    )

    #  FINAL COMPOSITION
    all_clips = [bg_clip, particle_clip, line_clip]

    if avatar_clip:
        all_clips.append(avatar_clip)

    all_clips += [title_clip] + text_clips + [progress_clip]

    video = CompositeVideoClip(all_clips, size=(width, height))
    video = video.with_audio(audio)

    video.write_videofile(
        output_path,
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="fast",
        logger=None,
    )

    try:
        audio.close()
    except:
        pass

    print(f" Video saved → {output_path}")
    return output_path
