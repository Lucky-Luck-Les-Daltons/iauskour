import os
import threading
import time
import fcntl
import subprocess
import sys
import os


class LlamaInterface:
    def __init__(self):
        self.generating = False
        self.answer = ""
        self.prompt = None
        self.model_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "models/7B/ggml-model-q4_0.gguf")

        # intern
        self.pipe_name = "/tmp/IAuskour"+str(id(self))
        self.binary = os.path.join(os.path.dirname(os.path.realpath(__file__)), "simple")
        self._new_token_actions = [lambda t: self._add_to_answer(t)]
        self._gen_end_actions = [lambda s: self._switch_generating_state()]

    def generate_non_block(self, prompt, on_new_token=lambda s: None, on_end=lambda s: None):
        self._generate(prompt, False, on_new_token=on_new_token, on_end=on_end)

    def generate(self, prompt, on_new_token=lambda s: None, on_end=lambda s: None) -> str:
        self._generate(prompt, True, on_new_token=on_new_token, on_end=on_end)
        return self.answer

    def get_all_tokens(self):
        return self.answer

    def _generate(self, prompt, block:bool=False, on_new_token=lambda s: None, on_end=lambda s: None):
        self.prompt = prompt
        self.generating = True

        try:
            os.remove(self.pipe_name)
        except FileNotFoundError:
            pass

        os.mkfifo(self.pipe_name)

        self._new_token_actions.append(on_new_token)
        self._gen_end_actions.append(on_end)

        real_time_read = threading.Thread(target=self._check_pipe)
        real_time_read.start()

        llama_starter = threading.Thread(target=lambda: self._start_llama(onend=self._on_gen_end))
        llama_starter.start()

        if block:
            llama_starter.join()

    def _switch_generating_state(self):
        self.generating = False

    def _check_pipe(self):
        with open(self.pipe_name) as fifo:
            while self.generating:
                s = self.non_block_read(fifo)
                if s:
                    self._on_new_token(s)
                time.sleep(0.5)

    def _start_llama(self, onend):
        sp = subprocess.run([self.binary, self.model_path, self.prompt, self.pipe_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#        sp = subprocess.run([self.binary, self.model_path, self.prompt, self.pipe_name])
        onend()

    def _add_to_answer(self, str):
        self.answer += str

    def _on_new_token(self, token):
        for action in self._new_token_actions:
            action(token)

    def _on_gen_end(self):
        for action in self._gen_end_actions:
            action(self.answer)

    @staticmethod
    def non_block_read(output):
        fd = output.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        try:
            return output.read()
        except Exception as e: # https://bugs.python.org/issue13322
            return ""

"""
llint = LlamaInterface()
prompt = "top 10 walter white moments"
res =[prompt]

llint.generate_non_block(prompt, on_end=lambda s: res.append(s), on_new_token = lambda s: print("new token:", s))

while llint.generating:
    #print("full:", llint.get_all_tokens())
    time.sleep(1)

print("full:", "".join(res))
"""
