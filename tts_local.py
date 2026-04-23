
import os
import torch
import soundfile as sf
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan

print("Loading TTS model...")

processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

speaker_embeddings = torch.randn(1, 512)

print("TTS Ready!")

def text_to_speech(text, filename="output/audio/output.wav"):

    #  Ensure folder exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    #  Clean text (important)
    text = text.replace("\n", ". ")

    inputs = processor(text=text, return_tensors="pt")

    speech = model.generate_speech(
        inputs["input_ids"],
        speaker_embeddings,
        vocoder=vocoder
    )

    #  Save using filename (NOT hardcoded)
    sf.write(filename, speech.numpy(), samplerate=16000)

    return filename 