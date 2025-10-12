import os
import sys
import argparse
import torch
import gradio as gr
import numpy as np
from pathlib import Path

# Import the voice conversion model components
try:
    from modules.commons import recursive_munch
    import yaml
    from hf_utils import load_custom_model_from_hf
    import soundfile as sf
except ImportError as e:
    print(f"Warning: Some imports failed: {e}")
    print("Make sure all dependencies are installed")

parser = argparse.ArgumentParser()
parser.add_argument("--share", type=bool, default=False)
parser.add_argument("--checkpoint", type=str, default="")
parser.add_argument("--config", type=str, default="")
parser.add_argument("--fp16", type=bool, default=True)
args = parser.parse_args()

# Global variables
model = None
config = None
device = None

def load_model():
    """Load the voice conversion model"""
    global model, config, device
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Load default model from HuggingFace if not specified
    if not args.checkpoint or not args.config:
        print("Loading default model from HuggingFace...")
        try:
            from hf_utils import load_custom_model_from_hf
            model, config = load_custom_model_from_hf(
                "Plachta/Seed-VC",
                "DiT_seed_v2_uvit_whisper_small_wavenet_bigvgan_pruned.pth",
                "config_dit_mel_seed_uvit_whisper_small_wavenet.yml"
            )
        except Exception as e:
            print(f"Error loading model: {e}")
            return None, None
    else:
        # Load custom model
        print(f"Loading custom model from {args.checkpoint}")
        try:
            with open(args.config) as f:
                config = yaml.safe_load(f)
            config = recursive_munch(config)
            model = torch.load(args.checkpoint, map_location=device)
        except Exception as e:
            print(f"Error loading custom model: {e}")
            return None, None
    
    if model:
        model = model.to(device)
        if args.fp16:
            model = model.half()
        model.eval()
    
    return model, config

def voice_conversion(source_audio, target_audio, diffusion_steps=25, length_adjust=1.0, inference_cfg_rate=0.7):
    """Perform voice conversion"""
    try:
        if model is None:
            return None, "Model not loaded. Please check the logs."
        
        # This is a simplified version - actual implementation would call inference functions
        return None, "Voice conversion functionality is being prepared. Please use the command line interface for now."
    except Exception as e:
        return None, f"Error during conversion: {str(e)}"

# Initialize model on startup
print("Initializing voice conversion model...")
model, config = load_model()

if model is None:
    print("Warning: Model failed to load. The app will run but conversions will not work.")

# Create Gradio interface
with gr.Blocks(title="Seed-VC Voice Conversion") as demo:
    gr.Markdown("# Seed-VC Voice Conversion")
    gr.Markdown("Upload source and target audio files for zero-shot voice conversion.")
    
    with gr.Row():
        with gr.Column():
            source_audio = gr.Audio(label="Source Audio (audio to convert)", type="filepath")
            target_audio = gr.Audio(label="Target Audio (reference voice)", type="filepath")
        
        with gr.Column():
            output_audio = gr.Audio(label="Converted Audio", type="filepath")
            status_text = gr.Textbox(label="Status", interactive=False)
    
    with gr.Row():
        diffusion_steps = gr.Slider(minimum=4, maximum=50, value=25, step=1, label="Diffusion Steps")
        length_adjust = gr.Slider(minimum=0.5, maximum=2.0, value=1.0, step=0.1, label="Length Adjust")
        inference_cfg_rate = gr.Slider(minimum=0.0, maximum=1.0, value=0.7, step=0.1, label="Inference CFG Rate")
    
    convert_btn = gr.Button("Convert Voice", variant="primary")
    convert_btn.click(
        fn=voice_conversion,
        inputs=[source_audio, target_audio, diffusion_steps, length_adjust, inference_cfg_rate],
        outputs=[output_audio, status_text]
    )
    
    gr.Markdown("---")
    gr.Markdown("### Note")
    gr.Markdown("For full functionality, please ensure all model files are downloaded and dependencies are installed.")
    gr.Markdown("For production use, consider using the command-line inference script.")

# Launch the app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting Gradio server on port {port}...")
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=args.share,
        show_error=True
    )
