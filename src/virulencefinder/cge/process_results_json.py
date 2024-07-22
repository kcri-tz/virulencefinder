import os
from .gene_result import GeneResult
from .phenotype_scraping import PhenotypeResult
from .exceptions import DuplicateKeyError





def add_gene_result_if_key_not_None(gene_result, res_collection, key_object):
    '''
        Input:
            gene_result: GeneResult object (seq_region dict)
            res_collection: Result object created by the cge core module.
        adds gene_result to res_collection if gene_result['key'] is different
        from None.
            '''
    if gene_result["key"] is None:
        return
    elif gene_result["key"] not in res_collection[key_object]:
        res_collection.add_class(cl=key_object, **gene_result)
    else:
        raise DuplicateKeyError(
            "About to overwrite dict entry. This should not be "
            "happening as all keys are supposed to be unique."
            "Non-unique key was: {}".format(gene_result["key"]))



    
class VirulenceFinderResultHandler():
        
        
    def standardize_results(res_collection, results, conf, ref_db_name="VirulenceFinder"):
        """
            Input:
                res_collection: Result object created by the cge core module.

            Method loads the given res_collection with results from res.
        """

        for db_name, db in results.items():
            if(db_name == "excluded"):
                continue

            elif(db == "No hit found"):
                continue

            
            for unique_id, hit_db in db.items(): # one whole process per gene

                if(unique_id in results["excluded"]):
                    continue
                gene_result = GeneResult(res_collection, hit_db, ref_db_name, conf)

                add_gene_result_if_key_not_None(gene_result, res_collection, "seq_regions")
