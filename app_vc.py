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
    
    try:
        # Load config
        if args.config:
            config_path = args.config
        else:
            # Try default config path
            config_path = "./configs/config.yaml"
            
        if not os.path.exists(config_path):
            print(f"Warning: Config file not found at {config_path}")
            config = None
        else:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
            config = recursive_munch(config)
        
        # Load model
        print("Loading model...")
        if args.checkpoint:
            checkpoint_path = args.checkpoint
            model = load_custom_model_from_hf(checkpoint_path, device)
        else:
            # Load default model from HuggingFace
            print("Loading default model from HuggingFace...")
            model = load_custom_model_from_hf(
                "Plachta/Seed-VC",
                device
            )
        
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {e}")
        import traceback
        traceback.print_exc()
        raise

def voice_conversion(source_audio, target_voice, pitch_shift):
    """Perform voice conversion"""
    try:
        if model is None:
            return None, "Error: Model not loaded. Please restart the application."
        
        if source_audio is None:
            return None, "Error: No source audio provided"
        
        # Process audio here
        # This is a placeholder - actual implementation would depend on the model's API
        return source_audio, "Conversion completed successfully!"
    
    except Exception as e:
        return None, f"Error during conversion: {str(e)}"

def create_demo():
    """Create the Gradio demo interface"""
    with gr.Blocks() as demo:
        gr.Markdown("# Seed-VC Voice Conversion")
        gr.Markdown("Upload audio and select target voice for conversion")
        
        with gr.Row():
            with gr.Column():
                source_audio = gr.Audio(
                    label="Source Audio",
                    type="filepath"
                )
                target_voice = gr.Textbox(
                    label="Target Voice (speaker name or path)",
                    placeholder="Enter target voice..."
                )
                pitch_shift = gr.Slider(
                    minimum=-12,
                    maximum=12,
                    value=0,
                    step=1,
                    label="Pitch Shift (semitones)"
                )
                convert_btn = gr.Button("Convert", variant="primary")
            
            with gr.Column():
                output_audio = gr.Audio(label="Converted Audio")
                status_text = gr.Textbox(label="Status")
        
        convert_btn.click(
            fn=voice_conversion,
            inputs=[source_audio, target_voice, pitch_shift],
            outputs=[output_audio, status_text]
        )
        
    return demo

if __name__ == "__main__":
    print("Starting Seed-VC application...")
    print(f"Python version: {sys.version}")
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    
    try:
        # Load model
        print("Loading model...")
        load_model()
        
        # Create and launch demo
        print("Creating demo interface...")
        demo = create_demo()
        
        # Get port from environment variable (Cloud Run uses PORT env var)
        port = int(os.environ.get("PORT", 8080))
        
        print(f"Launching on port {port}...")
        demo.launch(
            server_name="0.0.0.0",
            server_port=port,
            share=args.share
        )
    except Exception as e:
        print(f"Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
