# This script should silently fail
from tensorflow.tensorboard import tensorboard
import os
import sys

import argparse
parser = argparse.ArgumentParser(description="Backend server for crayon")
parser.add_argument("frontend_reload", type=int,
          help="Frontend reload value")
parser.add_argument("backend_reload", type=float,
          help="How fast is tensorboard reloading its backend")
cli_args = parser.parse_args()

frontend_reload = str(cli_args.frontend_reload)
backend_reload = str(cli_args.backend_reload)


tb_path = os.path.dirname(os.path.abspath(tensorboard.__file__))

frontend_worked = False
try:
  print("Patching tensorboard to change the delay to "+frontend_reload+"s")

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
          line = line.replace("120", frontend_reload)
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

  frontend_worked = True
  print("Success !")
except:
  print("Patching failed")

backend_worked = False
try:
  print("Patching tensorboard to change backend reload to float.")

  tensorboard_path = os.path.join(tb_path, "tensorboard.py")

  content = []
  with open(tensorboard_path, "r") as source_file:
    for line in source_file:
      if ("DEFINE_integer" in line) and ("reload_interval" in line):
        line = line.replace("DEFINE_integer", "DEFINE_float")
      content += [line]

  with open(tensorboard_path, "w") as source_file:
    source_file.write("\n".join(content))

  backend_worked = True
  print("Success !")
except:
  print("Patching failed")

if backend_worked:
  if frontend_worked:
    # Both worked, return 3
    sys.exit(3)
  else:
    # Only backend worked, return 2
    sys.exit(2)
elif frontend_worked:
  # Only frontend worked, return 1
  sys.exit(1)
else:
  # Nothing worked, return -1
  sys.exit(-1)
