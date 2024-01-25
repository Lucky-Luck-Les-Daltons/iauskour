#!/usr/bin/env python3

import os
import subprocess
import threading
import select
import time
import fcntl

import yaml

CLI_ARGS_MAIN_PERPLEXITY = [
    "batch-size", "cfg-negative-prompt", "cfg-scale", "chunks", "color", "ctx-size", "escape",
    "export", "file", "frequency-penalty", "grammar", "grammar-file", "hellaswag",
    "hellaswag-tasks", "ignore-eos", "in-prefix", "in-prefix-bos", "in-suffix", "instruct",
    "interactive", "interactive-first", "keep", "logdir", "logit-bias", "lora", "lora-base",
    "low-vram", "main-gpu", "memory-f32", "mirostat", "mirostat-ent", "mirostat-lr", "mlock",
    "model", "multiline-input", "n-gpu-layers", "n-predict", "no-mmap", "no-mul-mat-q",
    "np-penalize-nl", "numa", "ppl-output-type", "ppl-stride", "presence-penalty", "prompt",
    "prompt-cache", "prompt-cache-all", "prompt-cache-ro", "random-prompt", "repeat-last-n",
    "repeat-penalty", "reverse-prompt", "rope-freq-base", "rope-freq-scale", "rope-scale", "seed",
    "simple-io", "tensor-split", "threads", "temp", "tfs", "top-k", "top-p", "typical",
    "verbose-prompt"
]

CLI_ARGS_LLAMA_BENCH = [
    "batch-size", "memory-f32", "low-vram", "model", "mul-mat-q", "n-gen", "n-gpu-layers",
    "n-prompt", "output", "repetitions", "tensor-split", "threads", "verbose"
]

CLI_ARGS_SERVER = [
    "alias", "batch-size", "ctx-size", "embedding", "host", "memory-f32", "lora", "lora-base",
    "low-vram", "main-gpu", "mlock", "model", "n-gpu-layers", "n-probs", "no-mmap", "no-mul-mat-q",
    "numa", "path", "port", "rope-freq-base", "timeout", "rope-freq-scale", "tensor-split",
    "threads", "verbose"
]

description = """Run llama.cpp binaries with presets from YAML file(s).
To specify which binary should be run, specify the "binary" property (main, perplexity, llama-bench, and server are supported).
To get a preset file template, run a llama.cpp binary with the "--logdir" CLI argument.

Formatting considerations:
- The YAML property names are the same as the CLI argument names of the corresponding binary.
- Properties must use the long name of their corresponding llama.cpp CLI arguments.
- Like the llama.cpp binaries the property names do not differentiate between hyphens and underscores.
- Flags must be defined as "<PROPERTY_NAME>: true" to be effective.
- To define the logit_bias property, the expected format is "<TOKEN_ID>: <BIAS>" in the "logit_bias" namespace.
- To define multiple "reverse_prompt" properties simultaneously the expected format is a list of strings.
- To define a tensor split, pass a list of floats.
"""


def non_block_read(output):
    fd = output.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    try:
        return output.read()
    except Exception as e:
        print(e)
        return ""

def check_pipe(pipe_name : str, callback, stop): # haaaaaaaaaaaaaaaaaaaa, oskour
    with open(pipe_name) as fifo:
        print("pipe open")
        #print(fifo.read())
        while not stop():
            #select.select([fifo],[],[fifo])
            print(f"new: <{non_block_read(fifo)}>")
            time.sleep(0.5)
        #for nextfetch in fifo:
         #   callback(nextfetch)


def start_subproc(binary, pipe_name, onend):
    sp = subprocess.run([binary, "./models/7B/ggml-model-q4_0.gguf", "my name is", pipe_name], )#stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    onend()

def launch_with_args(binary_path, yaml_args):

    props = dict()

    for yaml_file in yaml_args:
        with open(yaml_file, "r") as f:
            props.update(yaml.load(f, yaml.SafeLoader))

    props = {prop.replace("_", "-"): val for prop, val in props.items()}

    binary = props.pop("binary", "main")
    if binary_path:
        binary = binary_path

    if os.path.exists(f"./{binary}"):
        binary = f"./{binary}"

    if binary.lower().endswith("main") or binary.lower().endswith("perplexity"):
        cli_args = CLI_ARGS_MAIN_PERPLEXITY
    elif binary.lower().endswith("llama-bench"):
        cli_args = CLI_ARGS_LLAMA_BENCH
    elif binary.lower().endswith("server"):
        cli_args = CLI_ARGS_SERVER
    else:
        print(f"Unknown binary: {binary}")
        cli_args = []
        #return 1

    command_list = [binary]

    for cli_arg in cli_args:
        value = props.pop(cli_arg, None)

        if not value or value == -1:
            continue

        if cli_arg == "logit-bias":
            for token, bias in value.items():
                command_list.append("--logit-bias")
                command_list.append(f"{token}{bias:+}")
            continue

        if cli_arg == "reverse-prompt" and not isinstance(value, str):
            for rp in value:
                command_list.append("--reverse-prompt")
                command_list.append(str(rp))
            continue

        command_list.append(f"--{cli_arg}")

        if cli_arg == "tensor-split":
            command_list.append(",".join([str(v) for v in value]))
            continue

        value = str(value)

        if value != "True":
            command_list.append(str(value))

    num_unused = len(props)
    if num_unused > 10:
        print(f"The preset file contained a total of {num_unused} unused properties.")
    elif num_unused > 0:
        print("The preset file contained the following unused properties:")
        for prop, value in props.items():
            print(f"  {prop}: {value}")

    pipe_name = "/tmp/llama_pipe"

            
    full : bool = False
        
    if full:
        sp = subprocess.run([binary, "./models/7B/ggml-model-q4_0.gguf", "my name is", pipe_name], capture_output=True)
        
        if sp.returncode != 0:
            raise Exception("llama.cpp process returned an error ")
        
        return sp.stdout
    else:
        try : 
            os.remove(pipe_name)
        except FileNotFoundError:
            pass

        class GenState:
            def __init__(self):
                self.generating = False

            def switch_state(self):
                self.generating = not self.generating

        generating = GenState()
        print("id of ", id(generating))

        os.mkfifo(pipe_name)
        real_time_read = threading.Thread(target=lambda : check_pipe(pipe_name, lambda s : print("token", s), lambda: generating.generating))
        real_time_read.start()
    
        starter = threading.Thread(target=lambda: start_subproc(binary, pipe_name, onend=generating.switch_state))
        starter.start()
        
        #sp = subprocess.Popen([binary, "./models/7B/ggml-model-q4_0.gguf", "my name is", pipe_name])

        print("ending main")
        return 0
        """print("passed")
        with open(pipe_name) as fifo:
            print("pipe open")
            while True:
                select.select([fifo],[],[fifo])
                print("new: <", fifo.read(), ">")
                #time.sleep(0.5)"""



print(launch_with_args("simple", ["template.yml"]))
