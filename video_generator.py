import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
from moviepy import VideoClip, AudioFileClip, VideoFileClip
import math

os.environ['FFMPEG_BINARY'] = imageio_ffmpeg.get_ffmpeg_exe()

def make_frame(text, w, h, t, char_idx, lines_data):
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(h):
        r = int(25 * (y / h))
        arr[y] = [r, r // 2, r + 40]
    img = Image.fromarray(arr)
    draw = ImageDraw.Draw(img)
    
    cx = w // 2
    b = int(12 * math.sin(t * 4))
    s = int(5 * math.sin(t * 3))
    
    colors = [(255, 105, 180), (100, 200, 255), (255, 215, 0), (50, 255, 150), (200, 100, 255)]
    c = colors[char_idx % len(colors)]
    
    hy = 100 + b
    hr = 30
    
    draw.ellipse([cx-hr+s, hy-hr, cx+hr+s, hy+hr], c)
    draw.ellipse([cx-hr+s-3, hy-hr-3, cx+hr+s-3, hy+hr-3], outline=(255, 255, 255), width=2)
    
    for side in [-1, 1]:
        ex = cx + side * 10 + s
        draw.ellipse([ex-6, hy-8, ex+6, hy+3], (255, 255, 255))
        draw.ellipse([ex-3, hy-5, ex+3, hy+1], (0, 0, 0))
    
    draw.ellipse([cx-4, hy+2, cx+4, hy+7], (255, 150, 150))
    for side in [-1, 1]:
        draw.ellipse([cx+side*18+s-3, hy+2, cx+side*18+s+3, hy+7], (255, 150, 150))
    
    my = hy + 12
    mouth_open = int(5 + 3 * abs(math.sin(t * 4)))
    draw.arc([cx-8+s, my, cx+8+s, my+mouth_open+6], 0, 180, (255, 100, 100), width=2)
    
    by = hy + hr
    bw = 22
    bh = 28
    
    draw.rectangle([cx-bw//2+s, by, cx+bw//2+s, by+bh], c)
    
    w1 = int(18 * math.sin(t * 5))
    w2 = int(18 * math.sin(t * 5 + math.pi))
    
    draw.line([cx-bw//2+s, by+10, cx-bw//2-22+s+w2, by-10], c, width=8)
    draw.ellipse([cx-bw//2-28+s+w2, by-18, cx-bw//2-18+s+w2, by-6], c)
    draw.line([cx+bw//2+s, by+10, cx+bw//2+22+s+w1, by-10], c, width=8)
    draw.ellipse([cx+bw//2+18+s+w1, by-18, cx+bw//2+28+s+w1, by-6], c)
    
    word_colors = [(255, 255, 0), (0, 255, 255), (255, 100, 255), (100, 255, 100), (255, 200, 50), (255, 50, 100)]
    
    y_start = 240
    
    for i, (line, delay, duration) in enumerate(lines_data):
        elapsed = t - delay
        
        if elapsed > 0:
            if elapsed < 0.4:
                prog = elapsed / 0.4
                bounce = abs(math.sin(prog * math.pi)) * 15
                scale = 0.3 + 0.7 * prog
                alpha = int(255 * prog)
            elif elapsed > duration - 0.3:
                remaining = elapsed - (duration - 0.3)
                prog = remaining / 0.3
                bounce = 0
                scale = 1.0
                alpha = int(255 * (1 - prog))
            else:
                bounce = 0
                scale = 1.0
                alpha = 255
            
            try:
                font_s = ImageFont.truetype("arial.ttf", int(32 * scale))
            except:
                font_s = ImageFont.load_default(size=int(32 * scale))
            
            bbox = draw.textbbox((0, 0), line, font=font_s)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            
            x = (w - tw) // 2
            y = y_start + i * 48 + int(bounce)
            
            col = word_colors[i % len(word_colors)]
            
            for gl in range(8, 0, -1):
                gc = tuple(min(255, max(0, c + gl * 12)) for c in col)
                draw.text((x, y), line, font=font_s, fill=gc)
            
            draw.text((x+2, y+2), line, font=font_s, fill=(20, 10, 50))
            draw.text((x, y), line, font=font_s, fill=col)
            draw.text((x, y), line, font=font_s, fill=(255, 255, 255, alpha))
            
            for sp in range(4):
                sx = x + tw + int(20 * math.sin(t * 5 + sp + i))
                sy = y + th // 2 + int(15 * math.cos(t * 4 + sp * 2))
                sz = 3 + int(3 * math.sin(t * 6 + sp))
                draw.ellipse([sx-sz, sy-sz, sx+sz, sy+sz], (255, 255, 100, int(alpha * 0.8)))
    
    return np.array(img)

def create_video(text, audio_file, output_path="output/final.mp4", w=720, h=1280, fps=18):
    os.makedirs(os.path.dirname(output_path) or "output", exist_ok=True)
    
    audio_dur = 5
    
    if audio_file and os.path.exists(audio_file):
        try:
            try:
                import wave
                with wave.open(audio_file, 'rb') as wf:
                    nframes = wf.getnframes()
                    framerate = wf.getframerate()
                    if nframes > 0 and framerate > 0:
                        audio_dur = nframes / framerate
                        audio_dur = audio_dur / 1.15
                        print(f"Audio duration: {audio_dur:.2f}s")
            except:
                try:
                    audio_clip = AudioFileClip(audio_file)
                    audio_dur = audio_clip.duration
                    audio_dur = audio_dur / 1.15
                    audio_clip.close()
                    print(f"Audio duration: {audio_dur:.2f}s")
                except:
                    print("Using default audio duration: 5s")
        except Exception as e:
            print(f"Audio duration error: {e}")
            audio_dur = 5
    
    try:
        char_idx = int(hash(text)) % 5
        
        raw_lines = text.replace('"', '').replace('!', '.').replace('?', '.').split('.')
        sentences = [line.strip() for line in raw_lines if line.strip()]
        
        if not sentences:
            sentences = [text[:50]]
        
        final_lines = []
        for sentence in sentences:
            words = sentence.split()
            for i in range(0, len(words), 3):
                chunk = ' '.join(words[i:i+3])
                if chunk:
                    final_lines.append(chunk)
        
        if not final_lines:
            final_lines = [text[:30]]
        
        total_duration = audio_dur if audio_dur > 0 else 2
        line_duration = total_duration / max(len(final_lines), 1)
        
        lines_data = []
        for i, line in enumerate(final_lines):
            delay = i * line_duration
            duration = line_duration
            lines_data.append((line, delay, duration))
        
        print(f"Generating video: {total_duration:.2f}s, {len(lines_data)} lines")
        
        clip = VideoClip(lambda t: make_frame(text, w, h, t, char_idx, lines_data), duration=total_duration).with_fps(fps)
        
        temp_video = output_path.replace('.mp4', '_novid.mp4')
        clip.write_videofile(temp_video, fps=fps, codec='libx264', preset='fast', logger=None)
        
        if not os.path.exists(temp_video):
            print("Video generation failed")
            return None
        
        try:
            import subprocess
            import imageio_ffmpeg
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
            
            result = subprocess.run(
                [ffmpeg, '-y', '-i', temp_video, '-i', audio_file, 
                 '-filter:a', 'atempo=1.15',
                 '-c:v', 'copy', '-c:a', 'aac', '-shortest', output_path],
                capture_output=True, timeout=120
            )
            print(f"FFmpeg result: {result.returncode}")
        except Exception as e:
            print(f"Audio merge error: {e}")
            try:
                import shutil
                shutil.copy(temp_video, output_path)
            except:
                pass
        
        if os.path.exists(temp_video):
            try:
                os.remove(temp_video)
            except:
                pass
        
        if os.path.exists(output_path):
            print(f"Final video created: {output_path}")
            return output_path
        else:
            print("Failed to create final video")
            return None
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_dynamic_video(script, audio_file, output_path="output/final_video.mp4", width=720, height=1280, fps=18):
    return create_video(script, audio_file, output_path, width, height, fps)