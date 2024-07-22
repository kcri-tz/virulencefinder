#!/usr/bin/env python3
import random
import string

import os
from .phenotype_scraping import PhenotypeResult

class GeneResult(dict):
    def __init__(self, res_collection, res, ref_db_name, conf, alignments=None):
        self["type"] = "seq_region"
        self["gene"] = True

        self["ref_id"] = res["sbjct_header"]
        self["name"], self.variant, self["ref_acc"] = (
            GeneResult._split_sbjct_header(self["ref_id"]))
        self["identity"] = res["perc_ident"]
        self["ref_database"] = [res_collection.get_db_key(ref_db_name)[0]]
        
        self["alignment_length"] = res["HSP_length"]
        self["ref_seq_length"] = res["sbjct_length"]
        self["depth"] = res.get("depth", None)
        self["ref_start_pos"] = res["sbjct_start"]
        self["ref_end_pos"] = res["sbjct_end"]
        self["query_id"] = res["contig_name"]    # Positional essential
        self["query_start_pos"] = res["query_start"]    # Positional essential
        self["query_end_pos"] = res["query_end"]    # Positional essential
        #self["phenotypes"] = PhenotypeResult(res, ref_db_path)
        
        # Currently not used, but can be enabled when alignments are available
        
        # if conf and conf.output_aln:
        #     hit_class, hit_key = self.get_hit_class(alignments.gene_align_query)

        #     self["query_string"] = alignments.gene_align_query[hit_class][
        #         hit_key]
        #     self["alignment_string"] = alignments.gene_align_homo[hit_class][
        #         hit_key]
        #     self["ref_string"] = alignments.gene_align_sbjct[hit_class][hit_key]

        # BLAST coverage formatted results
        coverage = res.get("coverage", None)
        if (coverage is None):
            # KMA coverage formatted results
            coverage = res["perc_coverage"]
        else:
            coverage = float(coverage) * 100
        self["coverage"] = coverage

        self["grade"] = GeneResult.calc_gene_grade(
            coverage=self["coverage"], identity=self["identity"])

        self.remove_NAs()
        uniqueness = self._get_unique_gene_key(res_collection)
        self["key"] = uniqueness

        # Currently VirulenceFinder only has one phenotype per seq_region.
        # If this changes, this part also needs to change.
        self["phenotypes"] = [self.load_phenotype(res_collection, conf.db_notes_file)]

    def load_phenotype(self, res_collection, db_notes_file):
        phenotype = PhenotypeResult(self["key"], self["name"], db_notes_file)
        phenotype["ref_database"] = self["ref_database"]

        # If phenotype exist, just add seq_region to existing phenotype
        if phenotype["key"] in res_collection["phenotypes"]:
            res_collection["phenotypes"][phenotype["key"]]["seq_regions"].append(
                phenotype["key"])
        # Else add new phenotype
        else:
            res_collection.add_class(cl="phenotypes", **phenotype)
        
        return phenotype["key"]

    def get_hit_class(self, gene_align_query):
        """
            Input:
                gene_align_query: Dict from either FinderResult (KMA) or
                                  Blaster (BLAST)
            Output:
                hit_class: Name of AB class
                hit_key: Key used for query (hit)
            
            Method looks through all the queries that align to a reference and
            finds the query (hit) that matches the GeneResult object.
            For BLAST hits the query is named after the coresponding contig
            header (query_id), but for KMA the query key is named after the
            reference it aligns to (ref_id).
        """
        lookup_key = self["query_id"]
        if self["depth"] is not None:
            lookup_key = self["ref_id"]

        for ab_class, hits in gene_align_query.items():            
            if hits:
                hits_keys = list(hits.keys())
                hit_key = next((key for key in hits_keys
                                if key.startswith(lookup_key)), None)
                if hit_key is None:
                    continue
                hit_class = ab_class
                break
            else:
                continue
        
        return hit_class, hit_key

    @staticmethod
    def calc_gene_grade(coverage: float, identity: float) -> int:
        if coverage == 100.0 and identity == 100.0:
            return 3
        elif coverage == 100.0:
            return 2
        else:
            return 1

    def remove_NAs(self):
        """
            Remove all entries containing NA og None as values.

            Removing None is not necessary as the Result object will ignore all
            entries with None values.
        """
        na_keys = []
        for key, val in self.items():
            if (val == "NA" or val is None):
                na_keys.append(key)
        for key in na_keys:
            del self[key]

    @staticmethod
    def get_rnd_unique_gene_key(gene_key, res_collection,
                                minimum_gene_key, delimiter):
        """
            Input:
                gene_key: None-unique key
                res_collection: Result object created by the cgelib package.
                minimum_key: Key prefix
                delimiter: String used as delimiter inside the returned key.
            Output:
                gene_key: Unique key (string)

            If gene_key is found in res_collection. Creates a unique key by
            appending a random string ton minimum_gene_key.
        """
        while (gene_key in res_collection["seq_regions"]):
            rnd_str = GeneResult.random_string(str_len=4)
            gene_key = ("{key}{deli}{rnd}"
                        .format(key=minimum_gene_key, deli=delimiter,
                                rnd=rnd_str))
        return gene_key

    @staticmethod
    def random_string(str_len=4):
        """
            Output:
                random string of length 'str_len'

            Return a random string of the provided length. The string will only
            consist of lowercase ascii letters.
        """
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(str_len))

    @staticmethod
    def _split_sbjct_header(header):
        """
            Input:
                header: database entry header (ref_header/subject_header)
            Output:
                template: name of entry (string)
                variant: Variant interger (string) or None
                acc: Accession number given by sequnce database (string) or None

            Splits the input header by underscores and returns first list item
            as template. If list is > 1 then variant and acc will also return
            strings. If not they return None.
        """
        sbjct = header.split(":")
        template = sbjct[0]

        if (len(sbjct) > 1):
            variant = sbjct[1]
            acc = "_".join(sbjct[2:])
        else:
            variant = None
            acc = None

        return (template, variant, acc)

    def _get_unique_gene_key(self, res_collection, delimiter=";;"):
        """
            Input:
                res_collection: Result object created by the cgelib package.
                delimiter: String used as delimiter inside the returned key.
            Output:
                key: Unique key for hit

            Creates a unique key for GeneResult instance. Key format depends on
            database. If gene result is considered indentical to an existing
            gene result in the provided res_collection, it will not create a new
            key. Two restults are considered identical if they have the same
            query_id, query_start_pos and query_end_pos. If it is mapping
            results the query_* doesn't exist, and results will never be
            considered identical.
        """
        if "ref_acc" not in self:
            gene_key = ("{name}".format(**self))
        else:
            gene_key = ("{name}{deli}{var}{deli}{ref_acc}".format(
                        deli=delimiter, var=self.variant, **self))
        # Attach random string if key already exists
        minimum_gene_key = gene_key
        if gene_key in res_collection["seq_regions"]:

            query_id = self.get("query_id", "NA")

            # Query id == "NA" when FASTQ
            if (query_id == "NA"):
                res_collection["seq_regions"][gene_key]["ref_database"].extend(
                    self["ref_database"])
                gene_key = None
            # Query id != "NA" when FASTA
            elif (self["query_id"]
                    != res_collection["seq_regions"][gene_key]["query_id"]
                  or self["query_start_pos"]
                    != res_collection["seq_regions"][gene_key]["query_start_pos"]
                  or self["query_end_pos"]
                    != res_collection["seq_regions"][gene_key]["query_end_pos"]):
                gene_key = GeneResult.get_rnd_unique_gene_key(
                    gene_key, res_collection, minimum_gene_key, delimiter)
            else:
                res_collection["seq_regions"][gene_key]["ref_database"].extend(
                    self["ref_database"])
                gene_key = None

        return gene_key
