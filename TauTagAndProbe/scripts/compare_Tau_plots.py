import numpy as np
from PIL import Image
import matplotlib.pyplot as plt


pre_title       = "DPplots/test"
trigger_strings = ["ditau","mutau","etau","VBFditau_hi","VBFditau_lo","ditaujet"]
variables       = ["tau_pt", "tau_eta", "tau_phi"]
                  
for trigger in trigger_strings:
  print(f"setting up plots for {trigger}")
  file_string = pre_title + "_" + trigger
  set1 = np.array(Image.open(file_string + "_" + variables[0] + ".png"))
  set2 = np.array(Image.open(file_string + "_" + variables[1] + ".png"))
  set3 = np.array(Image.open(file_string + "_" + variables[2] + ".png"))

  images = [set1, set2, set3]

  fig = plt.figure(figsize=(15,5))
  for i in range(0,len(images)):
    ax = fig.add_subplot(1, 3, i+1)
    plt.imshow(images[i])
    plt.axis('off')
    plt.tight_layout()
  filename = trigger + "_collected_trigger_plots"
  print(f"saving as {filename}.png")
  plt.savefig(filename+".png")
  plt.close()

print("finished")
