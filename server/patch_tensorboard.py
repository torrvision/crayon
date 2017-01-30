# This script should silently fail
# try:
from tensorflow.tensorboard import tensorboard
import os
import sys

if len(sys.argv) > 1:
  new_delay = sys.argv[1]
else:
  new_delay = "10"

print("Patching tensorboard to change the delay to "+new_delay+"s")

tb_path = os.path.dirname(os.path.abspath(tensorboard.__file__))
dist_path = os.path.join(tb_path, "dist")
html_path = os.path.join(dist_path, "tf-tensorboard.html")

content = []
state = 0
# state:
# 0: looking for variable name
# 1: looking for type
# 2: looking for value
# 3: finishing to read the file
with open(html_path, "r") as html_file:
  for line in html_file:
    if state == 0:
      if "autoReloadIntervalSecs:" in line:
        state = 1
    elif state == 1:
      if "type: Number" in line:
        state = 2
      else:
        print("This should not happen, trying to find a new instance")
        state = 0
    elif state == 2:
      if "value: 120" in line:
        line = line.replace("120", new_delay)
        state = 3
      else:
        print("This should not happen, trying to find a new instance")
        state = 0
    elif state == 3:
      pass
    else:
        print("This should not happen, trying to find a new instance")
        state = 0

    content += [line]

with open(html_path, "w") as html_file:
  html_file.write("\n".join(content))

print("Success !")

# except:
#   print("Tensorboard patching failed")