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

    def match_code_to_row(self, pos: str or int, section_codes: dict) -> list:
        # Args:
            # pos = position number to check
            # section_codes = a dictionary keys=position values (4-7) and values=the individual position code
        # This method searches a particular position value to find a match to the 'section codes' code value passed as arg
        # It returns a list of all available category objects in all pcs rows
        # Convert pos to string for query
        if isinstance(pos, int):
            pos = str(pos)
        # Used to store path options
        options = []
        for row_container in table["pcsRow"]:
            # Extract number of codes available in this row
            num_codes_avail = row_container["_codes"]
            for row in row_container["axis"]:
                # Search for pos code match at pos passed as arg
                if row["_pos"] == pos:
                    for code_choice in row["label"]:
                        # If 'code_choice' matches individual pos 4 code extracted from index query return
                        if code_choice["_code"] == section_codes[pos]:
                            # Use options because user may have the choice to use more than one row
                            options.append(row)
        return options

# Aggregating tables into one list
tables = [table for table in PCS_tables["ICD10PCS.tabular"]["pcsTable"]]

# Begin query
query_tool = PCS_Table()
# Manually coded for testing
code_from_index = "0U2DXY"

# Return table object based on codes passed
# Must have 3 or more codes available
table = query_tool.get_table_from_string(code_from_index)
# Returns dict with keys=position values (4-7) and values=the individual position code
section_codes = query_tool.define_section_codes(code_from_index)
for code in section_codes.values(): 
    pos_count = 1
    # Query table to build final 'code_output' object using 'section_codes'
    list_of_options = query_tool.match_code_to_row(pos_count, section_codes)
    if not list_of_options:
        # Raise error if faulty code combination (code cannot be found)
        raise ValueError("Expected list_options list.")
    pos_count += 1
if len(list_of_options) == 1:
    print("HIII")
    # Auto-select
    # Add only element of list_of_options list to final 'code object'
    pass
else:
    print("YOOOO")
    # Ask user what they want
    pass
pprint(list_of_options)


    
            










