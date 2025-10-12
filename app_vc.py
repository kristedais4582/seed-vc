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
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            config = recursive_munch(config)
            print(f"Config loaded from {config_path}")
        else:
            print(f"Config file not found at {config_path}, using default HF model")
            config = None
        
        # Load model
        if args.checkpoint:
            checkpoint_path = args.checkpoint
            model = load_custom_model_from_hf(checkpoint_path, device, fp16=args.fp16)
        else:
            # Use default model from HuggingFace
            model = load_custom_model_from_hf(
                "Plachta/Seed-VC",
                device,
                fp16=args.fp16
            )
        
        # Validate that model is actually a model object and not a string or error
        if model is None:
            raise ValueError("Model loading failed: model is None")
        
        if isinstance(model, str):
            raise ValueError(f"Model loading failed: {model}")
        
        # Only move model to device if it's a valid model object
        if hasattr(model, 'to'):
            model = model.to(device)
            if args.fp16 and device.type == "cuda":
                model = model.half()
            model.eval()
            print("Model loaded successfully!")
        else:
            raise ValueError("Model object does not have 'to' method")
            
    except Exception as e:
        print(f"Error loading model: {e}")
        print(f"Full error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    
    return model, config

def voice_conversion(source_audio, target_voice, pitch_shift=0):
    """Perform voice conversion"""
    try:
        if model is None:
            return None, "Model not loaded. Please restart the application."
        
        # Placeholder for actual voice conversion logic
        # This would need to be implemented based on the Seed-VC model API
        return source_audio, "Voice conversion not yet implemented"
    
    except Exception as e:
        return None, f"Error during conversion: {str(e)}"

def create_demo():
    """Create Gradio demo interface"""
    with gr.Blocks(title="Seed-VC Voice Conversion") as demo:
        gr.Markdown("# Seed-VC Voice Conversion Demo")
        gr.Markdown("Upload a source audio and select a target voice for conversion.")
        
        with gr.Row():
            with gr.Column():
                source_audio = gr.Audio(label="Source Audio", type="filepath")
                target_voice = gr.Textbox(label="Target Voice (speaker ID or path)")
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
