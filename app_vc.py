import os
import argparse
import gradio as gr

parser = argparse.ArgumentParser()
parser.add_argument("--share", type=bool, default=False)
args = parser.parse_args()

def dummy_fn(x):
    return f"Hello, {x}!"

gr.Interface(
    fn=dummy_fn,
    inputs="text",
    outputs="text",
    title="Voice Conversion App"
).launch(
    server_name="0.0.0.0",
    server_port=int(os.environ.get("PORT", 8080)),
    share=args.share
)
