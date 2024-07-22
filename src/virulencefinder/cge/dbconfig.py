import sys
import os


class DBConfig:
    def __init__(self) -> (dict, dict, dict):
        self.dbs = {}
        self.db_description = {}
        self.tax_2_db = {}

    @staticmethod
    def prep_line(i):
        tmp = i.split("\t")
        if len(tmp) != 3:
            sys.exit(
                (
                    "Input Error: Invalid line in the database"
                    " config file!\nA proper entry requires 3 tab "
                    "separated columns!\n%s"
                )
                % (i)
            )
        db_prefix = tmp[0].strip()
        name = tmp[1].split("#")[0].strip()
        description = tmp[2]
        return db_prefix, name, description

    @staticmethod
    def check_extension(extensions, db_path, db_prefix):
        for ext in extensions:
            db = "%s/%s.%s" % (db_path, db_prefix, ext)
            if not os.path.exists(db):
                sys.exit(
                    ("Input Error: The database file (%s) " "could not be found!")
                    % (db)
                )

    def check_dbs(self):
        if len(self.dbs) == 0:
            sys.exit(
                "Input Error: No databases were found in the " "database config file!"
            )

    def parse_db_config(self, db_config_file, db_path: str) -> None:
        with open(db_config_file) as f:
            for i in f:
                i = i.strip()
                if i == "":
                    continue
                if i[0] == "#":
                    if "extensions:" in i:
                        extensions = [
                            s.strip() for s in i.split("extensions:")[-1].split(",")
                        ]
                    continue
                db_prefix, name, description = self.prep_line(i)
                # Check if all db files are present
                self.check_extension(extensions, db_path, db_prefix)

                if db_prefix not in self.dbs:
                    self.dbs[db_prefix] = []
                else:
                    pass
                self.dbs[db_prefix].append(name)

                self.db_description[db_prefix] = description

                # Create database, where keys are from column 2 in config file (species
                # or other taxonomy). Values are lists of databases belonging to the
                # species or "group".
                taxdbs = self.tax_2_db.get(name.lower(), [])
                taxdbs.append(db_prefix)
                self.tax_2_db[name.lower()] = taxdbs
        self.check_dbs()
