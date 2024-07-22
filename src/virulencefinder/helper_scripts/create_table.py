from .alignment_ import make_aln
from tabulate import tabulate

        
def make_table(method_obj, json_results, db_description, service, species, outputPath):
    query_aligns = method_obj.gene_align_query
    homo_aligns = method_obj.gene_align_homo
    sbjct_aligns = method_obj.gene_align_sbjct
    header = ["Virulence factor", "Identity", "Query / Template length", "Contig",
            "Position in contig", "Protein function", "Accession number"]
    # Define extented output
    table_filename = "{}/results_tab.tsv".format(outputPath)
    query_filename = "{}/Hit_in_genome_seq.fsa".format(outputPath)
    sbjct_filename = "{}/Virulence_genes.fsa".format(outputPath)
    result_filename = "{}/results.txt".format(outputPath)
    table_file = open(table_filename, "w")
    query_file = open(query_filename, "w")
    sbjct_file = open(sbjct_filename, "w")
    result_file = open(result_filename, "w")

    # Make results file
    result_file.write("{} Results\n\nOrganism(s): {}\n\n"
                    .format(service, ",".join(species)))

    # Write tsv table
    rows = [["Database"] + header]
    for species, dbs_info in json_results.items():
        for db_name, db_hits in dbs_info.items():
            result_file.write("*" * len("\t".join(header)) + "\n")
            result_file.write(db_description[db_name] + "\n")
            db_rows = []

            # Check it hits are found
            if isinstance(db_hits, str):
                content = [''] * len(header)
                content[int(len(header) / 2)] = db_hits
                result_file.write(text_table(header, [content]) + "\n")
                continue

            for gene_id, gene_info in sorted(
                    db_hits.items(),
                    key=lambda x: (x[1]['virulence_gene'],
                                x[1]['accession'])):

                vir_gene = gene_info["virulence_gene"]
                identity = str(gene_info["identity"])
                coverage = str(gene_info["coverage"])

                template_HSP = (
                    "{hsp_len} / {template_len}".
                    format(hsp_len=gene_info["HSP_length"],
                        template_len=gene_info["template_length"]))

                position_in_ref = gene_info["position_in_ref"]
                position_in_contig = gene_info["positions_in_contig"]
                protein_function = gene_info["protein_function"]
                acc = gene_info["accession"]
                contig_name = gene_info["contig_name"]

                # Add rows to result tables
                db_rows.append([vir_gene, identity, template_HSP, contig_name,
                                position_in_contig, protein_function, acc])
                rows.append([db_name, vir_gene, identity, template_HSP,
                            contig_name, position_in_contig, protein_function,
                            acc])

                # Write query fasta output
                hit_name = gene_info["hit_id"]
                query_seq = query_aligns[db_name][hit_name]
                sbjct_seq = sbjct_aligns[db_name][hit_name]

                if coverage == 100 and identity == 100:
                    match = "PERFECT MATCH"
                else:
                    match = "WARNING"
                qry_header = (">{}:{} ID:{}% COV:{}% Best_match:{}\n"
                            .format(vir_gene, match, identity, coverage,
                                    gene_id))
                query_file.write(qry_header)
                for i in range(0, len(query_seq), 60):
                    query_file.write(query_seq[i:i + 60] + "\n")

                # Write template fasta output
                sbj_header = ">{}\n".format(gene_id)
                sbjct_file.write(sbj_header)
                for i in range(0, len(sbjct_seq), 60):
                    sbjct_file.write(sbjct_seq[i:i + 60] + "\n")

            # Write db results tables in results file and table file
            result_file.write(text_table(header, db_rows) + "\n")

        result_file.write("\n")

    for row in rows:
        table_file.write("\t".join(row) + "\n")




    # Write allignment output
    result_file.write("\n\nExtended Output:\n\n")
    make_aln(result_file, json_results, query_aligns, homo_aligns,
            sbjct_aligns)

    # Close all files
    query_file.close()
    sbjct_file.close()
    table_file.close()
    result_file.close()
    
    
    
def text_table(headers, rows, empty_replace='-'):
    ''' Create text table

    USAGE:
        >>> from tabulate import tabulate
        >>> headers = ['A','B']
        >>> rows = [[1,2],[3,4]]
        >>> print(text_table(headers, rows))
        **********
          A     B
        **********
          1     2
          3     4
        ==========
    '''
    # Replace empty cells with placeholder
    rows = map(lambda row: map(lambda x: x if x else empty_replace, row), rows)
    # Create table
    table = tabulate(rows, headers, tablefmt='simple').split('\n')
    # Prepare title injection
    width = len(table[0])
    # Switch horisontal line
    table[1] = '*' * (width + 2)
    # Update table with title
    table = (("%s\n" * 3)
             % ('*' * (width + 2), '\n'.join(table), '=' * (width + 2)))
    return table