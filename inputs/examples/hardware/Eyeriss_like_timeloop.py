from zigzag.classes.hardware.architecture.memory_hierarchy import MemoryHierarchy
from zigzag.classes.hardware.architecture.memory_level import MemoryLevel
from zigzag.classes.hardware.architecture.operational_unit import Multiplier
from zigzag.classes.hardware.architecture.operational_array import MultiplierArray
from zigzag.classes.hardware.architecture.memory_instance import MemoryInstance
from zigzag.classes.hardware.architecture.accelerator import Accelerator
from zigzag.classes.hardware.architecture.core import Core


def memory_hierarchy_latency(multiplier_array):
    """Memory hierarchy variables"""
    ''' size=#bit, bw=(read bw, write bw), cost=(read word energy, write work energy) '''
    rf_weights = MemoryInstance(name="rf_weights", size=3072, r_bw=16, w_bw=16, r_cost=1.586, w_cost=1.586, area=0.3, r_port=1, w_port=1, rw_port=1, latency=1)
    rf_inputs = MemoryInstance(name="rf_inputs", size=192, r_bw=16, w_bw=16, r_cost=0.237, w_cost=0.237, area=0.95, r_port=1, w_port=1, rw_port=1, latency=1) 
    rf_outputs = MemoryInstance(name="rf_outputs", size=256, r_bw=16, w_bw=16, r_cost=0.251, w_cost=0.251, area=0.95, r_port=1, w_port=1, rw_port=1, latency=1)

    shared_buff = MemoryInstance(name="shared_buff", size=1048576, r_bw=64, w_bw=64, r_cost=75.22, w_cost=75.22, area=0.95, r_port=1, w_port=1, rw_port=1, latency=1)
    top_dram = MemoryInstance(name="top_dram", size=100000000000, r_bw=64, w_bw=64, r_cost=512, w_cost=512, area=0.95, r_port=1, w_port=1, rw_port=1, latency=1)

    memory_hierarchy_graph = MemoryHierarchy(operational_array=multiplier_array)

    '''
    fh: from high = wr_in_by_high 
    fl: from low = wr_in_by_low 
    th: to high = rd_out_to_high
    tl: to low = rd_out_to_low
    '''
    # By Convention: I1 = Inputs I2 = Weights
    memory_hierarchy_graph.add_memory(memory_instance=rf_inputs, operands=('I1',),
                                      port_alloc=({'fh': 'w_port_1', 'tl': 'r_port_1', 'fl': None, 'th': None},),
                                      served_dimensions=set())
    memory_hierarchy_graph.add_memory(memory_instance=rf_weights, operands=('I2',),
                                      port_alloc=({'fh': 'w_port_1', 'tl': 'r_port_1', 'fl': None, 'th': None},),
                                      served_dimensions=set())
    memory_hierarchy_graph.add_memory(memory_instance=rf_outputs, operands=('O',),
                                      port_alloc=({'fh': 'rw_port_1', 'tl': 'r_port_1', 'fl': 'w_port_1', 'th': 'rw_port_1'},),
                                      served_dimensions=set())

    memory_hierarchy_graph.add_memory(memory_instance=shared_buff, operands=('I1', 'O'),xe
                                      port_alloc=({'fh': 'rw_port_1', 'tl': 'rw_port_2', 'fl': None, 'th': None},
                                                  {'fh': 'rw_port_1', 'tl': 'rw_port_2', 'fl': 'rw_port_2', 'th': 'rw_port_1'},),
                                      served_dimensions='all')
    memory_hierarchy_graph.add_memory(memory_instance=top_dram, operands=('I1', 'I2', 'O'),
                                      port_alloc=({'fh': 'rw_port_1', 'tl': 'rw_port_1', 'fl': None, 'th': None},
                                                  {'fh': 'rw_port_1', 'tl': 'rw_port_1', 'fl': None, 'th': None},
                                                  {'fh': 'rw_port_1', 'tl': 'rw_port_1', 'fl': 'rw_port_1', 'th': 'rw_port_1'},),
                                      served_dimensions='all')

    # from visualization.graph.memory_hierarchy import visualize_memory_hierarchy_graph
    # visualize_memory_hierarchy_graph(memory_hierarchy_graph)
    return memory_hierarchy_graph


def multiplier_array_latency():
    """ Multiplier array variables """
    multiplier_input_precision = [16, 16]
    multiplier_energy = 0.5
    multiplier_area = 0.1
    dimensions = {'D1': 7, 'D2': 2, 'D3': 11} #{'D1': 14, 'D2': 12}
    multiplier = Multiplier(multiplier_input_precision, multiplier_energy, multiplier_area)
    multiplier_array = MultiplierArray(multiplier, dimensions)

    return multiplier_array


def cores():
    multiplier_array1 = multiplier_array_latency()
    memory_hierarchy1 = memory_hierarchy_latency(multiplier_array1)

    core1 = Core(1, multiplier_array1, memory_hierarchy1)

    return {core1}


cores = cores()
global_buffer = None
accelerator = Accelerator("Eyeriss-like-simple", cores, global_buffer)

