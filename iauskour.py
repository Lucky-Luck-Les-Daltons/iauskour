import llama.llama_py_interface as llama
import stable.stable_diffusion_interface as stable

ll = llama.LlamaInterface()
ff = ll.generate("final fantasy 14 is free up to level 60")
print("ff: ", ff)
stab = stable.StableDiffusionInterface(stable.CPU, model="./stable/models/stable_diffusion-v1-5")
stab.generate(ff, "ff13.jpg")

print("we good")
