#!/usr/bin/env python3

import os.path
import os
import sys
import subprocess
import json
from argparse import Namespace

from cgelib.utils.loaders_mixin import LoadersMixin
from .dbconfig import DBConfig


class Config:

    ENV_VAR_FILENAME = "environment_variables.md"
    # SPECIES_ABBR_FILENAME = "species_abbreviations.md"

    DEFAULT_VALS = {
        "inputfasta": None,
        "inputfastq": None,
        "nanopore": False,
        "outputPath": ".",
        "tmp_dir": None,
        "kmaPath": "kma",
        "blastPath": "blastn",
        "db_path": "databases",
        "min_cov": 0.6,
        "threshold": 0.9,
        "speciesinfo_json": None,
    }

    def __init__(self, args: Namespace) -> None:

        # Directoy of config.py substracted the last dir 'cge'
        self.virulence_finder_root = os.path.dirname(os.path.realpath(__file__))[:-3]
        self.env_var_file = os.path.join(
            self.virulence_finder_root, "cge", Config.ENV_VAR_FILENAME
        )

        Config.set_default_and_env_vals(args, self.env_var_file)

        self.set_general_opts(args)

        self.set_virfinder_opts(args)

        self.set_virdb_conf(args)

        self.set_species()

    def set_general_opts(self, args):
        """
        :param args: defined dic with arguments for virulencefinder
        :result Creates first folder in given outputPath (default: .).
        """
        self.outputPath = os.path.abspath(args.outputPath)
        os.makedirs(self.outputPath, exist_ok=True)

        if args.tmp_dir is None:
            args.tmp_dir = f"{self.outputPath}/tmp"
        self.tmp_dir = os.path.abspath(args.tmp_dir)
        os.makedirs(self.tmp_dir, exist_ok=True)

        if args.out_json:
            if not args.out_json.endswith(".json"):
                sys.exit(
                    "Please specify the path to the JSON file including "
                    "its filename ending with .json.\n"
                )
            self.out_json = os.path.abspath(args.out_json)
            os.makedirs(os.path.dirname(self.out_json), exist_ok=True)
        else:
            self.out_json = False

        if args.speciesinfo_json:
            self.speciesinfo_json = self.get_abs_path_and_check(args.speciesinfo_json)
        else:
            self.speciesinfo_json = None

        if args.inputfasta != None:
            self.set_fasta_related_opts(args)
        else:
            self.set_fastq_related_opts(args)

    #  self.output_aln = bool(args.output_aln)

    def set_fasta_related_opts(self, args):
        """
        :param args: Contains the arguments for Virulencefinder
        :result Checks if the input fasta file exists. Creates a directory for virulencefinder output in outputPath
        """
        self.inputfastq_1 = None
        self.inputfasta = self.get_abs_path_and_check(args.inputfasta[0])

        self.outPath_blast = "{}/virulencefinder_blast".format(self.outputPath)
        os.makedirs(self.outPath_blast, exist_ok=True)
        self.sample_name = os.path.basename(self.inputfasta)
        self.blast = self.get_prg_path(args.blastPath)
        self.kma = None
        self.aligner = "blastn"

    def set_fastq_related_opts(self, args):
        """
        :param args: Contains the arguments for Virulencefinder from the user
        :result: Checks if the input fastq file exists. Creates a directory for resfinder output in outputPath
        """
        self.inputfasta = None
        self.inputfastq_1 = self.get_abs_path_and_check(args.inputfastq[0])
        if len(args.inputfastq) == 2:
            self.inputfastq_2 = self.get_abs_path_and_check(args.inputfastq[1])
        elif len(args.inputfastq) > 2:
            sys.exit(
                "ERROR: More than 2 files were provided to inputfastq: "
                "{}.".format(args.inputfastq)
            )
        else:
            self.inputfastq_2 = None

        self.outPath_kma = "{}/virulencefinder_kma".format(self.outputPath)
        os.makedirs(self.outPath_kma, exist_ok=True)

        self.sample_name = os.path.basename(args.inputfastq[0])
        self.kma = self.get_prg_path(args.kmaPath)
        self.nanopore = args.nanopore
        self.aligner = "kma"

    def set_virfinder_opts(self, args):
        """
        :param args: Contains the arguments for Virulencefinder from the user
        :result: checks database path and subfiles. Then checks inputs from user for min cov and threshold.
        NOTES: maybe it needs a check for the specific organism fsa file. If that exists in the database dir
        """
        self.set_path_virfinderdb(args)
        self.db_config_file = f"{self.db_path_vir}/config"
        self.db_notes_file = f"{self.db_path_vir}/notes.txt"
        if not os.path.exists(self.db_config_file):
            sys.exit(
                "Input Error: The database config file could not be found"
                " in the ResFinder database directory."
            )
        if not os.path.exists(self.db_notes_file):
            sys.exit(
                "Input Error: The database notes.txt file could not be "
                "found in the ResFinder database directory."
            )

        args.min_cov = float(args.min_cov)
        args.threshold = float(args.threshold)

        # Check if coverage/identity parameters are valid
        if args.min_cov > 1.0 or args.min_cov < 0.0:
            sys.exit(
                "ERROR: Minimum coverage above 1 or below 0 is not "
                "allowed. Please select a minimum coverage within the "
                "range 0-1 with the flag -l. Given value: {}.".format(args.min_cov)
            )
        self.min_cov = args.min_cov

        if args.threshold > 1.0 or args.threshold < 0.0:
            sys.exit(
                "ERROR: Threshold for identity of ResFinder above 1 or "
                "below 0 is not allowed. Please select a threshold for "
                "identity within the range 0-1 with the flag -t. Given "
                "value: {}.".format(args.threshold)
            )
        self.min_id = args.threshold

        self.overlap = int(args.overlap)

    def set_virdb_conf(self, args):
        """
        :param args: Contains the arguments for Virulencefinder from the user
        :result: Checks the database configuration file and sets the databases
        and their descriptions.
        """
        self.db_conf = DBConfig()
        self.db_conf.parse_db_config(self.db_config_file, self.db_path_vir)

        if self.speciesinfo_json:
            self.databases = None
            taxonomy = tuple(json.loads(self.speciesinfo_json))
            for tax in reversed(taxonomy):
                if tax in self.db_conf.tax_2_db:
                    self.databases = self.db_conf.tax_2_db[tax]
                    break
            if self.databases is None:
                self.databases = self.db_conf.dbs.keys()
        elif args.databases is None or args.databases == "all":
            # Choose all available databases from the config file
            # Needs to be a list as an iterator is not JSON serializable and
            # that is needed for writing the output json.
            self.databases = list(self.db_conf.dbs.keys())
        else:
            # Handle multiple databases
            database_list = args.databases.split(",")

            self.databases = []
            for db_prefix in database_list:
                if db_prefix in self.db_conf.dbs:
                    self.databases.append(db_prefix)
                else:
                    sys.exit(
                        "Input Error: Provided database was not "
                        f"recognised! ({db_prefix})\n"
                    )

    def set_species(self):
        self.species = list(set([",".join(self.db_conf.dbs[db]) for db in self.databases]))

    @staticmethod
    def get_abs_path_and_check(path, allow_exit=True):
        """
        :param: path: Path to input FASTA/FASTQ file.
        :param: allow_exit: Default True. If set to False virulencefinder will
                            continue to run.
        :result: Checks if path is file.
        """
        abs_path = os.path.abspath(path)
        if not os.path.isfile(abs_path) and not os.path.isdir(abs_path):
            if allow_exit:
                sys.exit("ERROR: Path not found: {}".format(path))
            else:
                raise FileNotFoundError
        return abs_path

    def set_path_virfinderdb(self, args):
        """
        :param args: arguments from parsed by the user and setted default arguments
        :result: takes path to virulencefinder database and checks its path. Also checks whether path to indexed database with kma is given.
        """
        self.db_path_vir = args.db_path
        self.db_path_vir_kma = args.db_path_vir_kma

        if self.db_path_vir_kma is None:
            self.db_path_vir_kma = self.db_path_vir

        if self.db_path_vir_kma is None and self.inputfastq_1:
            sys.exit("Input Error: No database directory for KMA was provided!" "\n")

        if self.db_path_vir is None and self.inputfasta:
            sys.exit("Input Error: No database directory was provided!\n")

        try:
            self.db_path_vir = Config.get_abs_path_and_check(
                self.db_path_vir, allow_exit=False
            )
        except FileNotFoundError:
            sys.exit(
                "Input Error: Could not locate VirulenceFinder database "
                f"path: {self.db_path_vir}"
            )

        try:
            self.db_path_vir_kma = Config.get_abs_path_and_check(
                self.db_path_vir_kma, allow_exit=False
            )
        except FileNotFoundError:
            if self.inputfastq_1:
                sys.exit(
                    "Could not locate VirulenceFinder database index "
                    f"path: {self.db_path_vir_kma}\n"
                    "Did you forget to run the INSTALL script in the "
                    "database directory?"
                )
            else:
                pass

    @staticmethod
    def get_prg_path(prg_path):
        """
        :param prg_path: for instance kma path.
        :result: Checks whether prg_path exists and if so, it will test kma by
                 running help. If the programm does not work it will exit the
                 run.
        """
        try:
            prg_path = Config.get_abs_path_and_check(prg_path, allow_exit=False)
        except FileNotFoundError:
            pass

        try:
            _ = subprocess.check_output([prg_path, "-h"])
        except PermissionError:
            sys.exit(
                "ERROR: Missing permission. Unable to execute app from"
                " the path: {}".format(prg_path)
            )
        return prg_path

    @staticmethod
    def set_default_and_env_vals(args, env_def_filepath):

        known_envs = LoadersMixin.load_md_table_after_keyword(
            env_def_filepath, "## Environment Variables Table"
        )

        # Set flag values defined in environment variables
        for var, entries in known_envs.items():
            try:
                cli_val = getattr(args, entries[0])
                # Flags set by user will not be None, default vals will be None
                if cli_val is not None:
                    continue

                var_val = os.environ.get(var, None)
                if var_val is not None:
                    setattr(args, entries[0], var_val)

            except AttributeError:
                sys.exit(
                    "ERROR: A flag set in the Environment Variables Table"
                    " in the README file did not match any valid flags in"
                    " VirulenceFinder. Flag not recognized: {}.".format(entries[0])
                )

        Config._set_default_values(args)

    @staticmethod
    def _set_default_values(args):
        for flag, def_val in Config.DEFAULT_VALS.items():
            val = getattr(args, flag)
            if val is None:
                setattr(args, flag, def_val)
