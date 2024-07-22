VirulenceFinder documentation
===================

This project documents the VirulenceFinder service
VirulenceFinder identifies viruelnce genes in total or partial sequenced
isolates of bacteria - at the moment E. coli, Enterococcus, S. aureus and Listeria are available.


## Important if you are updating from a previous VirulenceFinder version

It is no longer recommended to clone the VirulenceFinder bitbucket repository unless you plan to do development work on VirulenceFinder.

Instead we recommend installing VirulenceFinder using pip as described below.

There are several good reasons why the recommended installation procedure has changed. Its easier for users. And it makes sure your installation will be a tested release of the application.

## Installation

VirulenceFinder consists of an application and a database. The database can be used without the application, but not the other way around. Below VirulenceFinder, the application, will be installed first and then the database will be installed and configured to work with VirulenceFinder the application.

### Dependencies

VirulenceFinder uses two external alignment tools that must be installed.

* BLAST
* KMA

#### BLAST

If you don't want to specify the path of BLAST every time you run VirulenceFinder, make sure that "blastn" is in you PATH or set the environment variable specified in the "Environment Variables Table" in this README.

Blastn can be obtained from:

```url
https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/
```

```bash
# Example of how to set the environment variable in the bash shell. Remember this is only temporary, if you want it set every time you log in you need to add this line to your .bashrc, .zshrc file.
export CGE_BLASTN="/path/to/some/dir/blastn"
```

#### KMA

If you don't want to specify the path of KMA every time you run VirulenceFinder, make sure that KMA is in you PATH or set the environment variable specified in the "Environment Variables Table" in this README.

KMA can be obtained from:

```url
https://bitbucket.org/genomicepidemiology/kma.git
```

```bash
# Example of how to set the environment variable in the bash shell. Remember this is only temporary, if you want it set every time you log in you need to add this line to  your .bashrc, .zshrc file.
export CGE_KMA="/path/to/some/dir/kma/kma"
```

### Install VirulenceFinder the application using pip

**Important**: This will install VirulenceFinder in the environment where you run pip and potenitally update the python modules VirulenceFinder depends on. It is recommended to run VirulenceFinder in its own environment, in order to avoid breaking existing installations and prevent VirulenceFinder from getting broken by future unrelated pip installations. This is described in the optional step below.

#### Optional: Create virtual environment ####

Go to the location where you want to store your environment.

```bash

# Create environment
python3 -m venv virulencefinder_env

# Activate environment
source vilencefinder_env/bin/activate

# When you are finished using Virulencefinder deactivate the environment
deactivate

```

#### Install VirulenceFinder ####

```bash
cd virulencefinder 

pip install dist/*.whl
pip install dist/*.tar.gz

```

#### Databases

If you don't want to specify the path to the database every time you run VirulenceFinder, you need to set the environment variable specified in the "Environment Variables Table" in this README.

Go to the location where you want to store the database. Clone the datbases you need.

**Note**: We are currently working on hosting a tarballed version of the database that can be downloaded, so that cloning can be avoided.

```bash

git clone https://bitbucket.org/genomicepidemiology/virulencefinder_db/

```

Set temporary environment variables.

```bash

# Example of how to set the environment variable in the bash shell. Remember this is only temporary, if you want it set every time you log in you need to add this line to for example your .bashrc file.
export CGE_VIRULENCEFINDER_DB="/path/to/some/dir/virulencefinder_db"

```

### Install VirulenceFinder with Docker

The VirulenceFinder application and the database has been build into a single image on docker hub named "genomicepidemiology/virulencefinder". Below is an example run, where the current working directory is bound to the container "/app" path which is the container working directory.

```bash

docker run -v "$(pwd):/app" genomicepidemiology/virulencefinder:3.0.0 -o test_out -d s.aureus_exoenzyme,s.aureus_hostimm,s.aureus_toxin -ifq tests/data/s_aureus/*.gz

```

## Usage

You can run virulencefinder command line using python.

```bash

# Example of running virulencefinder
python -m src.virulencefinder.__main__ -ifa data/test_isolate_01.fa -o "." 

```

# The program can be invoked with the -h option


options:
```
  -h, --help            show this help message and exit

  -ifa INPUTFASTA, --inputfasta INPUTFASTA
                        Input fasta file.

  -ifq INPUTFASTQ [INPUTFASTQ ...], --inputfastq INPUTFASTQ 
  [INPUTFASTQ ...]
                        Input fastq file(s). Assumed to be single-end fastq if only one file is provided, and assumed to be paired-end data if two files are provided.

  --nanopore            If nanopore data is used

  -p DB_PATH, --db_path DB_PATH
                        Path to the database

  -d DATABASES, --databases DATABASES
                        Databases to search in. You can type all or None to choose all databases

  -o OUTPUTPATH, --outputPath OUTPUTPATH
                        Output directory. If it doesnt exist, it will be created.

  -j OUT_JSON, --out_json OUT_JSON
                        Specify JSON filename and output directory. 
                        If the directory doesnt exist, it will be created.

  -b BLASTPATH, --blastPath BLASTPATH
                        Path to blastn

  -k KMAPATH, --kmaPath KMAPATH
                        Path to KMA

  --speciesinfor_json SPECIES
                        Argument used by the cge pipeline. It takes a list"
                            " in json format consisting of taxonomy, from "
                            "domain -> species. A database is chosen based on "
                            "the taxonomy.

  -l MIN_COV, --min_cov MIN_COV
                        Minimum (breadth-of) coverage of ResFinder within the range 0-1.

  -t THRESHOLD, --threshold THRESHOLD
                        Threshold for identity of ResFinder within the range 0-1.

  -v, --version         Show programs version number and exit
  
  --pickle              Create a pickle dump of the Isolate object. Currently needed in the CGE webserver. Dependency and this option is being removed.

```

### Environment Variables

Environment variables recognized by VirulenceFinder, the flag they replace and the default value for the flag. Provided commandline flags will always take precedence. Set environment variables takes precedence over default flag values.

Additional Environment variables can be added by appending entries to the file named "environment_variables.md".

#### Environment Variables Table

## Environment Variables Table

| Environment Variabel       | Flag                | Default Value  |
|----------------------------|---------------------|----------------|
| CGE_BLASTN                 | blastPath           | blastn         |
| CGE_VIRULENCEFINDER_DB     | db_path             | databases      |
| CGE_VIRFINDER_GENE_COV     | min_cov             | 0.60           |
| CGE_VIRFINDER_POINT_ID     | threshold           | 0.90           |
| CGE_VIRFINDER_JSON         | speciesinfo_json    | None           |

### Web-server

A webserver implementing the methods is available at the [CGE
website](http://www.genomicepidemiology.org/) and can be found here:
<https://cge.food.dtu.dk/services/VirulenceFinder/>

Citation
=======

When using the method please cite:

Real-time whole-genome sequencing for routine typing, surveillance, and outbreak detection of verotoxigenic Escherichia coli.
Joensen KG, Scheutz F, Lund O, Hasman H, Kaas RS, Nielsen EM, Aarestrup FM.
J. Clin. Micobiol. 2014. 52(5): 1501-1510.
[Epub ahead of print]

References
=======

1. Camacho C, Coulouris G, Avagyan V, Ma N, Papadopoulos J, Bealer K, Madden TL. BLAST+: architecture and applications. BMC Bioinformatics 2009; 10:421.
2. Clausen PTLC, Aarestrup FM, Lund O. Rapid and precise alignment of raw reads against redundant databases with KMA. BMC Bioinformatics 2018; 19:307.

License
=======

Copyright (c) 2014, Ole Lund, Technical University of Denmark
All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   <http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
