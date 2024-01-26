import llama.llama_py_interface as llama
import stable.stable_diffusion_interface as stable

ll = llama.LlamaInterface()
ff = ll.generate("le scénario d'une bd en 4 cases pourrait etre")
print("ff: ", ff)
stab = stable.StableDiffusionInterface(stable.CPU, model="./stable/models/stable_diffusion-v1-5")
#stab = stable.StableDiffusionInterface(stable.CPU, model="runwayml/stable-diffusion-v1-5")
stab.generate(ff, "res.jpg")

print("we good")
