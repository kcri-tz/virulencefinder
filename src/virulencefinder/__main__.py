from __future__ import division
import sys
import os
import json
from .helper_scripts.file_transformations_ import *
from .helper_scripts.software_executions import get_software_exec_res
from .helper_scripts.alignment_ import *
from .helper_scripts.parser import collect_args
from .helper_scripts.old_json_results import json_old
from .helper_scripts.create_table import make_table
from .__init__ import __version__
from .cge.process_results_json import VirulenceFinderResultHandler
from cgelib.output.result import Result
from .cge.config import Config
from cgecore.blaster import Blaster
from cgecore.cgefinder import CGEFinder

if __name__ == "__main__":
    version = __version__

    args, parser = collect_args()

    conf = Config(args)
    
    if args.quiet:
        f = open('/dev/null', 'w')
        sys.stdout = f
    
    # Call appropriate method (kma or blastn) based on file format
    if conf.kma:
        # Call KMA
        method_obj = CGEFinder.kma(conf.inputfastq_1, conf.outPath_kma, conf.databases, conf.db_path_vir_kma,
                                min_cov=conf.min_cov, threshold=conf.min_id,
                                kma_path=conf.kma, sample_name=conf.sample_name,
                                inputfile_2=conf.inputfastq_2, kma_mrs=0.75,
                                kma_gapopen=-5, kma_gapextend=-1,
                                kma_penalty=-3, kma_reward=1)
    elif conf.blast:
        # Call BLASTn
        method_obj = Blaster(conf.inputfasta, conf.databases, conf.db_path_vir, conf.outPath_blast,
                            conf.min_cov, conf.min_id, conf.blast, cut_off=False,
                            allowed_overlap=conf.overlap)
    else:
        sys.exit("Input file must be fastq or fasta format.")

    results = method_obj.results
    
    std_result = Result.init_software_result(
        name="VirulenceFinder",
        gitdir=f"{conf.virulence_finder_root}/../../"
        )

    init_result_data = {
        "software_version": __version__,
        "key": f"VirulenceFinder-{__version__}",
    }
    
    std_result.init_database("VirulenceFinder", conf.db_path_vir)

    VirulenceFinderResultHandler.standardize_results(
        res_collection=std_result,
        results = results,
        conf=conf)

    std_result.add_class(cl = "software_executions",
                        **get_software_exec_res(conf))
        
    if (conf.out_json):
        std_result_file = conf.out_json
    else:
        std_result_file = "{}/{}.json".format(
            conf.outputPath, conf.sample_name.replace("_R1", "").split(".")[0])

    with open(std_result_file, 'w') as fh:
        fh.write(std_result.json_dumps())
    
    service = os.path.basename(__file__).replace(".py", "")

    if conf.inputfasta:
        infiles = conf.inputfasta
        file_format = "fasta"
    else:
        infiles = ", ".join(filter(None, [conf.inputfastq_1, conf.inputfastq_2]))
        file_format = "fastq"

    result_file, json_results = json_old(args,
                                         results,
                                         conf.aligner,
                                         file_format,
                                         conf.db_conf.dbs,
                                         service,
                                         conf.inputfasta)
    if args.extented_output:
        make_table(method_obj,
                   json_results,
                   conf.db_conf.db_description,
                   service,
                   conf.species,
                   conf.outputPath)

    if args.quiet:
        f.close()
        
        
