# Environment Variables for ResFinder

Environment variables recognized by ResFinder, the flag they replace and the default value for the flag. Provided command line flags will always take precedence. Set environment variables takes precedence over default flag values.

Additional Environment variables can be added by appending entries to the table below. The 'Flag' entry in the table must be the double dash flag recognised by ResFinder. The 'Default Value' entry is just for information.

## Environment Variables Table

| Environment Variabel       | Flag                | Default Value  |
|----------------------------|---------------------|----------------|
| CGE_BLASTN                 | blastPath           | blastn         |
| CGE_VIRULENCEFINDER_DB     | db_path             | databases      |
| CGE_VIRFINDER_GENE_COV     | min_cov             | 0.60           |
| CGE_VIRFINDER_POINT_ID     | threshold           | 0.90           |
| CGE_VIRFINDER_JSON         | speciesinfo_json    | None           |

