import json
from pprint import pprint # Used for debugging

# Creating memory allocations to PSC Index, PCS Tables, PCS Definitions json files
with open("Data/JSON/PCS_Index.json") as index_file:
    index = json.load(index_file)
with open("Data/JSON/PCS_Tables.json") as table_file:
    tables = json.load(table_file)
with open("Data/JSON/PCS_Definitions.json") as definitions_file:
    defs = json.load(definitions_file)

################################################# Start Class Definitions #################################################
###########################################################################################################################

class Parser:
    def __init__(self):
        self.term_found_flag = False # Flag for ensuring mainterm found. Used for debugging

    def execute_tree(self, mainterm, single_level_check=False):
        """
        Args:
            Mainterm -> Mainterm object in focus.
            single_level_check -> Bool value signaling to check for single level.
        Returns:
            None.
        """
        # This function acts as the 'go-to' execution funtion for this script
        # All "mainterm" objects are passed to this function
        # This function checks for levels, then executes functions built to handle the mainterm's structure
        levels = self.check_for_levels_in_mainterm(mainterm)
        # Check for levels to see which type of execute function is needed
        if levels == "level_1" and single_level_check == True:
            print("--------EXECUTE SINGLE LEVEL--------")
            # Used to execute mainterms that have multiple subterms "_level" key equal to "1" 
            # Does not include mainterms with subterms that have "_level" equal to "2" or greater
            Single_Level_Parser().execute_single_level(mainterm)
        elif not levels:
            print("--------PARENT EXECUTE--------")
            # Used to execute mainterms that do not have levels
            Mainterm_Parser().parent_execute(mainterm)
        else:
            print("--------PROGRESS THROUGH LEVELS--------")
            # Used to execute mainterms with subterms that have "_level" of 2 or greater
            self.progress_through_levels(mainterm)
    
    def progress_through_levels(self, mainterm):
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns:
            None.
        """
        # This function handles "mainterm" objects that contain more than 1 level
        # It iterates through levels until a final code or term is found
        # This function executes queries using sub-function Mainterm_Parser().progress_through_levels_execute()
        level_flag = True
        while level_flag:
            # Returns all "title" values from the next level of subterms
            new_level_terms = self.get_next_level_title_values(mainterm)
            if new_level_terms == None:
                # If no next level choices, execute with final subterm
                Mainterm_Parser().progress_through_levels_execute(mainterm)
            elif len(new_level_terms) == 1:
                # Find new_level_term. Auto select the first term from the new_level_terms list because only one term available
                new_level_term = new_level_terms[0]
                print(f"Automatically choosing term, '{new_level_term}', because it's the only choice available.")
                # Re-query mainterm object to find subterm that matches our new_level_term
                # Start another while loop with updated mainterm object
                mainterm = self.find_matching_mainterm_to_user_input(mainterm, new_level_term)
            else:
                # If more than one next level choice, ask user to choose
                print(new_level_terms)
                user_input = input("Choose term : ")
                # If user's choice does not match a choice in new_level_terms
                if user_input not in new_level_terms:
                    user_input = self.handle_bad_user_query
                # Find new mainterm object based on user choice above
                mainterm = self.find_matching_mainterm_to_user_input(mainterm, user_input)
                # Check for levels on new mainterm
                levels = self.check_for_levels_in_mainterm(mainterm)
                if not levels:
                    # If no more levels, execute with final mainterm
                    # If more levels, start another while loop iteration
                    level_flag = False
                    Mainterm_Parser().progress_through_levels_execute(mainterm)
    
    def find_matching_mainterm_to_user_input(self, mainterm, user_input):
        # This function is called in progress_through_levels()
        # This function iterates through next level terms and returns the term with a 'title' or 'see' tag equal to user_input
        # This function returns a 'mainterm' object or raises LookupError
        # Find new mainterm object based on user choice above
        for i in mainterm["term"]:
            try:
                # See if 'title' value matches user input
                if i["title"] == user_input:
                    return i
            except KeyError:
                try:
                    # If no 'title' value, check 'see' value for match
                    if i["see"] == user_input:
                        return i
                except KeyError:
                    # If no 'title' or 'see' match, raise error
                    raise LookupError("Could not find user's term in next_level_choices. Checked for a 'see' and 'title' tag. -> progress_through_levels()")

    def handle_bad_user_query(self, user_input, new_level_terms):
        # This function is called in progress_through_levels() and get_render_ask_next_level_terms()
        # If a user searches for a term that is not valid, give user three more trys
        # If user query term is not a valid term raise LookupError
            bad_query_flag = 0
            # User gets 5 query trys before throwing error
            while user_input not in new_level_terms and bad_query_flag <= 3:
                print("Your choice is not valid. Please try again.")
                user_input = input("Choose term : ")
                if bad_query_flag > 3:
                    raise LookupError("The term you've chosen does not match any valid options. Please try your query again.")
            return user_input
    
    def check_for_levels_in_mainterm(self, mainterm):
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            - "level_1"
            - True
            - False
        """
        # This function checks for levels in the Mainterm object in focus.
        # It can return:
            # 'level_1' -> Indicates multiple terms on level 1 to be handled, no further levels.
            # True -> Indicates multiple levels to be handled.
            # False -> Indicates no levels to be handled.
        try:
            # Check for "term" key in mainterm. If no "term" key, return False (no levels)
            for subterm in mainterm["term"]:
                try:
                    if subterm["term"]:
                        # Check for "term" key in sub_term
                        # This indicates multiple levels
                        return True
                except KeyError:
                    pass
            try:
                if mainterm["term"][0]["_level"] == "1":
                    # Check for level term on one of subterms
                    # This indicates multiple level 1 terms
                    return "level_1"
                elif mainterm["term"][0]["_level"] in ["2", "3", "4", "5", "6"]:
                    # Check to see if next level term has level tag
                    # This indicates there is a next level
                    return True
            # If no mainterm["_level"] key, return False
            except KeyError:
                return False
        # If no mainterm["term"] key, return False
        except KeyError:
            return False
        
    def get_next_level_title_values(self, mainterm):
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            List of "title" values found on next level of mainterm.
            If no next level, returns None.
        """
        # This function returns the "title" value of each next level subterm in a list
        # If the "mainterm" does not have subterms, the function returns None
        next_level_terms = []
        try:
            # Get list of "title" values on the next level of subterms
            for level_term in mainterm["term"]:
                try:
                    # Get 'level' tag
                    title = level_term["title"]
                except KeyError:
                    try:
                        # If no 'level' tag, try to get 'see' tag
                        title = level_term["see"]
                    except KeyError:
                        # Raise error if cannot find text to use in 'title' or 'see'
                        raise LookupError("Could not determine which text to be used when retrieveing next level values. See get_next_level_title_values()")
                # Add term to terms list to return to user
                next_level_terms.append(title)
        except KeyError:
            # If no next level terms, return None
            next_level_terms = None
        return next_level_terms
    
    def check_for_varying_subterm_structures(self, mainterm, set_like_object):
        """
        Args
            mainterm -> Mainterm object in focus.
            set_like_object -> set containing ordered dictionary keys which are being compared.
        Returns
            True
            ValueError
        """
        accounted_for_structures = [
            {'title', 'codes', '_level'}, # Accounted for in execute_single_level_5
            {'title', 'code', '_level'}, # Accounted for in execute_single_level_5
        ]
        # This function interates through each subterm to see if subterm structures vary from one another
        # It will raise ValueError if a mainterm structure is found that our code isn't prepared to handle
        # set_like_object is passed to the function and is a set of the first subterm's keys
        for term in mainterm["term"]:
            # Extracting keys of subterm
            term_keys = term.keys()
            # Iterating through subterm keys to check if structures vary
            for i in term_keys:
                # If the subterm's key is not in passed variable set_like_object
                # This means there is a subterm that contains a key that is different from the other subterm's keys
                if i not in set_like_object:
                    # Iterate through subterms and check that keys are not in accounted_for_structures
                    for j in mainterm["term"]:
                        # If not in accounted_for_structures, raise ValueError
                        if j.keys() in accounted_for_structures:
                            # This True value is used in execute_single_level()
                            return True
                        else:
                            raise ValueError("One subterm in the mainterm contains a key that is different from the other subterm keys and it is not accounted for.")
        # NOTE: Add functionality here to handle mainterm's with different structures
        # Could call an execute function here depending on structure found
    
    def get_render_ask_next_level_terms(self, mainterm, key_1, key_2=None):
        """
        Args
            mainterm -> Mainterm object in focus.
            key_1 -> String representing a dictionary key.
            key_2 -> String representing a dictionary key.
        Return
            User's choice of next level term, string.
        Notes
        """
        # This function aggregates the next level's terms from a mainterm's "term" key based on
        # developer provided keys passed as key_1 and key_2
        # It then prints choices for the user and asks user to choose which subterm they want to use
        if key_2:
            text_choices = [term[key_1][key_2] for term in mainterm["term"]]
        else:
            try:
                text_choices = [term[key_1] for term in mainterm["term"]]
            except KeyError:
                text_choices = [term["__text"] for term in mainterm["term"]]
        print(text_choices)
        user_input = input("Choose term that most correlates to this medical case: ")
        if user_input in text_choices:
            return user_input
        else:
            return self.handle_bad_user_query(user_input, text_choices)

    def create_new_mainterm_generator(self, index):
        letters_new = (letter_new for letter_new in index["ICD10PCS.index"]["letter"])
        return (mainterms_new for letter in letters_new for mainterms_new in letter["mainTerm"])

class Single_Level_Parser(Parser):
    def execute_single_level(self, mainterm):
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            None.
        """
        # This function points to a sub-function built to handle incoming mainterm structures
        # It returns ValueError if presented a mainterm structure it cannot handle
        # The first subterm is used to understand mainterm's structure
        # It is assumed that all subterms have the same key structure (which may not be true, Logan in progress of adding functionality)
        # Based on structure of subterms found, execute function that can handle structure
        first_subterm = mainterm["term"][0]
        if {"see", "_level"} == first_subterm.keys():
            self.check_for_varying_subterm_structures(mainterm, {"see", "_level"})
            self.execute_single_level_1(mainterm)
        elif {"title", "see", "_level"} == first_subterm.keys():
            self.check_for_varying_subterm_structures(mainterm, {"title", "see", "_level"})
            self.execute_single_level_2(mainterm)    
        elif {"use", "_level"} == first_subterm.keys():
            self.check_for_varying_subterm_structures(mainterm, {"use", "_level"})
            self.execute_single_level_3(mainterm)
        elif {"code", "_level"} == first_subterm.keys():
            self.check_for_varying_subterm_structures(mainterm, {"code", "_level"})
            self.execute_single_level_4(mainterm)
        elif {"title", "code", "_level"} == first_subterm.keys():
            self.check_for_varying_subterm_structures(mainterm, {'title', 'code', '_level'})
            self.execute_tree(mainterm)
        elif {"title", "codes", "_level"} == first_subterm.keys():
            varying_structures = self.check_for_varying_subterm_structures(mainterm, {"title', 'codes', '_level"})
            if varying_structures:
                self.execute_single_level_5(mainterm)
            else:
                raise ValueError("Code not prepared for mainterm's keys -> execute_single_level()")
        else:
            raise ValueError("Code not prepared mainterm's keys -> execute_single_level()") 

            
    def execute_single_level_1(self, mainterm):
        print("--------execute_single_level_1--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            None.
        """
        # This function is called in execute_single_level()
        # This function handles a "see" tag with or without children
        # It points to a sub-function that is built to handle the structure
        # Assumes subterms all have same key structure (determined by check_for_varying_subterm_structures) (Logan working on)
        first_subterm = mainterm["term"][0]
        # If type str this indicates the "see" key has no children, execute function built to handle.
        if isinstance(first_subterm["see"], str):
            self.execute_single_level_1_1(mainterm) 
        # If "see" key has children, execute based on structure returned
        elif {"tab", "__text"} == first_subterm["see"].keys():
            self.execute_single_level_1_2(mainterm)
        elif {"codes", "__text"} == first_subterm["see"].keys():
            self.execute_single_level_1_2(mainterm)
        else:
            raise ValueError("Code not prepared for mainterm key structure -> execute_single_level_1")

    def execute_single_level_1_1(self, mainterm):
        print("--------execute_single_level_1_1--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            None.
        """
        # This function is called in execute_single_level_1()
        # This function handles mainterm objects containing a "see" key that does not have children
        # Get user's selection of new mainterm of focus
        user_input = self.get_render_ask_next_level_terms(mainterm, "see")
        # Re-query the 'mainterms' generator to find the mainterm that matches user's selection
        # Create new generator object so that new search starts at the beginning of the mainterms
        # If use generator object already in memory you will start your iteration whereever the last iteration left off
        mainterms = self.create_new_mainterm_generator(index)
        for new_mainterm in mainterms:
            if new_mainterm["title"] == user_input:
                self.term_found_flag = True
                self.execute_tree(new_mainterm)
                break
        # If we didnt find a valid response, raise LookupError
        if not self.term_found_flag:
            raise LookupError("Code not prepared for mainterm key structure -> execute_single_level_1_1")
    
    def execute_single_level_1_2(self, mainterm):
        print("--------execute_single_level_1_2--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            None.
        """
        # This function is called in execute_single_level_1()
        # This function handles mainterm objects containing a "see" key that does have children
        # See keys require a second query for a new lookup term
        # Get user's selection of new mainterm of focus
        user_input = self.get_render_ask_next_level_terms(mainterm, "see", "__text")
        # Searching subterms to find new Mainterm object in focus
        for new_mainterm in mainterm["term"]:
            if new_mainterm["see"]["__text"] == user_input:
                # Executing with new mainterm
                self.term_found_flag = True
                self.execute_tree(new_mainterm)
                break
        # If we didnt find a valid response, raise ValueError
        if not self.term_found_flag:
            raise LookupError("Code not prepared for mainterm key structure -> execute_single_level_1_2")
                
    def execute_single_level_2(self, mainterm):
        print("--------execute_single_level_2--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            None
        """
        # This function is called in execute_single_level()
        # This function handles a "see" tag that contains levels
        # Get user's selection of new mainterm of focus
        user_input = self.get_render_ask_next_level_terms(mainterm, "title")
        # Searching subterms to find new Mainterm object in focus
        for new_mainterm in mainterm["term"]:
            if new_mainterm["title"] == user_input:
                # Executing with new mainterm
                self.term_found_flag = True
                self.execute_tree(new_mainterm)
                break
        # If we didnt find a valid response, raise ValueError
        if not self.term_found_flag:
            raise LookupError("Code not prepared for mainterm key structure -> execute_single_level_2")
                
    def execute_single_level_3(self, mainterm):
        print("--------execute_single_level_3--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            None
        """
        # This function is called in execute_single_level()
        # This function handles a "use" tag with or without children
        # Assumes subterms all have same key structure (determined by check_for_varying_subterm_structures)
        first_subterm = mainterm["term"][0]
        # If type str, this indicates the "use" key has no children
        if isinstance(first_subterm["use"], str):
            # Returns string of new mainterm of focus based on user response in get_render_ask_next_level_terms()
            user_input = self.get_render_ask_next_level_terms(mainterm, "use")
            # Search subterms to find new Mainterm object in focus
            for new_mainterm in mainterm["term"]:
                # Execute with new mainterm
                if new_mainterm["use"] == user_input:
                    self.term_found_flag = True
                    self.execute_tree(new_mainterm)
                    break
            # If we didnt find a valid response, raise ValueError
            if not self.term_found_flag:
                raise LookupError("Code not prepared for mainterm key structure -> execute_single_level_3")
        else:
            # If "use" key has children, execute based on structure returned
            if {"tab", "__text"} == first_subterm["use"].keys():
                # Returns string of new mainterm of focus based on user response in get_render_ask_next_level_terms()
                user_input = self.get_render_ask_next_level_terms(mainterm, "use", "__text")
                for new_mainterm in mainterm["term"]:
                    if new_mainterm["use"]["__text"] == user_input:
                        self.term_found_flag = True
                        self.execute_tree(new_mainterm)
                        break 
                # If we didnt find a valid response, raise ValueError
                if not self.term_found_flag:
                    raise LookupError("Code not prepared for mainterm key structure -> execute_single_level_3")
            else:
                raise ValueError("Code not prepared for mainterm key structure -> execute_single_level_3")
                
    def execute_single_level_4(self, mainterm):
        print("--------execute_single_level_4--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            None.
        """
        # This function is called in execute_single_level()
        # This function handles mainterm objects with subterms that contain a "code" key
        # Get number of final code's available 
        len_choices = len(mainterm["term"])
        # Get list of available codes
        choices = [term["code"] for term in mainterm["term"]]
        # Return codes to user
        print(f"""
You have {len_choices} choices for final codes related to term '{mainterm['title']}'. Choose the code that works best for this medical case. No further guidance given.""")
        print(choices)
        
    def execute_single_level_5(self, mainterm):
        print("--------execute_single_level_5--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            None.
        """
        # This function is called in execute_single_level()
        # This function is used to handle multiple subterm structures in the same mainterm
        # This function only works when 'code' and 'codes' are available as subterms in a mainterm's 'term' list
        # Add functionality here to handle other varying structures as need
        final_codes = []
        partial_codes = []
        for term in mainterm["term"]:
            try:
                # Create list of final codes
                code_data = (term["code"], term["title"])
                final_codes.append(code_data)
            except KeyError:
                # Create list of partial codes
                codes_data = (term["codes"], term["title"])
                partial_codes.append(codes_data)
        # Return codes to user
        print(f"""
Choices for Final codes: {final_codes}""")
        print(f"Choices for un-finished codes: {partial_codes}")

class Mainterm_Parser(Parser):
    def parent_execute(self, mainterm):
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            None
        """
        # This function is called when there are no levels in the Mainterm object in focus
        # Depending on the mainterm's key structure, an execute function built to handle given structure is called
        if {"title", "use"} == mainterm.keys():
            self.execute_group_1(mainterm)
        elif {"title", "see"} == mainterm.keys():
            self.execute_group_2(mainterm)
        elif {"title", "term"} == mainterm.keys():
            self.execute_tree(mainterm)
        elif {"title", "tab"} == mainterm.keys():
            self.execute_group_5(mainterm)
        elif {"title", "codes"} == mainterm.keys():
            self.execute_group_6(mainterm)
        elif {"title", "code"} == mainterm.keys():
            self.execute_group_4(mainterm)
        elif {"title", "code", "term"} == mainterm.keys():
            self.execute_group_7(mainterm)
        elif {"title", "code", "_level"} == mainterm.keys():
            self.execute_group_4(mainterm)
        elif {"see", "_level"} == mainterm.keys():
            self.execute_group_2(mainterm)
        elif {"use", "_level"} == mainterm.keys():
            self.execute_group_1(mainterm)
        elif {"title", "see", "_level"} == mainterm.keys():
            self.execute_group_2(mainterm)
        else:
            pprint(mainterm)
            raise LookupError("Code not prepared for mainterm key structure -> parent_execute()")
            
    def progress_through_levels_execute(self, mainterm):
        print("--------progress_through_levels_execute--------")
        # This function is called in Parser().progress_through_levels()
        # It uses sub-functions defined in the Mainterm_Parser() class to complete queries
        # Depending on the key structure of the passed 'mainterm', this function will call sub-function built to handle
        if {'title', 'codes', '_level'} == mainterm.keys():
            self.execute_group_6(mainterm)  
        elif {'title', 'code', '_level'} == mainterm.keys():
            self.execute_group_4(mainterm)
        elif {'see', '_level'} == mainterm.keys():
            self.execute_group_2(mainterm)
        elif {'use', '_level'} == mainterm.keys():
            self.execute_group_1(mainterm)
        elif {'title', 'see', '_level'} == mainterm.keys():
            self.execute_group_2(mainterm)
        elif {'code', '_level'} == mainterm.keys():
            self.execute_group_4(mainterm)
        elif {'title', 'tab', '_level'} == mainterm.keys():
            self.execute_group_5(mainterm)
#         elif {"title", "term", "level"}:
#             pass
        elif {"_level"} == mainterm.keys():
            print(mainterm)
            raise LookupError("Code not prepared for mainterm key structure -> progress_through_levels_execute()")
        else:
            pprint(mainterm)
            raise LookupError("Code not prepared for mainterm key structure -> progress_through_levels_execute()")
    
    def execute_group_1(self, mainterm):
        print("--------execute_group_1--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            None.
        """
        # This function is called in parent_execute() and progress_through_levels_execute()
        # This function points to sub-functions that handle mainterm objects containing a "use" key
        # If "use" key returns a string then it has no children, execute function built to handle.
        if isinstance(mainterm["use"], str):
            self.execute_group_1_1(mainterm)
        # If the "use" key has children, execute based on children's key structure
        elif {"tab", "__text"} == mainterm["use"].keys():
            self.execute_group_1_2(mainterm)
        else:
            pprint(mainterm)
            raise LookupError("Code not prepared for mainterm key structure -> execute_group_1()")

    
    def execute_group_1_1(self, mainterm):
        print("--------execute_group_1_1--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            None.
        """
        # This function is called in execute_group_1()
        # This function is used to handle mainterm objects that contain a "use" key that has no children
        # This function returns a term that corresponds to a code in a PCS Table
        # This term may be a:
            # Body Part Key
            # Device Key
            # Substance Key
            # Device Aggregation Table
                # Contains entries that correlate a specific PCS device value to a general device value
                # which can be used in PCS tables containing only general values
        print(f"""
Use the code associated with term '{mainterm['use']}' in the PCS Table.""")

    def execute_group_1_2(self, mainterm):
        print("--------execute_group_1_2--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            None
        """
        # This function is called in execute_group_1()
        # This function is used to handle mainterm objects that contain a "use" key that has no children
        # This function returns the PCS Table which the user needs to use
        # It also returns text that may correspond to a pos. 4-7 code in a PCS Row inside that PCS Table
        table = mainterm["use"]["tab"]
        text = mainterm["use"]["__text"]
        print(f"""
Go to table {table}, use PCS Row containing text '{text}' in pos. 4-7 values.""")

                
    def execute_group_2(self, mainterm):
        print("--------execute_group_2--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            None.
        """
        # This function is called in parent_execute() and progress_through_levels_execute()
        # This function points to sub-functions that handle mainterm objects containing a "see" key
        # If mainterm's "see" key returns a string then it has no children, execute function built to handle.
        if isinstance(mainterm["see"], str):
            self.execute_group_2_1(mainterm)
        # If mainterm's "see" key has children, execute based on structure returned
        elif {"codes", "__text"} == mainterm["see"].keys():
            self.execute_group_2_2(mainterm)
        elif {"tab", "__text"} == mainterm["see"].keys():
            self.execute_group_2_3(mainterm)
        else:
            pprint(mainterm)
            raise LookupError("Code not prepared for mainterm key structure -> progress_through_levels_execute()")
        
    
    def execute_group_2_1(self, mainterm):
        print("--------execute_group_2_1--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            None.
        """
        # This function is called in execute_group_2()
        # This function handles mainterm objects with a "see" key
        new_term = mainterm["see"]
        print(f"--Redirected to term '{new_term}'.") # Logging
        # Create new generator object so that new search starts at the beginning of the mainterms
        # If use generator object already in memory you will start your iteration whereever the last iteration left off
        mainterms = self.create_new_mainterm_generator(index)
        for new_mainterm_1 in mainterms:
            # print(new_mainterm_1["title"], new_term)
            # Re-query mainterms to find new_mainterm object with matching "title" 
            # "title" value must match the original mainterm's "see" value
            if new_mainterm_1["title"] == new_term:
                print(f"--Found '{new_term}' on first attempt") # Logging
                self.term_found_flag = True
                self.execute_tree(new_mainterm_1)
                break
            else:
                # Split value returned from "see" key to re-query data for match
                # When a "see" value has multiple terms separated by ", " that means they have given us a subterm(s) (second, third term) to look for within the mainterm (first term)
                split_term = new_term.split(", ")
                if len(split_term) == 2:
                    # If there are two terms, execute function that can handle
                    self.execute_group_2_1_1(split_term)
                    break
                elif len(split_term) >= 3:
                    # If there are three or more terms, raise error. Need functionality
                    pprint(f"Mainterm: {new_mainterm_1}")
                    raise ValueError("ERROR 1: Found 'see' tag that wasn't identified on re-query. Need to write function for specific use case. See execute_group_2_1().")
        if not self.term_found_flag:
            raise LookupError("Code not prepared for mainterm key structure -> execute_group_2_1()")
    
    def execute_group_2_1_1(self, split_term):
        print("--------execute_group_2_1_1--------")
        # This function is called in execute_group_2_1()
        # This function re-queries the data to find new_mainterm given by "see" value
        # Once it finds the parent_search_term, it will find the child_search_term within the parent_search_term
        # Unpack split_term
        parent_search_term, child_search_term = split_term
        print(f"--Looking for new parent term: {parent_search_term}") # Logging
        # Re-query the database to find first search term
        # Create new generator object so that new search starts at the beginning of the mainterms
        # If use generator object in memory this iteration will start where last iteration left off
        mainterms = self.create_new_mainterm_generator(index)
        for new_mainterm_2 in mainterms:
            if new_mainterm_2["title"] == parent_search_term:
                # If find first search term, look for second search term
                for subterm in new_mainterm_2["term"]:
                    if subterm["title"] == child_search_term:
                        # If find second search term, execute
                        print(f"--Found child term: {child_search_term}")
                        self.term_found_flag = True
                        self.execute_tree(subterm)
                        break
        if not self.term_found_flag:
            raise LookupError("Code not prepared for mainterm key structure -> execute_group_2_1_1()")
    
    def execute_group_2_2(self, mainterm):
        print("--------execute_group_2_2--------")
        # This function is called in execute_group_2()
        # This function handles mainterm objects with a "see" key that contains "codes" and "__text" keys
        code = mainterm["see"]["codes"]
        text = mainterm["see"]["__text"]
        print(f"""
Go to table '{code[:3]}', located at '{text}'.
Position 4 and greater code(s): '{code[3:]}'
Each code corresponds to it's respective position number.""")
        
    def execute_group_2_3(self, mainterm):
        print("--------execute_group_2_3--------")
        # This function is called in execute_group_2()
        # This function handles mainterm objects with a "see" key that contains "tab" and "__text" keys
        table = mainterm["see"]["tab"]
        text = mainterm["see"]["__text"]
        print(f"""
Go to table '{table}', located at sections '{text}'.
The 'sections' may also correspond to a pos. 4-7 value in a PCS Row in the given PCS Table""")
            
    def execute_group_4(self, mainterm):
        print("--------execute_group_4--------")
        # This function is called in Mainterm_Parser().parent_execute() and Mainterm_Parser().progress_through_levels_execute()
        # This function handles a mainterm object with keys:
            # {"title", "code"}
            # {'code', '_level'}
            # {'title', 'code', '_level'}
        try:
            # If "mainterm" has a "title" key, display "title" in return
            print(f"""
Use final code: {mainterm['code']} with description '{mainterm['title']}'.""")
        except KeyError:
            # If no title key, only display "code"
            print(f"""
Use final code: {mainterm['code']}. No further information given.""")
        
    def execute_group_5(self, mainterm):
        print("--------execute_group_5--------")
        # This function is called in Mainterm_Parser().parent_execute() and Mainterm_Parser().progress_through_levels_execute()
        # This function handles a mainterm object with keys:
            # {"title", "tab"}
            # {'title', 'tab', '_level'}
        table = mainterm["tab"]
        print(f"""
Go to table: {table}. No additional guidance given.""")

    def execute_group_6(self, mainterm):
        print("--------execute_group_6--------")
        # This function is called in Mainterm_Parser().parent_execute() and Mainterm_Parser().progress_through_levels_execute()
        # This function handles a mainterm object with keys:
            # "title", "codes"}
            # {'title', 'codes', '_level'}
        code = mainterm["codes"]
        print(f"""
Go to table: {code[:3]}
Position 4 and greater code(s): '{code[3:]}'
Each code corresponds to it's respective position number.""")

    def execute_group_7(self, mainterm):
        print("--------execute_group_7--------")
        # This function is called in Mainterm_Parser().parent_execute()
        # This function handles a "mainterm" with keys:
            # {"title", "code", "term"}
        # Get "code", "title" values for next level of terms
        code = mainterm["code"]
        level_1_terms = self.get_next_level_title_values(mainterm)
        # Display "code" to user and ask if any next_level_terms apply to this medical case
        user_input = input(f"""
Use code: {code}. If this case involves any of the following terms, {level_1_terms}, press 'y' now. If not, press 'n' to exit.""")
        if user_input == "y":
            # If next level terms apply, execute
            self.execute_tree(mainterm)

################################################# End Class Definitions #################################################
#########################################################################################################################

user_flag = "y" # Flag used to see if user wants to choose a different term
while user_flag == "y":
    # Creat generator of all 'letter' objects
    letters = (letter for letter in index["ICD10PCS.index"]["letter"])
    # Create generator of all 'mainterm' objects
    mainterms = (mainterms for letter in letters for mainterms in letter["mainTerm"])
    # Ask user for query mainterm
    user_mainterm = input("Enter the medical term you want to search for : ")
    # Search 'mainterms' for matching mainterm to user query
    for mainterm in mainterms:
        # If found matching mainterm
        if mainterm["title"] == user_mainterm:
            # Execute the mainterm
            parser = Parser()
            parser.execute_tree(mainterm, single_level_check=True)
            break
    user_flag = input("\nDo you want to search another term? (y/n) : ").lower()