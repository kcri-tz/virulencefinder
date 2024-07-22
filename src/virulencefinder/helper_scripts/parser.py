from argparse import ArgumentParser, Namespace
from ..__init__ import __version__

def collect_args() -> (Namespace, ArgumentParser):
    parser = ArgumentParser()
    parser.add_argument("-ifa", "--inputfasta",
                        help="FASTA or FASTQ input files.",
                        nargs="+",
                        default = None
                        )
    parser.add_argument("-ifq", "--inputfastq",
                    help=("Input fastq file(s). Assumed to be single-end "
                            "fastq if only one file is provided, and assumed"
                            " to be paired-end data if two files are "
                            "provided."),
                    nargs="+",
                    default=None)
    parser.add_argument("--nanopore",
                    action="store_true",
                    dest="nanopore",
                    help="If nanopore data is used",
                    default=False)
    parser.add_argument("-o", "--outputPath",
                        dest="outputPath",
                        help="Path to blast output",
                        default='.')
    parser.add_argument("-tmp", "--tmp_dir",
                        help=("Temporary directory for storage of the results "
                              "from the external software. Defaults to 'tmp' "
                              "dir in the given output dir."),
                        default=None)
    parser.add_argument("-b", "--blastPath",
                        help="Path to blastn",
                        default=None)
    parser.add_argument("-k", "--kmaPath",
                        help="Path to KMA",
                        default=None)
    parser.add_argument("-p", "--databasePath",
                        dest="db_path",
                        help="Path to the databases",
                        default=None)
    parser.add_argument("-d", "--databases",
                        help=("Databases chosen to search in - if non or all is "
                            "specified all is used"))
    parser.add_argument("-l", "--mincov",
                        dest="min_cov",
                        help="Minimum coverage",
                        default=0.60)
    parser.add_argument("-t", "--threshold",
                        dest="threshold",
                        help="Minimum hreshold for identity",
                        default=0.90)
    parser.add_argument("-x", "--extented_output",
                        help=("Give extented output with allignment files, "
                            "template and query hits in fasta and a tab "
                            "seperated file with gene profile results"),
                        action="store_true")
    parser.add_argument("--speciesinfo_json",
                        help=("Argument used by the cge pipeline. It takes a list"
                            " in json format consisting of taxonomy, from "
                            "domain -> species. A database is chosen based on "
                            "the taxonomy."),
                        default=None)
    parser.add_argument("-db_vir_kma", "--db_path_vir_kma",
                    help=("Path to the virulencefinder databases indexed with "
                            "KMA. Defaults to the value of the --db_res "
                            "flag."),
                    default=None)
    parser.add_argument("-q", "--quiet",
                        action="store_true")
    parser.add_argument("-j", "--out_json",
                    help=("Specify JSON filename and output directory. If "
                            "the directory doesn't exist, it will be "
                            "created."),
                    default=None)
    parser.add_argument("-v","--version",
                        help = ("Version of Virulencefinder"),
                        version = __version__,
                        action = "version")
    parser.add_argument("--overlap",
                    help=("Genes are allowed to overlap this number of"
                          "nucleotides."),
                    default=30)

    args = parser.parse_args()
    return args, parser