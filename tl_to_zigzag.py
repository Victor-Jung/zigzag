#   =====================================================================
#   Title:        tl_to_zigzag.py
#   Description: This file contains the engine class that handles the 
#   optimization of temporal mapping of SALSA.
#  
#   Date:        17.01.2023
#  
#   =====================================================================
# 
#   Copyright (C) 2020 ETH Zurich and University of Bologna.
#  
#   Author: Victor Jung, ETH Zurich
#  
#   SPDX-License-Identifier: Apache-2.0
#  
#   Licensed under the Apache License, Version 2.0 (the License); you may
#   not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#  
#   www.apache.org/licenses/LICENSE-2.0
#  
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an AS IS BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


import sys
import os
import importlib
import inspect
import subprocess


tl_mapping_folder_path = "../salsa_benchmark/tl_to_zz_benchmark/alexnet_timeloop_output/"
tl_mapping_file_name = "alexnet_1.map.txt"

tl_to_zz_notation = {'C': 'C', 'M': 'K', 'N': 'B', 'P': 'OX', 'Q': 'OY', 'R': 'FX', 'S': 'FY'}
temporal_mapping = {"DRAM": [], "shared_glb": [], "DummyBuffer": [], "ifmap_spad": [], "weights_spad": [], "psum_spad": []}
spatial_mapping = {}
memory_level = ""
spatial_dimension_counter = 1

### Extract the Temporal and Spatial Mapping from the timeloop output
with open(tl_mapping_folder_path + tl_mapping_file_name, "r") as f:
    lines = f.readlines()
    for line in lines:
        if 'for' in line:

            is_spatial = (line.find("Spatial") != -1)
            loop_idx = line[line.find("for")+4]
            loop_size = line[line.find(":")+1:line.find(")")]
            if is_spatial:
                spatial_mapping["D" + str(spatial_dimension_counter)] = (tl_to_zz_notation[loop_idx], int(loop_size))
                spatial_dimension_counter += 1
            else:
                temporal_mapping[memory_level].append((tl_to_zz_notation[loop_idx], int(loop_size)))

            print("loop_idx:", loop_idx)
            print("loop_size:", loop_size)
            print("is_spatial:", is_spatial)

        elif line.find("]") != -1:
            memory_level = line[:line.find("[")-1]
            print("memory_level:", memory_level)



print("temporal_mapping:", temporal_mapping)
print("spatial_mapping:", spatial_mapping)

### Convert the temporal mapping to zigzag format
temporal_mapping_dict = {"I": [[], [], []], "W": [[], []], "O": [[], [], []]}

temporal_mapping_dict["I"][2] += temporal_mapping["DRAM"]
temporal_mapping_dict["W"][1] += temporal_mapping["DRAM"]
temporal_mapping_dict["O"][2] += temporal_mapping["DRAM"]

temporal_mapping_dict["W"][1] += temporal_mapping["shared_glb"] # since it can't hold weights

temporal_mapping_dict["I"][1] += temporal_mapping["shared_glb"]
temporal_mapping_dict["O"][1] += temporal_mapping["shared_glb"]

temporal_mapping_dict["W"][1] += temporal_mapping["ifmap_spad"]
temporal_mapping_dict["O"][1] += temporal_mapping["ifmap_spad"] + temporal_mapping["weights_spad"]

temporal_mapping_dict["I"][0] += temporal_mapping["ifmap_spad"] + temporal_mapping["weights_spad"] + temporal_mapping["psum_spad"]
temporal_mapping_dict["W"][0] += temporal_mapping["weights_spad"] + temporal_mapping["psum_spad"]
temporal_mapping_dict["O"][0] += temporal_mapping["psum_spad"]

for level_idx in range(len(temporal_mapping_dict["I"])):
    temporal_mapping_dict["I"][level_idx] = temporal_mapping_dict["I"][level_idx][::-1]
for level_idx in range(len(temporal_mapping_dict["W"])):
    temporal_mapping_dict["W"][level_idx] = temporal_mapping_dict["W"][level_idx][::-1]
for level_idx in range(len(temporal_mapping_dict["O"])):
    temporal_mapping_dict["O"][level_idx] = temporal_mapping_dict["O"][level_idx][::-1]

print("temporal_mapping_dict:\n\tI: ", temporal_mapping_dict["I"], "\n\tW: ", temporal_mapping_dict["W"], "\n\tO: ", temporal_mapping_dict["O"], "\n\t")



### Inject the temporal and spatial mapping into the zigzag workload input file
print(f"Overwritting Input File")

# from inputs.examples.workloads.alexnet_l1_copy import workload
# print(alexnet_l1_copy)
module_path = "inputs.examples.workloads.alexnet_l1_copy"
module = importlib.import_module(module_path)
spec = importlib.util.find_spec(module_path)
source = inspect.getsource(module)

tm_source = source[source.find("temporal_mapping")-1:source.find("spatial_mapping")-1]
new_tm_source = "'temporal_mapping': " + str(temporal_mapping_dict) + ",\n\t\t"
modified_source = source.replace(tm_source, new_tm_source)

sm_source = source[source.find("spatial_mapping")-1:source.find("memory_operand_links")-1]
new_sm_source = "'spatial_mapping': " + str(spatial_mapping) + ",\n\t\t"
modified_source = modified_source.replace(sm_source, new_sm_source)

with open(spec.origin, "w") as f:
    f.write(modified_source)



### Inject the spatial mapping into the zigzag architecture input file
print(f"Overwritting Architecture File")

for dim_idx in spatial_mapping.keys():
    spatial_mapping[dim_idx] = spatial_mapping[dim_idx][1]

arch_module_path = "inputs.examples.hardware.Eyeriss_like_timeloop"
arch_module = importlib.import_module(arch_module_path)
arch_spec = importlib.util.find_spec(arch_module_path)
source = inspect.getsource(arch_module)

old_source = source[source.find("spatial_dimension"):source.find("multiplier = Multiplier")]
new_source = "spatial_dimension = " + str(spatial_mapping) + "\n    "
modified_source = source.replace(old_source, new_source)

with open(arch_spec.origin, "w") as f:
    f.write(modified_source)

print("Evaluating the Timeloop Mapping")
bashCommand = "python main_fixed.py --workload inputs.examples.workloads.alexnet_l1_copy --accelerator inputs.examples.hardware.Eyeriss_like_timeloop"
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
print("")

print("Starting SALSA Run")
bashCommand = "python main_salsa.py --workload inputs.examples.workloads.alexnet_l1_copy --accelerator inputs.examples.hardware.Eyeriss_like_timeloop"
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
print("")