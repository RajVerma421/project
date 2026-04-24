#//Source Code//
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
import torch
import soundfile as sf
import numpy as np
import os
import subprocess

print("Loading TTS model...")

try:
    processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
    model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
    vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")
    
    embeddings_path = "static/speaker_embeddings.npy"
    if os.path.exists(embeddings_path):
        emb = np.load(embeddings_path)
        emb = np.asarray(emb).flatten()[:512]
        speaker_embeddings = torch.from_numpy(emb).float().unsqueeze(0)
    else:
        speaker_embeddings = torch.randn(1, 512)
    
    use_neural = True
    print("Neural TTS Ready!")
except Exception as e:
    print(f"Neural TTS failed: {e}, using gTTS")
    use_neural = False

def text_to_speech(text, filename=None, use_gtts=True):
    if not text or not text.strip():
        raise ValueError("No text to speak")
    
    if filename is None:
        filename = "static/audio/output.mp3"
    
    folder = os.path.dirname(filename)
    if folder:
        os.makedirs(folder, exist_ok=True)
    
    if use_gtts or not use_neural:
        from gtts import gTTS
        import re
        text = text.strip()
        if not text:
            raise ValueError("No text to speak")
        
        def num_to_words(match):
            num = int(match.group())
            ones = ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
            teens = ['ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen']
            tens = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
            
            if num < 10:
                return ones[num]
            elif num < 20:
                return teens[num - 10]
            elif num < 100:
                return tens[num // 10] + ('' if num % 10 == 0 else ' ' + ones[num % 10])
            return str(num)
        
        text = re.sub(r'\b\d+\b', lambda m: num_to_words(m), text)
        
        filename = filename.replace('.wav', '.mp3')
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(filename)
        return filename
    
    inputs = processor(text=text, return_tensors="pt")

    speech = model.generate_speech(
        inputs["input_ids"],
        speaker_embeddings,
        vocoder=vocoder
    )

    sf.write(filename, speech.numpy(), samplerate=16000)

    return filename
