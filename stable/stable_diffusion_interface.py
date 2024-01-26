from diffusers import StableDiffusionPipeline
import torch
import os

CPU = "cpu"
GPU_CUDA = "cuda"

class StableDiffusionInterface:
    def __init__(self, target, model=None):
        self.target = target
        
        if model:
            self.pipe = StableDiffusionPipeline.from_pretrained(model).to(target)
        else:
            default = get_default_model()
            self.pipe = StableDiffusionPipeline.from_pretrained(default).to(target)
            
                
        
    def generate(self, prompt, dest_path, height=None, width=None):
        
        if width and height:
            img = self.pipe(prompt, width=width, height=height).images[0]
        else:    
            img = self.pipe(prompt).images[0]
        
        img.save(dest_path)



default = "dreamlike-art/dreamlike-photoreal-2.0"
models_dir = "models"
def get_default_model():
    try:
        entries = os.listdir(models_dir)

        subdirectories = [entry for entry in entries if os.path.isdir(os.path.join(models_dir, entry))]

        if subdirectories:
            return os.path.join(models_dir, subdirectories[0])
        else:
            return default

    except OSError as e:
        print(f"get_default_model Error: {e}")
        return default

