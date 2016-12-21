import os
import compileall

current_path = os.path.dirname(os.path.abspath(__file__))

compileall.compile_dir(os.path.join(current_path,"tools"), force=True)