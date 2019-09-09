import glob
import subprocess

filelist = glob.glob("./notebook/*.ipynb")
for i in filelist:
    subprocess.run(["jupyter", "nbconvert", "--output-dir='./note_py'", "--to", "script", i])
    
