import os
import librosa
import numpy as np
import librosa.display
import matplotlib.pyplot as plt
import argparse
from uagents import Agent, Context, Model

destination_folder = '/Users/aishwaryadekhane/Desktop/My_Files/Fetch.ai/SpectraAI/temp'

# Constants
DATA_DIR = '/Users/aishwaryadekhane/Desktop/My_Files/RA/Spectrogram/Laundering_attack_dataset/Donald_Trump_v2/train/Original'
SPEAKER_NAME = 'DonaldTrump_v2'
TRAIN = 'train'
TEST = 'test'
DEEPFAKE = 'E2tts_img'
ORIGINAL = 'original_img'

# Global variables
img_paths = ''

# Define the envelope to send the images to process agent
class initSpectraProcessing(Model):
    image_path:str

# Define the agent
agentGetSpectra = Agent(
    name='get_spectra',
    port=5053,
    endpoint='http://localhost:5053/submit'
)

spectraProcessingAgentAddress = 'agent1qggxwc0fkfeuhkc5qleyw9r59gt6uwm38vy9uj7tqxnf2e85qkyhv8he8n6'

# Define the handler on which agent will work
@agentGetSpectra.on_event('startup')
async def startup_handler(ctx: Context):
    ctx.logger.info(f'Sending Spectrogram Image Paths for Processing...')

@agentGetSpectra.on_message(model = initSpectraProcessing)
async def message_handler(ctx:Context, sender:str, img_info:initSpectraProcessing):
    global img_paths

    #get the confirmation over how many images got tranfered and from whom
    ctx.logger.info(f'I have received the message from {sender}')
    ctx.logger.info(f'We have received {img_info.image_path} image.')
    
    wav_path = img_info.image_path
    print(f'*************{wav_path}')

    process_wav_file(wav_path, destination_folder, 100)

    await ctx.send(spectraProcessingAgentAddress, initSpectraProcessing(image_path=img_paths))

# Function to plot and save spectrogram
def plot_spectrogram(audio_path, save_path, dpi=300):
    # Load the audio file
    y, sr = librosa.load(audio_path, sr=None)

    # Compute the Short-Time Fourier Transform (STFT)
    D = np.abs(librosa.stft(y, n_fft=2048, hop_length=512))

    # Convert to dB (log scale)
    S_db = librosa.amplitude_to_db(D, ref=np.max)

    # Plot spectrogram
    plt.figure(figsize=(10, 5), dpi=dpi)
    librosa.display.specshow(S_db, sr=sr, hop_length=512, x_axis='time', y_axis='log', cmap='magma')

    # Save as RGB image
    plt.axis('off')  # Remove axis for saving as an image
    plt.savefig(save_path, bbox_inches='tight', pad_inches=0, format='png')
    plt.close()

# Function to process the wav file
def process_wav_file(file_name, destination_folder, dpi=100):
    global img_paths
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    audio_path = file_name
    img_paths = os.path.join(destination_folder, os.path.basename(file_name).replace(".wav", ".png"))

    # Plot and save spectrogram for the wav file
    plot_spectrogram(audio_path, img_paths, dpi=dpi)
    print(f"Saved spectrogram for {file_name} at {img_paths}")

if __name__ == '__main__':
    
    # Run the agent
    agentGetSpectra.run()
