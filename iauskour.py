import llama.llama_py_interface as llama
import stable.stable_diffusion_interface as stable

ll = llama.LlamaInterface()
ff = ll.generate("Récit pour enfant, Agathe est la reine des neiges")
print("ff: ", ff)
#stab = stable.StableDiffusionInterface(stable.CPU, model="./stable/models/stable_diffusion-v1-5")
stab = stable.StableDiffusionInterface(stable.CPU, model="runwayml/stable-diffusion-v1-5")
stab.generate(ff, "res.jpg")

print("we good")
