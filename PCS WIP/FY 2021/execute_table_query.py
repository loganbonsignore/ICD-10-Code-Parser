import json
from pprint import pprint # Used for debugging

# Creating memory allocation to PSC Index json file
with open("Data/JSON/PCS_Tables.json") as tables_file:
    PCS_tables = json.load(tables_file)

class PCS_Table:
    def __init__(self):
        pass

    def get_table_from_string(self, codes: str) -> dict:
        # This method returns an object containing a PCS table which pos 1,2,3 codes match what is passed as arg
        # This method only works when pos 1,2,3 codes are provided in codes in s
        # NOTE: If less than 3 codes passed, will need to execute another display structure (similar to icd_10_codes.com) 
        found = False # Flag used to determine if table found
        # Ensure all individual codes inside the codes list are capitalized
        codes = codes.upper()
        # Get table codes
        tab = codes[:3]
        for table in tables:
            # Gather table's 'tab' value
            tab_codes = (tab["label"][0]["_code"] for tab in table["axis"])
            tab_codes = "".join(tab_codes)
            # If table's 'tab' value matches 'tab' value passed as arg
            if tab_codes == tab:
                found = True
                return table
        # If did not find a match, raise error
        if not found:
            raise LookupError(f"Did not find matching table to '{tab_codes}'. Must include code values for pos 1,2,3 of the PCS table you are looking for. Be sure to not mistake a '0', for 'O'.")

    def define_section_codes(self, codes: str) -> dict:
        # This method returns a dictionary with keys=position values (4-7) and values=the individual position code
        # Starting at position 4 because using first three codes already
        pos_indicator = 4
        pos_structures = {}
        for code in codes[3:]:
            # Add to dictionary
            pos_structures[str(pos_indicator)] = code
            # Move to next pos
            pos_indicator += 1
        return pos_structures

    def find_component_in_tables(self, pcs_component: str) -> dict:
        # This method is used to identify a 'category', 'code' and 'pos' value for any 'pcs_component' text returned by an index query
        # This method iterates through each table and calls find_component_in_table() to identify matching pcs components
        # This method queries all tables until match is found
        # It's assummed that each pcs component text is always shown in the same 'category' or 'pos' (NOTE: test this claim)
        # Create generator object of all pcs tables
        tables = (table for table in PCS_tables["ICD10PCS.tabular"]["pcsTable"])
        for table in tables:
            # Run find_pcs_component_in_table() on each table until match found
            return self.find_component_in_table(pcs_component, table)
        # If match is not found, return empty dict
        raise LookupError(f"Could not find a matching text value to '{pcs_component}' in any pcs table.")

    def find_component_in_table(self, pcs_component: str, table: dict) -> dict:
        # This method is called in find_component_in_tables()
        # This method is used to identify a 'category', 'code' and 'pos' value for any pcs_component text returned by an index query
        # This method queries only one individual table
        for row_container in table["pcsRow"]:
            for row in row_container["axis"]:
                # Search for pos code match at pos passed as arg
                for code_container in row["label"]:
                    # Search for matching text to pcs component
                    if pcs_component == code_container["__text"]:
                        # Return data to user
                        return {
                            "category": row["title"],
                            "pos": row["_pos"],
                            "code": code_container["_code"],}
        # If match is not found, raise error
        raise LookupError(f"Could not find a matching text value to '{pcs_component}' in pcs table passed as arg.")

# # Aggregating tables into one list
# tables = [table for table in PCS_tables["ICD10PCS.tabular"]["pcsTable"]]

# # Begin query
query_tool = PCS_Table()
# Manually coded for testing
code_from_index = "0UJ"

# Return table object based on codes passed
# Must have 3 or more codes available
table = query_tool.get_table_from_string(code_from_index)
pprint(table)
# Returns dict with keys=position values (4-7) and values=the individual position code
section_codes = query_tool.define_section_codes(code_from_index)

print(query_tool.find_component_in_table("Percutaneous Endoscopic", table))



    
            










