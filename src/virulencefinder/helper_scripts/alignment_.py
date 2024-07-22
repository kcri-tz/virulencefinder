import sys 

def make_aln(file_handle, json_data, query_aligns, homol_aligns, sbjct_aligns):
    for dbs_info in json_data.values():
        for db_name, db_info in dbs_info.items():
            if isinstance(db_info, str):
                continue

            for gene_id, gene_info in sorted(
                    db_info.items(),
                    key=lambda x: (x[1]['virulence_gene'],
                                   x[1]['accession'])):

                seq_name = ("{gene}_{acc}"
                            .format(gene=gene_info["virulence_gene"],
                                    acc=gene_info["accession"]))
                hit_name = gene_info["hit_id"]

                seqs = ["", "", ""]
                seqs[0] = sbjct_aligns[db_name][hit_name]
                seqs[1] = homol_aligns[db_name][hit_name]
                seqs[2] = query_aligns[db_name][hit_name]

                write_align(seqs, seq_name, file_handle)


def write_align(seq, seq_name, file_handle):
    file_handle.write("# {}".format(seq_name) + "\n")
    sbjct_seq = seq[0]
    homol_seq = seq[1]
    query_seq = seq[2]
    for i in range(0, len(sbjct_seq), 60):
        file_handle.write("%-10s\t%s\n" % ("template:", sbjct_seq[i:i + 60]))
        file_handle.write("%-10s\t%s\n" % ("", homol_seq[i:i + 60]))
        file_handle.write("%-10s\t%s\n\n" % ("query:", query_seq[i:i + 60]))
