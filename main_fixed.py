from zigzag.classes.stages import *
import argparse

# Parse the workload and accelerator arguments
parser = argparse.ArgumentParser(description="Setup zigzag-v2 inputs")
parser.add_argument('--workload', metavar='path', required=True, help='module path to workload, e.g. inputs.examples.workload1')
parser.add_argument('--accelerator', metavar='path', required=True, help='module path to the accelerator, e.g. inputs.examples.accelerator1')
args = parser.parse_args()

# Initialize the logger
import logging as _logging
_logging_level = _logging.INFO
_logging_format = '%(asctime)s - %(name)s.%(funcName)s +%(lineno)s - %(levelname)s - %(message)s'
_logging.basicConfig(level=_logging_level,
                     format=_logging_format)

# Initialize the MainStage which will start execution.
# The first argument of this init is the list of stages that will be executed in sequence.
# The second argument of this init are the arguments required for these different stages.
mainstage = MainStage([
    WorkloadAndAcceleratorParserStage,
    CompleteSaveStage,
    WorkloadStage,
    SpatialMappingGeneratorStage,
    MinimalLatencyStage,
    TemporalMappingConversionStage,  # Converts the temporal ordering into a temporal mapping (TM)
    CostModelStage
],
    accelerator_path=args.accelerator,
    workload_path=args.workload,
    dump_filename_pattern="outputs_workshop/{datetime}.json",
    plot_filename_pattern="outputs_workshop/temporal_mappings.png",
    loma_lpf_limit=6,
    loma_show_progress_bar=True,  # shows a progress bar while iterating over temporal mappings
    salsa_iteration_number=1000,
    salsa_start_temperature=0.05,
    salsa_opt_criterion="latency",
    salsa_number_of_core=8
)

# Launch the MainStage
mainstage.run()