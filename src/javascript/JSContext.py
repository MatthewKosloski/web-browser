import dukpy
import os

class JSContext:

    def __init__(self):
        runtime_file = os.path.join(os.path.dirname(__file__), "runtime.js")
        self.runtime = open(runtime_file).read()
        self.interp = dukpy.JSInterpreter()

        self.interp.evaljs(self.runtime)

        self.interp.export_function("log", print)

    def run(self, code: str):
        try:
            return self.interp.evaljs(code)
        except dukpy.JSRuntimeError as e:
            print("Script crashed", e)
