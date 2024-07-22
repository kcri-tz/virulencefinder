class PhenotypeResult(dict):
    def __init__(self, region_key, region_name, db_notes_file):
        self["type"] = "phenotype"
        self["category"] = "virulence"
        self["seq_regions"] = [region_key]
        self["key"], self["function"] = self.find_protein_function(
            region_name, db_notes_file)

        
            
    def find_protein_function(self, region_name, notes_file):
        """Returns the matching seq_regions protein function from notes.txt
        file

        TODO: The notes.txt file is read for each gene hit. It should just be
        a dictionary that is read once and then used for all gene hits.

        Args:
            region_name (str): Name of sequence region
            notes_file (str): Path to database notes.txt file

        Returns:
            str: protein function
        """
        func_notes = {}
        with open(notes_file, "r") as notes_fh:
            for line in notes_fh.readlines():
                splitted_line = line.split(":")
                gene = splitted_line[0]
                func = splitted_line[1]
                func_notes[gene] = func
        # Get protein function from notes_file
        if region_name not in func_notes:
            key = region_name.replace("_", " ")
            prot_function = func_notes.get(
                key, "No function found in database")
            # print(f"Warn: Function not found for {region_name}. Using {key}")
        else:
            key = region_name
            prot_function = func_notes[region_name]
        return key, prot_function.strip()
