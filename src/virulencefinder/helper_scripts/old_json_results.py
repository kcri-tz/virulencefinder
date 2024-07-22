import json
import os
import pprint
from time import strftime

def json_old(args, results, method, file_format, dbs, service, infile):
    """
    :param args: The arguments from parser.py
    :param results: The results from the analysis
    :param method: The method used for the analysis, kma or blast
    :param file_format: The file format of the input file. fastq or fasta
    :param dbs: The databases used for the analysis
    :return: Returns a json file in the old format which is necessary to create the extended output for virulencefinder
    
    """
    
    db_path = args.db_path
    min_cov = float(args.min_cov)
    threshold = float(args.threshold)
    outdir = args.outputPath

    json_results = dict()

    # Open notes.txt from database
    func_notes = {}
    notes_file = open(db_path + "/notes.txt")
    for line in notes_file:
        splitted_line = line.split(":")
        gene = splitted_line[0]
        func = splitted_line[1]
        func_notes[gene] = func

    hits = []

    for db in results:
        contig_res = {}
        if db == 'excluded':
            continue
        db_name = str(dbs[db][0])
        if db_name not in json_results:
            json_results[db_name] = {}
        if db not in json_results[db_name]:
            json_results[db_name][db] = {}
        if results[db] == "No hit found":
            json_results[db_name][db] = "No hit found"
        else:
            for contig_id, hit in results[db].items():

                identity = float(hit["perc_ident"])
                coverage = float(hit["perc_coverage"])

                # Skip hits below coverage
                if coverage < (min_cov * 100) or identity < (threshold * 100):
                    continue

                bit_score = identity * coverage

                if contig_id not in contig_res:
                    contig_res[contig_id] = []
                contig_res[contig_id].append([hit["query_start"], hit["query_end"],
                                            bit_score, hit])

        if not contig_res:
            json_results[db_name][db] = "No hit found"

        # Check for overlapping hits, only report the best
        for contig_id, hit_lsts in contig_res.items():

            hit_lsts.sort(key=lambda x: x[0])
            hits = [hit[3] for hit in hit_lsts]

            for hit in hits:
                header = hit["sbjct_header"]

                tmp = header.split(":")
                try:
                    gene = tmp[0]
                    note = tmp[1]
                    acc = tmp[2]
                except IndexError:
                    gene = ":".join(tmp)
                    print(gene)
                    note = ""
                    acc = ""
                try:
                    variant = tmp[3]
                except IndexError:
                    variant = ""

                identity = hit["perc_ident"]
                coverage = hit["perc_coverage"]
                sbj_length = hit["sbjct_length"]
                HSP = hit["HSP_length"]
                positions_contig = "%s..%s" % (hit["query_start"],
                                            hit["query_end"])
                positions_ref = "%s..%s" % (hit["sbjct_start"], hit["sbjct_end"])
                contig_name = hit["contig_name"]

                # Get protein function from notes_file
                if gene + note in func_notes:
                    function = func_notes[gene + note].rstrip()
                elif gene + variant in func_notes:
                    function = func_notes[gene + variant].rstrip()
                elif gene in func_notes:
                    function = func_notes[gene].rstrip()
                else:
                    function = ""

                # Write JSON results dict
                json_results[db_name][db].update({contig_id: {}})
                json_results[db_name][db][contig_id] = {
                    "virulence_gene": gene,
                    "identity": round(identity, 2),
                    "HSP_length": HSP,
                    "template_length": sbj_length,
                    "position_in_ref": positions_ref,
                    "contig_name": contig_name,
                    "positions_in_contig": positions_contig,
                    "note": note,
                    "accession": acc,
                    "protein_function": function,
                    "coverage": round(coverage, 2),
                    "hit_id": contig_id}

    # Get run info for JSON file
    date = strftime("%d.%m.%Y")
    time = strftime("%H:%M:%S")

    # Make JSON output file
    data = {service: {}}

    userinput = {"filename(s)": infile,
                "method": method,
                "file_format": file_format}
    run_info = {"date": date, "time": time}
    json_results=dict(sorted(json_results.items(), key=lambda x: x[0].lower()))
    data[service]["user_input"] = userinput
    data[service]["run_info"] = run_info
    data[service]["results"] = json_results

   # pprint.pprint(data)

    # Save json output
    result_file = "{}/data.json".format(outdir)
    with open(result_file, "w") as outfile:
        json.dump(data, outfile)
        
    return result_file, json_results