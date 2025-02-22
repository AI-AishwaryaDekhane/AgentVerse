import gradio as gr
import soundfile as sf  # For reading audio files
from uagents import Agent, Context, Model

get_spectra_address = 'agent1qg0yq4gcfqyzaz7ng20wyg4zmzpwcllscxay5n0gsq3vva3hwr346r6uaeq'

wav_path = ''  # Initialize wav_path

# Define the envelope to send the images to process agent
class initSpectraProcessing(Model):
    image_path: str

# Define the agent
agentSendWav = Agent(
    name='send_wav',
    port=5056,
    endpoint='http://localhost:5056/submit'
)

# Define the handler on which agent will work
@agentSendWav.on_event('startup')
async def startup_handler(ctx: Context):
    ctx.logger.info(f'Sending Spectrogram Image Paths for Processing...')

    # Define the Gradio interface
    iface = gr.Interface(
        fn=classify_audio_and_play,
        inputs=gr.Textbox(label="Audio File Path"),  # Textbox for file path input
        outputs=[
            gr.Audio(label="Play Audio"),  # Allow audio playback
            gr.Textbox(label="Classification Result")  # Output classification result as text
        ],
        title="Audio Deepfake Detector",
        description="Enter the file path of an audio file to play it and determine whether it is original or a deepfake."
    )
    iface.launch(share=True)
    await ctx.send(get_spectra_address, initSpectraProcessing(image_path=wav_path))

def classify_audio_and_play(file_path):
    global wav_path
    wav_path = file_path  # Assign the input to wav_path

if __name__ == '__main__':
    
    # Launch the interface
    

    # Run the agent
    agentSendWav.run()

'''
/Users/aishwaryadekhane/Desktop/My_Files/Fetch.ai/SpectraAI/train/E2tts/Donald_Trump_00421.wav
'''