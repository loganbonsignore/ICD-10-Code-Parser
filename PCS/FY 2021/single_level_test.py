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
        self.term_found_flag = False # Flag for ensuring mainterm found. Used for debugging.
        self.pcs_component = False # Flag to let output function know if need to account for PCS Table component.

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
            single_level_parser.execute_single_level(mainterm)
        elif not levels:
            print("--------PARENT EXECUTE--------")
            # Used to execute mainterms that do not have levels
            mainterm_parser.parent_execute(mainterm)
        else:
            # print("--------PROGRESS THROUGH LEVELS--------")
            # # Used to execute mainterms with subterms that have "_level" of 2 or greater
            # self.progress_through_levels(mainterm)

            # Not testing for this
            global test_flag
            test_flag = "No Test"
    
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
                mainterm_parser.progress_through_levels_execute(mainterm)
                level_flag = False
            elif len(new_level_terms) == 1:
                # Find new_level_term. Auto select the first term from the new_level_terms list because only one term available
                new_level_term = new_level_terms[0]
                print(f"Automatically choosing term, '{new_level_term}', because it's the only choice available.")
                # Re-query mainterm object to find subterm that matches our new_level_term
                # Start another while loop with updated mainterm object
                mainterm = self.find_matching_mainterm_to_user_input(mainterm, new_level_term)
            else:
                # # If more than one next level choice, ask user to choose
                # print(new_level_terms)
                # user_input = input("Choose term : ")
                # # If user's choice does not match a choice in new_level_terms
                # if user_input not in new_level_terms:
                #     user_input = self.handle_bad_user_query(user_input, new_level_terms)
                # # Find new mainterm object based on user choice above
                # mainterm = self.find_matching_mainterm_to_user_input(mainterm, user_input)
                # # Check for levels on new mainterm
                # levels = self.check_for_levels_in_mainterm(mainterm)
                # if not levels:
                #     # If no more levels, execute with final mainterm
                #     # If more levels, start another while loop iteration
                #     level_flag = False
                #     mainterm_parser.progress_through_levels_execute(mainterm)

                ### TESTING ###
                # Indicate term note being tested
                # Doing this because We are testing terms with only one level
                global test_flag
                test_flag = "No Test"
                break
    
    def find_matching_mainterm_to_user_input(self, mainterm, user_input):
        """
        Args
            mainterm -> Mainterm object in focus.
            user_input -> User's choice on subterm to choose next.
        Returns:
            Subterm object if match to user's input is found.
        """
        # This function is called in progress_through_levels()
        # This function iterates through next level terms and returns the term with a 'title' or 'see' tag equal to user_input
        # This function returns a 'mainterm' object or raises LookupError
        # Find new mainterm object based on user choice above
        for subterm in mainterm["term"]:
            try:
                # Look for 'title' value that matches user input
                if subterm["title"] == user_input:
                    return subterm
            except KeyError:
                try:
                    # If no 'title' value, look for 'see' value that matches user input
                    if subterm["see"] == user_input:
                        return subterm
                except KeyError:
                    try:
                        if subterm["code"] == user_input:
                            return subterm
                    except KeyError:

                        ### ADDED ###
                        global test_flag
                        #Indicate failed test
                        test_flag = False

                        # If no 'title' or 'see' match, raise error
                        # raise LookupError("Could not find user's term in next_level_choices. Checked for a 'see', 'title', and 'code' tag. -> progress_through_levels()")

    
    def handle_bad_user_query(self, user_input, new_level_terms):
        """
        Args
            user_input -> User's choice on subterm to choose next.
            new_level_terms -> All possible choices for the user to make
        Returns:
            New user input that matches a usable term
        """
        # This function is called in progress_through_levels() and get_render_ask_next_level_terms()
        # If a user searches for a term that is not valid, give user three more trys
        # If user query term is not a valid term raise LookupError
        bad_query_flag = 0
        # User gets 5 query trys before throwing error
        while user_input not in new_level_terms and bad_query_flag <= 3:
            print("Your choice is not valid. Please try again.")
            user_input = input("Choose term : ")
            bad_query_flag += 1
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
                    # Check for "term" key in sub_term
                    if subterm["term"]:
                        # This indicates multiple levels
                        return True
                except KeyError:
                    pass
            try:
                # Check for level term on one of subterms
                if mainterm["term"][0]["_level"]:
                    # This indicates multiple level 1 terms
                    return "level_1"
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
        # This function returns the "title" or "see" value of each next level subterm in a list
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
                        try:
                            title = level_term["code"]
                        except KeyError:
                            # Raise error if cannot find text to use in 'title' or 'see'
                            pprint(mainterm)

                            ### ADDED ###
                            global test_flag
                            #Indicate failed test
                            test_flag = False
        
                            # raise LookupError("Could not determine which text to be used when retrieveing next level values. See get_next_level_title_values()")
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
            LookupError
        """
        accounted_for_structures = [
            {'title', 'codes', '_level'}, # Accounted for in execute_single_level_5
            {'title', 'code', '_level'}, # Accounted for in execute_single_level_5
        ]
        # This function interates through each subterm to see if subterm structures vary from one another
        # It will raise LookupError if a mainterm structure is found that our code isn't prepared to handle
        # set_like_object is passed to the function and is a set of the first subterm's keys
        for term in mainterm["term"]:
            # Extracting keys of subterm
            term_keys = term.keys()
            # Iterating through subterm keys to check if structures vary
            for key in term_keys:
                # If the subterm's key is not in passed variable set_like_object
                # This means there is a subterm that contains a key that is different from the other subterm's keys
                if key not in set_like_object:
                    # Iterate through subterms and check that keys are not in accounted_for_structures
                    for subterm in mainterm["term"]:
                        # If not in accounted_for_structures, raise LookupError
                        if subterm.keys() in accounted_for_structures:
                            # This True value is used in execute_single_level()
                            return True
                        else:
                            pprint(mainterm)

                            ### ADDED ###
                            global test_flag
                            #Indicate failed test
                            test_flag = False

                            # raise LookupError("One subterm in the mainterm contains a key that is different from the other subterm keys and it is not accounted for.")
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
                try:
                    text_choices = [term["__text"] for term in mainterm["term"]]
                except KeyError:
                    try:
                        text_choices = [term["see"] for term in mainterm["term"]]
                    except KeyError:
                        # This mainterm has a blank subterm that does not contain a 'title' value
                        # This is used to catch that error
                        # Use this list to add terms that have errors like this
                        # May want to create a member variable to represent
                        if mainterm["title"] in ["Radiation Therapy"]:
                            text_choices = []
                            for subterm in mainterm["term"]:
                                try:
                                    text_choices.append(subterm["see"])
                                except KeyError:
                                    # Skipping one subterm that has no title value
                                    # Ex: Radiation Therapy'
                                    pass
                        else:
                            pprint(mainterm)

                            ### ADDED ###
                            global test_flag
                            #Indicate failed test
                            test_flag = False

                            # raise LookupError("Could not find term to use as 'title' of subterm. -> get_render_ask_next_level_terms()")
        print(text_choices)
        user_input = input("Choose term that most correlates to this medical case: ")
        if user_input in text_choices:
            return user_input
        else:
            return self.handle_bad_user_query(user_input, text_choices)

    def create_new_mainterm_generator(self, index):
        """
        Args
            index -> JSON document representing the PCS Index.
        Return
            Generator object of all 'mainterm' objects
        """
        # This function is called in: execute_single_level_1_1(), execute_group_2_1(), custom_search(), handle_pcs_table_component(), execute_group_2_1_1()
        # This function is used to create a new generator object of all 'mainterm' objects
        # It is needed in situations where we are re-querying the mainterms and have already iterated through a generator object
        # If we dont create a new generator object, the next iteration on that object will start where the last iteration left off
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
        # It returns LookupError if presented a mainterm structure it cannot handle
        # The first subterm is used to understand mainterm's structure
        # It is assumed that all subterms have the same key structure (which may not be true, Logan in progress of adding functionality)
        # Based on structure of subterms found, execute function that can handle structure
        
        ### ADDED ###
        global test_flag

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
                pprint(mainterm)

                ### ADDED ###
                #Indicate failed test
                test_flag = False

                # raise LookupError("Code not prepared for mainterm's keys -> execute_single_level()")
        else:
            pprint(mainterm)

            ### ADDED ###
            #Indicate failed test
            test_flag = False

            # raise LookupError("Code not prepared mainterm's keys -> execute_single_level()") 

            
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
            pprint(mainterm)

            ### ADDED ###
            global test_flag
            #Indicate failed test
            test_flag = False

            # raise LookupError("Code not prepared for mainterm key structure -> execute_single_level_1")

    def execute_single_level_1_1(self, mainterm):
        print("--------execute_single_level_1_1--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            None.
        """
        
        ### ADDED ###
        global test_flag

        # This function is called in execute_single_level_1()
        # This function handles mainterm objects containing a "see" key that does not have children
        # Ensure term_found_flag is False
        self.term_found_flag = False
        # Get user's selection of new mainterm of focus
        user_input = self.get_render_ask_next_level_terms(mainterm, "see")
        # Re-query the 'mainterms' generator to find the mainterm that matches user's selection
        # Create new generator object so that new search starts at the beginning of the mainterms
        mainterms = self.create_new_mainterm_generator(index)
        for new_mainterm in mainterms:
            if new_mainterm["title"] == user_input:
                self.term_found_flag = True
                self.execute_tree(new_mainterm)
                break
        # Trying to execute "see" tag with specific structure (Ex: "Brachytherapy, CivaSheet(R)")
        if not self.term_found_flag:
            try:
                for new_mainterm_1 in mainterm["term"]:
                    if new_mainterm_1["see"] == user_input:
                        self.term_found_flag = True
                        mainterm_parser.execute_group_2_1(new_mainterm_1)
            except KeyError:

                ### ADDED ###
                #Indicate failed test
                test_flag = False

                # raise LookupError("Code not prepared for mainterm key structure -> execute_single_level_1_1()")
        # If we didnt find a valid response, raise LookupError
        if not self.term_found_flag:

            ### ADDED ###
            #Indicate failed test
            test_flag = False

            # raise LookupError("Code not prepared for mainterm key structure -> execute_single_level_1_1")
    
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
        # Ensure term_found_flag is False
        self.term_found_flag = False
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
        # If we didnt find a valid response, raise LookupError
        if not self.term_found_flag:

            ### ADDED ###
            global test_flag
            #Indicate failed test
            test_flag = False

            # raise LookupError("Code not prepared for mainterm key structure -> execute_single_level_1_2")
             
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
        # Ensure term_found_flag is False
        self.term_found_flag = False
        # Get user's selection of new mainterm of focus
        user_input = self.get_render_ask_next_level_terms(mainterm, "title")
        # Searching subterms to find new Mainterm object in focus
        for new_mainterm in mainterm["term"]:
            if new_mainterm["title"] == user_input:
                # Executing with new mainterm
                self.term_found_flag = True
                self.execute_tree(new_mainterm)
                break
        # If we didnt find a valid response, raise LookupError
        if not self.term_found_flag:

            ### ADDED ###
            global test_flag
            #Indicate failed test
            test_flag = False

            # raise LookupError("Code not prepared for mainterm key structure -> execute_single_level_2")
                
    def execute_single_level_3(self, mainterm):
        print("--------execute_single_level_3--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            None
        """

        ### ADDED ###
        global test_flag

        # This function is called in execute_single_level()
        # This function handles a "use" tag with or without children
        # Ensure term_found_flag is False
        self.term_found_flag = False
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
            # If we didnt find a valid response, raise LookupError
            if not self.term_found_flag:

                ### ADDED ###
                #Indicate failed test
                test_flag = False

                # raise LookupError("Code not prepared for mainterm key structure -> execute_single_level_3")
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
                # If we didnt find a valid response, raise LookupError
                if not self.term_found_flag:

                    ### ADDED ###
                    #Indicate failed test
                    test_flag = False

                    # raise LookupError("Code not prepared for mainterm key structure -> execute_single_level_3")
            else:

                ### ADDED ###
                #Indicate failed test
                test_flag = False

                # raise LookupError("Code not prepared for mainterm key structure -> execute_single_level_3")
        
    def execute_single_level_4(self, mainterm):
        print("--------execute_single_level_4--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            Information to user in form of print(). Will integrate with PCS Table.
        """
        # Execute function
        # This function is called in execute_single_level()
        # This function handles mainterm objects with subterms that contain a "code" key
        # Get number of final code's available 
#         len_choices = len(mainterm["term"])
#         # Get list of available codes
#         choices = [term["code"] for term in mainterm["term"]]
#         # Return codes to user
#         print(f"""
# You have {len_choices} choices for final codes related to term '{mainterm['title']}'. Choose the code that works best for this medical case. No further guidance given.""")
#         print(choices)
#         # Check to see if given a 'qualifier' or 'device'
#         # Always found in 'see' key
#         if self.pcs_component:
#             print(f"Use {self.pcs_component[0]} '{self.pcs_component[1]}' in the PCS table.")
#             # Resetting pcs_component flag
#             self.pcs_component = False

        ### TESTING ###
        global test_flag
        # Testing to see if code can execute what it is intended to execute
        try:
            len_choices = len(mainterm["term"])
            choices = [term["code"] for term in mainterm["term"]]
            if self.pcs_component:
                # Testing components are present
                comp_1 = self.pcs_component[0]
                comp_2 = self.pcs_component[1]
                # Resetting pcs_component flag
                self.pcs_component = False
            test_flag = True
        except:
            # Indicates failed test
            test_flag = False

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
        # This function is built for subterms with 'code', 'codes', and "see" keys in a mainterm's 'term' list
        # Add functionality here to handle other varying structures as need

        # Check if 'code', 'codes' or 'see' are available in subterms's keys
        # Depending on outcome, execute function built to handle
        # Used as flag for code to determine structure
        see_structure_flag = False
        for subterm in mainterm["term"]:
            try:
                # 'code' key is available
                if subterm["code"]:
                    # Dont change see_structure_flag
                    pass
            except KeyError:
                try:
                    # 'codes' key is available
                    if subterm["codes"]:
                        # Dont change see_structure_flag
                        pass
                except KeyError:
                    try:
                        # 'see' key is available
                        if subterm["see"]:
                            # Change see structure flag
                            see_structure_flag = True
                    except:
                        pprint(mainterm)

                        ### ADDED ###
                        global test_flag
                        #Indicate failed test
                        test_flag = False

                        # raise LookupError("Unknown subterm structure found. Need function to handle -> execute_single_level_5()")
        # Ex: 'Abortion'
        # If only need functionality for "codes", "code", execute function built to handle
        if not see_structure_flag:
            self.execute_single_level_5_1(mainterm)
        # Ex: 'Phototherapy'
        else:
            # Execute function that can handle 'see' and 'codes' structures on the same level
            # Get users choice of next level term
            user_input = self.get_render_ask_next_level_terms(mainterm, "title")
            # Find user's term in subterm objects
            for mainterm_1 in mainterm["term"]:
                if mainterm_1["title"] == user_input:
                    # Execute with new mainterm object
                    self.execute_tree(mainterm_1, single_level_check=True)
                    break

    def execute_single_level_5_1(self, mainterm):
        print("--------execute_single_level_5_1--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            Information to user in form of print(). Will integrate with PCS Table.
        """
        # Execute function
        # This function handles mainterms with 'code' and 'codes' keys on the same level of subterms
        # Ex: 'Abortion'
#         final_codes = []
#         partial_codes = []
#         for term in mainterm["term"]:
#             try:
#                 # Create list of final codes
#                 code_data = (term["code"], term["title"])
#                 final_codes.append(code_data)
#             except KeyError:
#                 # Create list of partial codes
#                 codes_data = (term["codes"], term["title"])
#                 partial_codes.append(codes_data)
#         # Return codes to user
#         if len(final_codes) > 0:
#             print(f"""
# Choices for Final codes: {final_codes}""")
#         if len(partial_codes) > 0:
#             print(f"Choices for un-finished codes: {partial_codes}")
#         # If nothing is found, raise LookupError
#         if len(partial_codes) == 0 and len(final_codes) == 0:
#             raise LookupError("Not prepared for mainterm structure -> execute_single_level_5()")
#         # Check to see if given a 'qualifier' or 'device'
#         # Always found in 'see' key
#         if self.pcs_component:
#             print(f"Use {self.pcs_component[0]} '{self.pcs_component[1]}' in the PCS table.")
#             # Resetting pcs_component flag
#             self.pcs_component = False

        ### TESTING ###
        global test_flag
        try:
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
                if self.pcs_component:
                    # Testing components are present
                    comp_1 = self.pcs_component[0]
                    comp_2 = self.pcs_component[1]
                    # Resetting pcs_component flag
                    self.pcs_component = False
            test_flag = True
        except:
            test_flag = False

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
        elif {"title", "tab", "_level"} == mainterm.keys():
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
        elif {"title", "codes", "_level"} == mainterm.keys():
            self.execute_group_6(mainterm)
        else:
            pprint(mainterm)

            ### ADDED ###
            global test_flag
            #Indicate failed test
            test_flag = False

            # raise LookupError("Code not prepared for mainterm key structure -> parent_execute()")
            
    def progress_through_levels_execute(self, mainterm):
        print("--------progress_through_levels_execute--------")

        ### ADDED ###
        global test_flag

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
        elif {"_level"} == mainterm.keys():
            print(mainterm)

            ### ADDED ###
            #Indicate failed test
            test_flag = False

            # raise LookupError("Code not prepared for mainterm key structure -> progress_through_levels_execute()")
        else:    
            pprint(mainterm)

            ### ADDED ###
            #Indicate failed test
            test_flag = False

            # raise LookupError("Code not prepared for mainterm key structure -> progress_through_levels_execute()")
    
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

            ### ADDED ###
            global test_flag
            #Indicate failed test
            test_flag = False

            # raise LookupError("Code not prepared for mainterm key structure -> execute_group_1()")

    
    def execute_group_1_1(self, mainterm):
        print("--------execute_group_1_1--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            Information to user in form of print(). Will integrate with PCS Table.
        """
        # Execute Function
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
#         print(f"""
# Use the code associated with term '{mainterm['use']}' in the PCS Table.""")
#         # Check to see if given a 'qualifier' or 'device'
#         # Always found in 'see' key
#         if self.pcs_component:
#             print(f"Use {self.pcs_component[0]} '{self.pcs_component[1]}' in the PCS table.")
#             # Resetting pcs_component flag
#             self.pcs_component = False

        ### TESTING ###
        global test_flag
        try:
            test = mainterm['use']
            if self.pcs_component:
                comp_1 = self.pcs_component[0]
                comp_2 = self.pcs_component[1]
                # Resetting pcs_component flag
                self.pcs_component = False
                # Indicate successful test
            test_flag = True
        except KeyError:
            # Indicate failed test
            test_flag = False

    def execute_group_1_2(self, mainterm):
        print("--------execute_group_1_2--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            Information to user in form of print(). Will integrate with PCS Table.
        """
        # Execute Function
        # This function is called in execute_group_1()
        # This function is used to handle mainterm objects that contain a "use" key that has no children
        # This function returns the PCS Table which the user needs to use
        # It also returns text that may correspond to a pos. 4-7 code in a PCS Row inside that PCS Table
#         table = mainterm["use"]["tab"]
#         text = mainterm["use"]["__text"]
#         print(f"""
# Go to table {table}, use PCS Row containing text '{text}' in pos. 4-7 values.""")
#         # Check to see if given a 'qualifier' or 'device'
#         # Always found in 'see' key
#         if self.pcs_component:
#             print(f"Use {self.pcs_component[0]} '{self.pcs_component[1]}' in the PCS table.")
#             # Resetting pcs_component flag
#             self.pcs_component = False

        ### TESTING ###
        global test_flag
        try:
            table = mainterm["use"]["tab"]
            text = mainterm["use"]["__text"]
            if self.pcs_component:
                print(f"Use {self.pcs_component[0]} '{self.pcs_component[1]}' in the PCS table.")
                # Resetting pcs_component flag
                self.pcs_component = False
                # Indicate successful test
                test_flag = True
        except:
            # Indicate failed test
            test_flag = False

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

        ### ADDED ###
        global test_flag

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
        # Create new generator object
        mainterms = self.create_new_mainterm_generator(index)
        # Ensure term_found_flag is False
        self.term_found_flag = False
        # Re-query mainterms to find new_mainterm object with matching "title" 
        # "title" value must match the original mainterm's "see" value
        for new_mainterm_1 in mainterms:
            # If mainterm object's 'title' value is equal to our new search term, execute
            # Using capitalized case search term for specific use cases (Ex: "Diagnostic Audiology","Diagnostic imaging","Diagnostic radiology","Radiology, diagnostic","Nuclear scintigraphy")
            if new_mainterm_1["title"] == new_term or new_mainterm_1["title"] == new_term.capitalize():
                print(f"--Found '{new_term}' on first attempt") # Logging
                self.term_found_flag = True
                self.execute_tree(new_mainterm_1, single_level_check=True)
                break   
        # If we did not find a match
        # See if structure of new_term is two separate terms separated by commas
        if not self.term_found_flag:
            # Split value returned from "see" key to re-query data for match
            # When a "see" value has multiple terms separated by ", " that means they have given us a subterm(s) (second, third term) to look for within the mainterm (first term)
            split_term = new_term.split(", ")
            if len(split_term) == 2:
                # If there are two terms, execute function that can handle
                self.term_found_flag = True
                self.execute_group_2_1_1(split_term)
            elif len(split_term) == 3:
                # If there are three terms, execute function that can handle
                self.term_found_flag = True
                self.custom_search(new_term)
        # If we have still not found a match 
        if not self.term_found_flag:
            # Isolate first word from new_term
            first_word = new_term.split(" ")[0]
            # If first word is introduction... (Ex: 'Drotrecogin alfa, infusion', 'Eptifibatide, infusion')
            if first_word == "Introduction":
                # self.term_found_flag = True
                # print("NEED FUNCTION TO HANDLE. INTEGRATE TO PCS TABLE") 

                ### TESTING ###
                # Used to avoid raising error later
                self.term_found_flag = True
                # Indicate failed test
                test_flag = False

        # If we still havent found a match
        if not self.term_found_flag:
            # Look for words signifying a certain structure (Ex: Core needle biopsy, Punch biopsy)
            if "with qualifier" in new_term or "with device" in new_term:
                self.term_found_flag = True
                self.handle_pcs_table_component(new_term)
        # If still now match, throw LookupError
        if not self.term_found_flag:
            pprint(mainterm)

            ### ADDED ###
            #Indicate failed test
            test_flag = False

            # raise LookupError("Code not prepared for mainterm key structure -> execute_group_2_1()")

    def custom_search(self, new_term):
        print("--------custom_search--------")
        """
        Args
            new_term -> "see" value that contains 3 separate search terms in one string.
        Returns
            None.
        """

        ### ADDED ###
        global test_flag

        # This function is called in execute_group_2_1()
        # These are custom searches that are hard coded because of there unique "see" value structure 
        # 'Ligation, hemorrhoid'
        if new_term == "Occlusion, Lower Veins, Hemorrhoidal Plexus":
            # # Create new 'mainterms' generator object
            # mainterms = self.create_new_mainterm_generator(index)
            # # Find first search terms object with 'title' value of "Occlusion"
            # for new_mainterm_2 in mainterms:
            #     if new_mainterm_2["title"] == "Occlusion":
            #         # Find second search terms object with 'title' value of "Vein"
            #         for new_mainterm_3 in new_mainterm_2["term"]:
            #             if new_mainterm_3["title"] == "Vein":
            #                 # Find third search term's object with 'title' value of "Lower"
            #                 for new_mainterm_4 in new_mainterm_3["term"]:
            #                     if new_mainterm_4["title"] == "Lower":
            #                         code = new_mainterm_4["codes"]
            #                         # Used in execute function to notify that Index gave us a PCS Table component
            #                         self.pcs_component = ("qualifier", "Hemorrhoidal Plexus")
            #                         self.execute_group_6(new_mainterm_4)
            test_flag = True
        # 'Myocardial Bridge Release'
        elif new_term == "Release, Artery, Coronary":
            # # Create new 'mainterms' generator object
            # mainterms = self.create_new_mainterm_generator(index)
            # for new_mainterm_2 in mainterms:
            #     # Search for 'mainterm' object with 'title' value of "Release"
            #     if new_mainterm_2["title"] == "Release":
            #         for new_mainterm_3 in new_mainterm_2["term"]:
            #             # Search for subterm object with 'title' value of "Artery"
            #             if new_mainterm_3["title"] == "Artery":
            #                 for new_mainterm_4 in new_mainterm_3["term"]:
            #                     # Search for subterm object with 'title' value of "Coronary"
            #                     if new_mainterm_4["title"] == "Coronary":
            #                         self.execute_tree(new_mainterm_4)
            test_flag = True
        # Psychotherapy -> Individual -> Mental Health Services
        elif new_term == "Psychotherapy, Individual, Mental Health Services":
            # # Create new 'mainterms' generator object
            # mainterms = self.create_new_mainterm_generator(index)
            # for new_mainterm_2 in mainterms:
            #     # Search for 'mainterm' object with 'title' value of "Release"
            #     if new_mainterm_2["title"] == "Psychotherapy":
            #         for new_mainterm_3 in new_mainterm_2["term"]:
            #             # Search for subterm object with 'title' value of "Artery"
            #             if new_mainterm_3["title"] == "Individual":
            #                 for new_mainterm_4 in new_mainterm_3["term"]:
            #                     # Search for subterm object with 'title' value of "Coronary"
            #                     try:
            #                         if new_mainterm_4["title"] == "Mental Health Services":
            #                             self.execute_tree(new_mainterm_4, single_level_check=True)
            #                     except KeyError:
            #                         if new_mainterm_4["see"] == "Mental Health Services":
            #                             self.execute_tree(new_mainterm_4, single_level_check=True)
            test_flag = True
        else:

            ### ADDED ###
            #Indicate failed test
            test_flag = False

            # raise LookupError(f"Do not have a function build to handle lookup term '{new_term}' -> custom_search()")

    def handle_pcs_table_component(self, new_term):
        print("--------handle_pcs_table_component--------")
        """
        Args
            new_term -> "see" value that contains a string representing a new search term and PCS Table component.
        Returns
            None.
        """
        # This function is called in execute_group_2_1()
        # This function parses a string containing information returned from a "see" tag
        # The string tells us what the new search term is, the PCS column header to be used (pos), and the PCS component to be used
        # Ex: 'Core needle biopsy', 'Punch biopsy'
        # Spliting text returned as value of "see" tag
        split_text = new_term.split(" ")
        # Finding new search term (always first word)
        new_search_term = split_text[0]
        # Finding pcs table column header to be used
        pcs_pos = split_text[2]
        # Finding pcs term to be used under table's column header
        pcs_component = " ".join(split_text[3:])
        # Create new generator object
        mainterms = self.create_new_mainterm_generator(index)
        # Finding search term and executing
        for mainterm_1 in mainterms:
            if mainterm_1["title"] == new_search_term:
                # Flag to let output know if they gave us a pcs component
                # tuple will always have the 1st position be the pos word and second position be the component
                self.pcs_component = (pcs_pos, pcs_component)
                self.execute_tree(mainterm_1, single_level_check=True)

    def execute_group_2_1_1(self, split_term):
        print("--------execute_group_2_1_1--------")
        """
        Args
            split_term -> two individual search terms gathered from a "see" value
        Returns
            None.
        """
        # This function is called in execute_group_2_1()
        # This function re-queries the data to find new_mainterm given by "see" value
        # Once it finds the parent_search_term, it will find the child_search_term within the parent_search_term
        # Ensure term_found_flag is False
        self.term_found_flag = False
        # Unpack split_term
        parent_search_term, child_search_term = split_term
        print(f"--Looking for new parent term: {parent_search_term}") # Logging
        # Re-query the database to find first search term
        # Create new generator object
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

            ### ADDED ###
            global test_flag
            #Indicate failed test
            test_flag = False

            # raise LookupError("Code not prepared for mainterm key structure -> execute_group_2_1_1()")
    
    def execute_group_2_2(self, mainterm):
        print("--------execute_group_2_2--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            Information to user in form of print(). Will integrate with PCS Table.
        """
#         # Execute Function
#         # This function is called in execute_group_2()
#         # This function handles mainterm objects with a "see" key that contains "codes" and "__text" keys
#         code = mainterm["see"]["codes"]
#         text = mainterm["see"]["__text"]
#         print(f"""
# Go to table '{code[:3]}', located at '{text}'.
# Position 4 and greater code(s): '{code[3:]}'
# Each code corresponds to it's respective position number.""")
#         # Check to see if given a 'qualifier' or 'device'
#         # Always found in 'see' key
#         if self.pcs_component:
#             print(f"Use {self.pcs_component[0]} '{self.pcs_component[1]}' in the PCS table.")
#             # Resetting pcs_component flag
#             self.pcs_component = False

        ### TESTING ###
        global test_flag
        try:
            code = mainterm["see"]["codes"]
            text = mainterm["see"]["__text"]
            if self.pcs_component:
                comp_1 = self.pcs_component[0]
                comp_2 = self.pcs_component[1]
                # Resetting pcs_component flag
                self.pcs_component = False
            test_flag = True
        except:
            test_flag = False
        
    def execute_group_2_3(self, mainterm):
        print("--------execute_group_2_3--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            Information to user in form of print(). Will integrate with PCS Table.
        """
        # Execute Function
        # This function is called in execute_group_2()
        # This function handles mainterm objects with a "see" key that contains "tab" and "__text" keys
#         table = mainterm["see"]["tab"]
#         text = mainterm["see"]["__text"]
#         print(f"""
# Go to table '{table}', located at sections '{text}'.
# The 'sections' may also correspond to a pos. 4-7 value in a PCS Row in the given PCS Table""")
#         # Check to see if given a 'qualifier' or 'device'
#         # Always found in 'see' key
#         if self.pcs_component:
#             print(f"Use {self.pcs_component[0]} '{self.pcs_component[1]}' in the PCS table.")
#             # Resetting pcs_component flag
#             self.pcs_component = False

        ### TESTING ###
        global test_flag
        try:
            table = mainterm["see"]["tab"]
            text = mainterm["see"]["__text"]
            if self.pcs_component:
                comp_1 = self.pcs_component[0]
                comp_2 = self.pcs_component[1]
                # Resetting pcs_component flag
                self.pcs_component = False
            test_flag = True
        except:
            test_flag = False

        





    def execute_group_4(self, mainterm):
        print("--------execute_group_4--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            Information to user in form of print(). Will integrate with PCS Table.
        """
        # Execute Function
        # This function is called in Mainterm_Parser().parent_execute() and Mainterm_Parser().progress_through_levels_execute()
        # This function handles a mainterm object with keys:
            # {"title", "code"}
            # {'code', '_level'}
            # {'title', 'code', '_level'}
#         try:
#             # If "mainterm" has a "title" key, display "title" in return
#             print(f"""
# Use final code: {mainterm['code']} with description '{mainterm['title']}'.""")
#         except KeyError:
#             # If no title key, only display "code"
#             print(f"""
# Use final code: {mainterm['code']}. No further information given.""")
#         # Check to see if given a 'qualifier' or 'device'
#         # Always found in 'see' key
#         if self.pcs_component:
#             print(f"Use {self.pcs_component[0]} '{self.pcs_component[1]}' in the PCS table.")
#             # Resetting pcs_component flag
#             self.pcs_component = False

        ### ADDED ###
        global test_flag
        try:
            try:
                code = mainterm['code']
                title = mainterm['title']
            except KeyError:
                code = mainterm['code']
            if self.pcs_component:
                comp_1 = self.pcs_component[0]
                comp_2 = self.pcs_component[1]
                # Resetting pcs_component flag
                self.pcs_component = False
            test_flag = True
        except:
            test_flag = False
        
    def execute_group_5(self, mainterm):
        print("--------execute_group_5--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            Information to user in form of print(). Will integrate with PCS Table.
        """
        # Execute Function
        # This function is called in Mainterm_Parser().parent_execute() and Mainterm_Parser().progress_through_levels_execute()
        # This function handles a mainterm object with keys:
            # {"title", "tab"}
            # {'title', 'tab', '_level'}
#         table = mainterm["tab"]
#         print(f"""
# Go to table: {table}. No additional guidance given.""")
#         # Check to see if given a 'qualifier' or 'device'
#         # Always found in 'see' key
#         if self.pcs_component:
#             print(f"Use {self.pcs_component[0]} '{self.pcs_component[1]}' in the PCS table.")
#             # Resetting pcs_component flag
#             self.pcs_component = False

        ### ADDED ###
        global test_flag
        try:
            table = mainterm["tab"]
            if self.pcs_component:
                comp_1 = self.pcs_component[0]
                comp_2 = self.pcs_component[1]
                # Resetting pcs_component flag
                self.pcs_component = False
            test_flag = True
        except:
            test_flag = False

    def execute_group_6(self, mainterm):
        print("--------execute_group_6--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            Information to user in form of print(). Will integrate with PCS Table.
        """
        # Execute Function
        # This function is called in Mainterm_Parser().parent_execute() and Mainterm_Parser().progress_through_levels_execute()
        # This function handles a mainterm object with keys:
            # "title", "codes"}
            # {'title', 'codes', '_level'}
#         code = mainterm["codes"]
#         print(f"""
# Go to table: {code[:3]}
# Position 4 and greater code(s): '{code[3:]}'
# Each code corresponds to it's respective position number.""")
#         # Check to see if given a 'qualifier' or 'device'
#         # Always found in 'see' key
#         if self.pcs_component:
#             print(f"Use {self.pcs_component[0]} '{self.pcs_component[1]}' in the PCS table.")
#             # Resetting pcs_component flag
#             self.pcs_component = False

        ### TESTING ###
        global test_flag
        try:
            code = mainterm["codes"]
            if self.pcs_component:
                comp_1 = self.pcs_component[0]
                comp_2 = self.pcs_component[1]
                # Resetting pcs_component flag
                self.pcs_component = False
            test_flag = True
        except:
            test_flag = False

    def execute_group_7(self, mainterm):
        print("--------execute_group_7--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            Information to user in form of print(). Will integrate with PCS Table.
        """
        # Execute Function
        # This function is called in Mainterm_Parser().parent_execute()
        # This function handles a "mainterm" with keys:
            # {"title", "code", "term"}
        # Get "code", "title" values for next level of terms
#         code = mainterm["code"]
#         level_1_terms = self.get_next_level_title_values(mainterm)
#         # Display "code" to user and ask if any next_level_terms apply to this medical case
#         user_input = input(f"""
# Use code: {code}. If this case involves any of the following terms, {level_1_terms}, press 'y' now. If not, press 'n' to exit.""")
#         if user_input == "y":
#             # If next level terms apply, execute
#             self.execute_tree(mainterm)
#         # Check to see if given a 'qualifier' or 'device'
#         # Always found in 'see' key
#         if self.pcs_component:
#             print(f"Use {self.pcs_component[0]} '{self.pcs_component[1]}' in the PCS table.")
#             # Resetting pcs_component flag
#             self.pcs_component = False

                ### ADDED ###
        global test_flag
        test_flag = "No Test"  
        # Not testing these terms
        # These terms may have a second level from which the user needs to choose

################################################# End Class Definitions #################################################
#########################################################################################################################

single_level_parser = Single_Level_Parser()
mainterm_parser = Mainterm_Parser()

# user_flag = "y" # Flag used to determine if user wants to choose another term
# while user_flag == "y":
#     # Create generator object of all 'letter' objects
#     letters = (letter for letter in index["ICD10PCS.index"]["letter"])
#     # Create generator object of all 'mainterm' objects
#     mainterms = (mainterms for letter in letters for mainterms in letter["mainTerm"])
#     # Ask user for query mainterm
#     user_mainterm = input("Enter the medical term you want to search for : ")
#     # Search 'mainterms' for matching mainterm to user query
#     for mainterm in mainterms:
#         # If found matching mainterm
#         if mainterm["title"] == user_mainterm:
#             # Execute the mainterm
#             parser = Parser()
#             parser.execute_tree(mainterm, single_level_check=True)
#             break
#     user_flag = input("\nDo you want to search another term? (y/n) : ").lower()

# List of terms not tested in first round of testing
terms_not_tested = ['Abdominoplasty',
 'Abductor hallucis muscle',
 'Ablation',
 'Abrasion',
 'Accessory cephalic vein',
 'Acetabulectomy',
 'Acetabulofemoral joint',
 'Acetabuloplasty',
 'Achilles tendon',
 'Achillotenotomy, achillotomy',
 'Acoustic Pulse Thrombolysis',
 'Acromioclavicular ligament',
 'Acromion (process)',
 'Acromionectomy',
 'Acromioplasty',
 'ACUITY(tm) Steerable Lead',
 'Acupuncture',
 'Adductor brevis muscle',
 'Adductor hallucis muscle',
 'Adductor longus muscle',
 'Adductor magnus muscle',
 'Adenoidectomy',
 'Adhesiolysis',
 'Administration',
 'Adrenalectomy',
 'Advancement',
 'Advisa (MRI)',
 'Alimentation',
 'Alteration',
 'Alveolar process of mandible',
 'Alveolectomy',
 'Alveoloplasty',
 'Alveolotomy',
 'Amputation',
 'Analog radiography',
 'Analog radiology',
 'Anastomosis',
 'Anatomical snuffbox',
 'Angiectomy',
 'Angiocardiography',
 'Angiography',
 'Angioplasty',
 'Angiorrhaphy',
 'Angiotripsy',
 'Angular vein',
 'Annular ligament',
 'Annuloplasty',
 'Anoplasty',
 'Antebrachial fascia',
 'Anterior (pectoral) lymph node',
 'Anterior circumflex humeral artery',
 'Anterior cruciate ligament (ACL)',
 'Anterior facial vein',
 'Anterior intercostal artery',
 'Anterior lateral malleolar artery',
 'Anterior medial malleolar artery',
 'Anterior spinal artery',
 'Anterior tibial recurrent artery',
 'Anterior ulnar recurrent artery',
 'Anterior vertebral muscle',
 'Antihelix',
 'Antitragus',
 'Antrum of Highmore',
 'Aortography',
 'Aortoplasty',
 'Apical (subclavicular) lymph node',
 'Appendectomy',
 'Application',
 'Aqueous humour',
 'Arcuate artery',
 'Areola',
 'Arteriectomy',
 'Arteriography',
 'Arterioplasty',
 'Arteriorrhaphy',
 'Arterioscopy',
 'Arthrectomy',
 'Arthrocentesis',
 'Arthrodesis',
 'Arthrography',
 'Arthrolysis',
 'Arthropexy',
 'Arthroplasty',
 'Arthroplasty, radial head',
 'Arthroscopy',
 'Arthrotomy',
 'Artificial Sphincter',
 'Arytenoid muscle',
 'Ascending pharyngeal artery',
 'Aspiration, fine needle',
 'Assessment',
 'Assistance',
 'Atherectomy',
 'Atrioseptoplasty',
 'Attain Ability(R) lead',
 'Attain StarFix(R) (OTW) lead',
 'Audiology, diagnostic',
 'Auditory tube',
 'Auricle',
 'Autologous artery graft',
 'Autologous vein graft',
 'Autotransfusion',
 'Autotransplant',
 'Avulsion',
 'Axillary fascia',
 'Balanoplasty',
 'Balloon Pump',
 'Bandage, Elastic',
 'Banding',
 'Banding, laparoscopic (adjustable) gastric',
 'Baroreflex Activation Therapy(R) (BAT(R))',
 'Beam Radiation',
 'Biceps brachii muscle',
 'Biceps femoris muscle',
 'Bicipital aponeurosis',
 'Biopsy',
 'Bisection',
 'Blepharectomy',
 'Blepharoplasty',
 'Body of femur',
 'Body of fibula',
 'Bone anchored hearing device',
 'Bone Growth Stimulator',
 'Bone screw (interlocking)(lag)(pedicle)(recessed)',
 'Bony labyrinth',
 'Bony orbit',
 'Bony vestibule',
 'Brachial (lateral) lymph node',
 'Brachialis muscle',
 'Brachiocephalic vein',
 'Brachioradialis muscle',
 'Brachytherapy',
 'Brachytherapy, CivaSheet(R)',
 'Bronchography',
 'Bronchoplasty',
 'Bursectomy',
 'Bursography',
 'Bursotomy',
 'Bypass',
 'Calcaneocuboid joint',
 'Calcaneocuboid ligament',
 'Calcaneofibular ligament',
 'Calcaneus',
 'Cannulation',
 'Capitate bone',
 'Capsulorrhaphy, joint',
 'Cardiac Lead',
 'Cardiac resynchronization therapy (CRT) lead',
 'Cardiac Rhythm Related Device',
 'Caroticotympanic artery',
 'Carotid glomus',
 'Carotid sinus',
 'Carpectomy',
 'Carpometacarpal ligament',
 'Casting',
 'CAT scan',
 'Catheterization',
 'Cauterization',
 'Cecectomy',
 'Cecocolostomy',
 'Cecopexy',
 'Cecostomy',
 'Central axillary lymph node',
 'Cerclage',
 'Cerebral Embolic Filtration',
 'Cervical facet joint',
 'Cervical lymph node',
 'Cervicectomy',
 'Change device in',
 'Change device in or on',
 'Chemoembolization',
 'Chemotherapy, Infusion for cancer',
 'Chiropractic Manipulation',
 'Cholangiogram',
 'Cholecystectomy',
 'Cholecystojejunostomy',
 'Cholecystopexy',
 'Cholecystostomy',
 'Choledochectomy',
 'Choledochoplasty',
 'Chondrectomy',
 'Choroidectomy',
 'Ciliary body',
 'Circumflex iliac artery',
 'CivaSheet(R) Brachytherapy',
 'Clamp and rod internal fixation system (CRIF)',
 'Clamping',
 'Claviculectomy',
 'Claviculotomy',
 'Clipping, aneurysm',
 'Clitorectomy, clitoridectomy',
 'Closure',
 'Clysis',
 'Coagulation',
 'Coccygeus muscle',
 'Cochlea',
 'Cochlear implant (CI), multiple channel (electrode)',
 'Cochlear implant (CI), single channel (electrode)',
 'Colectomy',
 'Collapse',
 'Collection from',
 'Colofixation',
 'Colopexy',
 'Coloproctectomy',
 'Coloproctostomy',
 'Colostomy',
 'Colpectomy',
 'Colpopexy',
 'Colpoplasty',
 'Common digital vein',
 'Common facial vein',
 'Common interosseous artery',
 'Compression',
 'Computer Assisted Procedure',
 'Computerized Tomography (CT Scan)',
 'Condylectomy',
 'Condyloid process',
 'Condylotomy',
 'Condylysis',
 'Conjunctivoplasty',
 'Construction',
 'Consulta CRT-D',
 'Consulta CRT-P',
 'Contact Radiation',
 'Continuous Negative Airway Pressure',
 'Continuous Positive Airway Pressure',
 'Contraceptive Device',
 'Control bleeding in',
 'Conversion',
 'Cook Zenith(R) Fenestrated AAA Endovascular Graft',
 'Coracoacromial ligament',
 'Coracobrachialis muscle',
 'Coracoclavicular ligament',
 'Coracohumeral ligament',
 'Coracoid process',
 'Core needle biopsy',
 'Coronary arteriography',
 'Corox (OTW) Bipolar Lead',
 'Costatectomy',
 'Costectomy',
 'Costocervical trunk',
 'Costochondrectomy',
 'Costoclavicular ligament',
 'Costosternoplasty',
 'Costotomy',
 'Counseling',
 'Craniectomy',
 'Cranioplasty',
 'Craniotomy',
 'Creation',
 'Cribriform plate',
 'Cricothyroid artery',
 'Cricothyroid muscle',
 'Crural fascia',
 'Crushing, nerve',
 'Cryoablation',
 'Cryotherapy',
 'Cryptorchidectomy',
 'Cryptorchiectomy',
 'Cryptotomy',
 'CT scan',
 'Cubital lymph node',
 'Cuboid bone',
 'Cuboideonavicular joint',
 'Culdoplasty',
 'Cuneonavicular joint',
 'Cuneonavicular ligament',
 'Curettage',
 'Cystectomy',
 'Cystography',
 'Cystopexy',
 'Cystoplasty',
 'Cystourethrography',
 'Cystourethroplasty',
 'Debridement',
 'Decortication, lung',
 'Deep cervical fascia',
 'Deep cervical vein',
 'Deep circumflex iliac artery',
 'Deep facial vein',
 'Deep femoral (profunda femoris) vein',
 'Deep femoral artery',
 'Deep Inferior Epigastric Artery Perforator Flap',
 'Deep palmar arch',
 'Deferential artery',
 'Delivery',
 'Delta frame external fixator',
 'Delta III Reverse shoulder prosthesis',
 'Deltoid fascia',
 'Deltoid ligament',
 'Deltoid muscle',
 'Deltopectoral (infraclavicular) lymph node',
 'Denervation',
 'Densitometry',
 'Descending genicular artery',
 'Destruction',
 'Detachment',
 'Detorsion',
 'Diagnostic Audiology',
 'Diagnostic imaging',
 'Diagnostic radiology',
 'Dialysis',
 'Digital radiography, plain',
 'Dilation',
 'Disarticulation',
 'Discectomy, diskectomy',
 'Discography',
 'Dismembered pyeloplasty',
 'Distal humerus',
 'Distal humerus, involving joint',
 'Distal radioulnar joint',
 'Diversion',
 'Division',
 'Doppler study',
 'Dorsal metacarpal vein',
 'Dorsal metatarsal artery',
 'Dorsal metatarsal vein',
 'Dorsal scapular artery',
 'Dorsal venous arch',
 'Dorsalis pedis artery',
 'Drainage',
 'Dressing',
 'Ductus deferens',
 'Duodenectomy',
 'Duodenocystostomy',
 'Duodenoenterostomy',
 'Duodenostomy',
 'DynaNail Mini(R)',
 'DynaNail(R)',
 'Dynesys(R) Dynamic Stabilization System',
 'Earlobe',
 'Echography',
 'Ejaculatory duct',
 'EKOS(tm) EkoSonic(R) Endovascular System',
 'Electrical bone growth stimulator (EBGS)',
 'Electrocautery',
 'Electroconvulsive Therapy',
 'Electroshock therapy',
 'Ellipsys(R) vascular access system',
 'Eluvia(tm) Drug-Eluting Vascular Stent System',
 'Embolectomy',
 'Embolization',
 'Endarterectomy',
 'EndoAVF procedure',
 'Endovascular fistula creation',
 'Enlargement',
 'EnRhythm',
 'Enucleation',
 'Epididymectomy',
 'Epididymoplasty',
 'Epiphysiodesis',
 'Epiretinal Visual Prosthesis',
 'Epitrochlear lymph node',
 'Erector spinae muscle',
 'Esophagectomy',
 'Esophagocoloplasty',
 'Esophagoenterostomy',
 'Esophagoesophagostomy',
 'Esophagogastrectomy',
 'Esophagogastroplasty',
 'Esophagogastrostomy',
 'Esophagojejunostomy',
 'Esophagoplasty',
 'ESWL (extracorporeal shock wave lithotripsy)',
 'Ethmoidal air cell',
 'Ethmoidectomy',
 'Evacuation',
 'Evera (XT)(S)(DR/VR)',
 'Evisceration',
 'Examination',
 'Exchange',
 'Excision',
 'EXCLUDER(R) AAA Endoprosthesis',
 'EXCLUDER(R) IBE Endoprosthesis',
 'Exploration',
 'Extensor carpi radialis muscle',
 'Extensor carpi ulnaris muscle',
 'Extensor digitorum brevis muscle',
 'Extensor digitorum longus muscle',
 'Extensor hallucis brevis muscle',
 'Extensor hallucis longus muscle',
 'External auditory meatus',
 'External fixator',
 'External oblique muscle',
 'External pudendal artery',
 'External pudendal vein',
 'Extirpation',
 'Extracorporeal shock wave lithotripsy',
 'Extraction',
 'Facet replacement spinal stabilization device',
 'Fascia lata',
 'Fasciaplasty, fascioplasty',
 'Fasciotomy',
 'Feeding Device',
 'Femoral head',
 'Femoral lymph node',
 'Femoropatellar joint',
 'Femorotibial joint',
 'FGS (fluorescence-guided surgery)',
 'Fibular artery',
 'Fibularis brevis muscle',
 'Fibularis longus muscle',
 'Fimbriectomy',
 'Fine needle aspiration',
 'Fistulization',
 'Fitting',
 'Fixation, bone',
 'Flexor carpi radialis muscle',
 'Flexor carpi ulnaris muscle',
 'Flexor digitorum brevis muscle',
 'Flexor digitorum longus muscle',
 'Flexor hallucis brevis muscle',
 'Flexor hallucis longus muscle',
 'Flexor pollicis longus muscle',
 'Flow Diverter embolization device',
 'Fluorescence Guided Procedure',
 'Fluoroscopy',
 'Fluoroscopy, laser intraoperative',
 'Flushing',
 'Fovea',
 'Fragmentation',
 'Fragmentation, Ultrasonic',
 'Frenectomy',
 'Frenoplasty, frenuloplasty',
 'Frenotomy',
 'Frenulotomy',
 'Frenulumectomy',
 'Frontal vein',
 'Fulguration',
 'Fusion',
 'Fusion screw (compression)(lag)(locking)',
 'Ganglionectomy',
 'Gastrectomy',
 'Gastrocnemius muscle',
 'Gastrocolostomy',
 'Gastroduodenectomy',
 'Gastroenteroplasty',
 'Gastroenterostomy',
 'Gastrogastrostomy',
 'Gastrojejunostomy',
 'Gastropexy',
 'Gastroplasty',
 'Gastrostomy',
 'Gemellus muscle',
 'Gingivoplasty',
 'Glenohumeral joint',
 'Glenohumeral ligament',
 'Glenoid fossa (of scapula)',
 'Glenoid ligament (labrum)',
 'Glomectomy',
 'Glossectomy',
 'Glossopexy',
 'Glossoplasty',
 'Gluteal Artery Perforator Flap',
 'Gluteal vein',
 'Gluteus maximus muscle',
 'Gluteus medius muscle',
 'Gluteus minimus muscle',
 'GORE EXCLUDER(R) AAA Endoprosthesis',
 'GORE EXCLUDER(R) IBE Endoprosthesis',
 'Gracilis muscle',
 'Graft',
 'Great(er) saphenous vein',
 'Greater trochanter',
 'Greater tuberosity',
 'Guidance, catheter placement',
 'Hallux',
 'Hamate bone',
 'Head of fibula',
 'Hearing Device',
 'Heart Assist System',
 'Helix',
 'Hemilaminectomy',
 'Hemilaminotomy',
 'Hemispherectomy',
 'Hemithyroidectomy',
 'Hepatectomy',
 'Hepaticoduodenostomy',
 'Hepatopexy',
 'Herniorrhaphy',
 'Humeroradial joint',
 'Humeroulnar joint',
 'Humerus, distal',
 'Hydrotherapy',
 'Hymenectomy',
 'Hymenoplasty',
 'Hymenotomy',
 'Hyoid artery',
 'Hyperalimentation',
 'Hyperbaric oxygenation',
 'Hyperthermia',
 'Hypogastric artery',
 'Hypophysectomy',
 'Hypothenar muscle',
 'Hysterectomy',
 'Hysteropexy',
 'Hysterotrachelectomy',
 'Ileectomy',
 'Ileopexy',
 'Ileostomy',
 'Iliac crest',
 'Iliac fascia',
 'Iliacus muscle',
 'Iliofemoral ligament',
 'Iliolumbar artery',
 'Iliotibial tract (band)',
 'Ilium',
 'Ilizarov external fixator',
 'Ilizarov-Vecklich device',
 'Imaging, diagnostic',
 'Immobilization',
 'Immunotherapy, antineoplastic',
 'Impeller Pump',
 'Implantable cardioverter-defibrillator (ICD)',
 'Implantation',
 'Incision, abscess',
 'Incudectomy',
 'Incudopexy',
 'Incus',
 'Induction of labor',
 'Inferior epigastric artery',
 'Inferior genicular artery',
 'Inferior gluteal artery',
 'Inferior oblique muscle',
 'Inferior rectus muscle',
 'Inferior suprarenal artery',
 'Inferior tarsal plate',
 'Inferior thyroid vein',
 'Inferior tibiofibular joint',
 'Inferior ulnar collateral artery',
 'Inferior vesical artery',
 'Infraclavicular (deltopectoral) lymph node',
 'Infrahyoid muscle',
 'Infraspinatus fascia',
 'Infraspinatus muscle',
 'Infusion',
 'Infusion Device, Pump',
 'Infusion, glucarpidase',
 'Inguinal canal',
 'Inguinal triangle',
 'Injection',
 'Insertion',
 'Insertion of device in',
 'Inspection',
 'Instillation',
 'Insufflation',
 'Interbody fusion (spine) cage',
 'Interbody Fusion Device',
 'Intercarpal joint',
 'Intercarpal ligament',
 'Interclavicular ligament',
 'Intercostal muscle',
 'Intercuneiform joint',
 'Intercuneiform ligament',
 'Intermediate cuneiform bone',
 'Intermittent Negative Airway Pressure',
 'Intermittent Positive Airway Pressure',
 'Internal iliac vein',
 'Internal maxillary artery',
 'Internal oblique muscle',
 'Internal pudendal artery',
 'Internal pudendal vein',
 'Internal thoracic artery',
 'Interphalangeal (IP) joint',
 'Interphalangeal ligament',
 'Interrogation, cardiac rhythm related device',
 'Interruption',
 'Interspinalis muscle',
 'Interspinous process spinal stabilization device',
 'Intertransversarius muscle',
 'Intraluminal Device',
 'Intramedullary (IM) rod (nail)',
 'Intramedullary skeletal kinetic distractor (ISKD)',
 'Intraocular Telescope',
 'Intraoperative Radiation Therapy (IORT)',
 'Intravascular Lithotripsy (IVL)',
 'Intravascular ultrasound assisted thrombolysis',
 'Introduction of substance in or on',
 'Intubation',
 'Iridectomy',
 'Iridoplasty',
 'Irrigation',
 'Ischiofemoral ligament',
 'Ischium',
 'Jejunectomy',
 'Jejunocolostomy',
 'Jejunopexy',
 'Jejunostomy',
 'Joint fixation plate',
 'Joint spacer (antibiotic)',
 'Jugular lymph node',
 'Kappa',
 'Keratectomy, kerectomy',
 'Keratoplasty',
 'Keratotomy',
 'Kirschner wire (K-wire)',
 'Kuntscher nail',
 'Labial gland',
 'Labiectomy',
 'Lacrimal canaliculus',
 'Lacrimal punctum',
 'Lacrimal sac',
 'LAGB (laparoscopic adjustable gastric banding)',
 'Laminectomy',
 'Laminotomy',
 'Laparoscopic-assisted transanal pull-through',
 'Laparoscopy',
 'Laparotomy',
 'Laryngectomy',
 'Laryngoplasty',
 'Laser Interstitial Thermal Therapy',
 'Lateral (brachial) lymph node',
 'Lateral canthus',
 'Lateral collateral ligament (LCL)',
 'Lateral condyle of femur',
 'Lateral condyle of tibia',
 'Lateral cuneiform bone',
 'Lateral epicondyle of femur',
 'Lateral epicondyle of humerus',
 'Lateral malleolus',
 'Lateral meniscus',
 'Lateral plantar artery',
 'Lateral rectus muscle',
 'Lateral sacral artery',
 'Lateral sacral vein',
 'Lateral tarsal artery',
 'Lateral thoracic artery',
 'Latissimus dorsi muscle',
 'Latissimus Dorsi Myocutaneous Flap',
 'Lavage',
 'Lengthening',
 'Lesser saphenous vein',
 'Lesser trochanter',
 'Lesser tuberosity',
 'Levator palpebrae superioris muscle',
 'Levator scapulae muscle',
 'Levatores costarum muscle',
 'Ligament of head of fibula',
 'Ligament of the lateral malleolus',
 'Ligation',
 'Liner',
 'Lingual artery',
 'Lingulectomy, lung',
 'Lithoplasty',
 'Lithotripsy',
 'LITT (laser interstitial thermal therapy)',
 'LIVIAN(tm) CRT-D',
 'Lobectomy',
 'Localization',
 'Lumpectomy',
 'Lunate bone',
 'Lunotriquetral ligament',
 'Lymphadenectomy',
 'Lymphangiectomy',
 'Lymphangioplasty',
 'Lysis',
 'Macula',
 'Magnetic Resonance Imaging (MRI)',
 'Magnetic-guided radiofrequency endovascular fistula',
 'Malleus',
 'Mammaplasty, mammoplasty',
 'Mammary duct',
 'Mammary gland',
 'Mammectomy',
 'Mandibular notch',
 'Mandibulectomy',
 'Manipulation',
 'Mapping',
 'Marsupialization',
 'Massage, cardiac',
 'Mastectomy',
 'Mastoid (postauricular) lymph node',
 'Mastoid air cells',
 'Mastoid process',
 'Mastoidectomy',
 'Mastopexy',
 'Maxillary artery',
 'Measurement',
 'Medial canthus',
 'Medial collateral ligament (MCL)',
 'Medial condyle of femur',
 'Medial condyle of tibia',
 'Medial cuneiform bone',
 'Medial epicondyle of femur',
 'Medial epicondyle of humerus',
 'Medial malleolus',
 'Medial meniscus',
 'Medial plantar artery',
 'Medial rectus muscle',
 'Median antebrachial vein',
 'Median cubital vein',
 'Medication Management',
 'Meningeorrhaphy',
 'Meniscectomy, knee',
 'Mental foramen',
 'Metacarpal ligament',
 'Metacarpophalangeal ligament',
 'Metal on metal bearing surface',
 'Metatarsal ligament',
 'Metatarsectomy',
 'Metatarsophalangeal (MTP) joint',
 'Metatarsophalangeal ligament',
 'Midcarpal joint',
 'Middle genicular artery',
 'Middle hemorrhoidal vein',
 'Middle rectal artery',
 'Middle temporal artery',
 'Mobilization, adhesions',
 'Monitoring',
 'MR Angiography',
 'Musculopexy',
 'Musculophrenic artery',
 'Musculoplasty',
 'Myectomy',
 'Myelogram',
 'Myopexy',
 'Myoplasty',
 'Myotomy',
 'Myringectomy',
 'Myringoplasty',
 'Nail bed',
 'Nail plate',
 'Nasolacrimal duct',
 'Navicular bone',
 'Neck of femur',
 'Neck of humerus (anatomical)(surgical)',
 'Nephrectomy',
 'Nephropexy',
 'Nephroplasty',
 'Nephropyeloureterostomy',
 'Nephrostomy',
 'Nephrotomography',
 'Nephrotomy',
 'Nerve conduction study',
 'Neurectomy',
 'Neurexeresis',
 'Neurolysis',
 'Neuroplasty',
 'Neurorrhaphy',
 'Neurostimulator Generator',
 'Neurostimulator generator, multiple channel',
 'Neurostimulator generator, multiple channel rechargeable',
 'Neurostimulator generator, single channel',
 'Neurostimulator generator, single channel rechargeable',
 'Neurostimulator Lead',
 'Neurotomy',
 'Neurotripsy',
 'Neutralization plate',
 'New Technology',
 'Nonimaging Nuclear Medicine Probe',
 'Nonimaging Nuclear Medicine Uptake',
 'Nuclear medicine',
 'Nuclear scintigraphy',
 'Nutrition, concentrated substances',
 'Obliteration',
 'Obturator artery',
 'Obturator muscle',
 'Obturator vein',
 'Occipital artery',
 'Occipital lymph node',
 'Occlusion',
 'Odentectomy',
 'Olecranon bursa',
 'Olecranon process',
 'Omentectomy, omentumectomy',
 'Omentoplasty',
 'Onychectomy',
 'Onychoplasty',
 'Oophorectomy',
 'Oophoropexy',
 'Oophoroplasty',
 'Oophorotomy',
 'Opponensplasty',
 'Optic disc',
 'Optical coherence tomography, intravascular',
 'Optimizer(tm) III implantable pulse generator',
 'Orbicularis oculi muscle',
 'Orbital portion of ethmoid bone',
 'Orbital portion of frontal bone',
 'Orbital portion of lacrimal bone',
 'Orbital portion of maxilla',
 'Orbital portion of palatine bone',
 'Orbital portion of sphenoid bone',
 'Orbital portion of zygomatic bone',
 'Orchectomy, orchidectomy, orchiectomy',
 'Orchidoplasty, orchioplasty',
 'Orchiopexy',
 'Ossiculectomy',
 'Ostectomy',
 'Osteoclasis',
 'Osteolysis',
 'Osteopathic Treatment',
 'Osteopexy',
 'Osteoplasty',
 'Osteorrhaphy',
 'Osteotomy, ostotomy',
 'Other Imaging',
 'Otoplasty',
 'Oval window',
 'Ovariectomy',
 'Ovariopexy',
 'Ovariotomy',
 'Ovatio(tm) CRT-D',
 'Oversewing',
 'Oviduct',
 'Oxygenation',
 'Pacemaker',
 'Packing',
 'Paclitaxel-eluting peripheral stent',
 'Palatoplasty',
 'Palmar (volar) digital vein',
 'Palmar (volar) metacarpal vein',
 'Palmar cutaneous nerve',
 'Palmar fascia (aponeurosis)',
 'Palmar interosseous muscle',
 'Palmar ulnocarpal ligament',
 'Palmaris longus muscle',
 'Pancreatectomy',
 'Pancreatotomy',
 'Panniculectomy',
 'Paracentesis',
 'Parathyroidectomy',
 'Parotidectomy',
 'Pars flaccida',
 'Partial joint replacement',
 'Patellapexy',
 'Patellaplasty',
 'Patellar ligament',
 'Patellar tendon',
 'Patellectomy',
 'Patellofemoral joint',
 'Pectineus muscle',
 'Pectoral (anterior) lymph node',
 'Pectoralis major muscle',
 'Pectoralis minor muscle',
 'Pedicle-based dynamic stabilization device',
 'Pelvic splanchnic nerve',
 'Penectomy',
 'Performance',
 'Perfusion',
 'Perfusion, donor organ',
 'Pericardiectomy',
 'Pericardiophrenic artery',
 'Pericardioplasty',
 'Peripheral Intravascular Lithotripsy (Peripheral IVL)',
 'Peritoneocentesis',
 'Peritoneoplasty',
 'Peroneus brevis muscle',
 'Peroneus longus muscle',
 'Petrous part of temoporal bone',
 'Phacoemulsification, lens',
 'Phalangectomy',
 'Phallectomy',
 'Phalloplasty',
 'Pharmacotherapy, for substance abuse',
 'Pharyngoplasty',
 'Pharyngotympanic tube',
 'Pheresis',
 'Phlebectomy',
 'Phlebography',
 'Phleborrhaphy',
 'Phlebotomy',
 'Photocoagulation',
 'Phrenoplasty',
 'Pinealectomy',
 'Pinna',
 'Pipeline(tm) (Flex) embolization device',
 'Piriformis muscle',
 'Pisiform bone',
 'Pisohamate ligament',
 'Pisometacarpal ligament',
 'Pituitectomy',
 'Plain film radiology',
 'Plain Radiography',
 'Planar Nuclear Medicine Imaging',
 'Plantar digital vein',
 'Plantar fascia (aponeurosis)',
 'Plantar metatarsal vein',
 'Plantar venous arch',
 'Plaque Radiation',
 'Platysma muscle',
 'Pleurectomy',
 'Pleurodesis, pleurosclerosis',
 'Plica semilunaris',
 'Plication',
 'Pneumectomy',
 'Pneumonopexy',
 'Popliteal ligament',
 'Popliteal lymph node',
 'Popliteal vein',
 'Popliteus muscle',
 'Postauricular (mastoid) lymph node',
 'Posterior (subscapular) lymph node',
 'Posterior auricular artery',
 'Posterior auricular vein',
 'Posterior chamber',
 'Posterior circumflex humeral artery',
 'Posterior cruciate ligament (PCL)',
 'Posterior facial (retromandibular) vein',
 'Posterior spinal artery',
 'Posterior tibial recurrent artery',
 'Posterior ulnar recurrent artery',
 'PRECICE intramedullary limb lengthening system',
 'Prepatellar bursa',
 'Pretracheal fascia',
 'Prevertebral fascia',
 'PrimeAdvanced neurostimulator (SureScan)(MRI Safe)',
 'Princeps pollicis artery',
 'Probing, duct',
 'Proctectomy',
 'Proctocolectomy',
 'Proctocolpoplasty',
 'Proctoperineoplasty',
 'Proctopexy',
 'Proctoplasty',
 'Proctosigmoidectomy',
 'Profunda brachii',
 'Profunda femoris (deep femoral) vein',
 'Pronator quadratus muscle',
 'Pronator teres muscle',
 'Prostatectomy',
 'Proximal radioulnar joint',
 'Psoas muscle',
 'Psychological Tests',
 'Psychotherapy',
 'Pubis',
 'Pubofemoral ligament',
 'Pull-through, laparoscopic-assisted transanal',
 'Pulmonary plexus',
 'Pulverization',
 'Punch biopsy',
 'Puncture',
 'Pyelography',
 'Pyeloplasty',
 'Pyeloplasty, dismembered',
 'Pyelostomy',
 'Pylorectomy',
 'Pylorogastrectomy',
 'Pyloroplasty',
 'Pyramidalis muscle',
 'Quadratus femoris muscle',
 'Quadratus lumborum muscle',
 'Quadratus plantae muscle',
 'Quadriceps (femoris)',
 'Radial collateral carpal ligament',
 'Radial collateral ligament',
 'Radial notch',
 'Radial recurrent artery',
 'Radial vein',
 'Radialis indicis',
 'Radiation Therapy',
 'Radiation treatment',
 'Radiocarpal joint',
 'Radiocarpal ligament',
 'Radiography',
 'Radiology, analog',
 'Radiology, diagnostic',
 'Radioulnar ligament',
 'Reattachment',
 'Recession',
 'Reconstruction',
 'Rectectomy',
 'Rectopexy',
 'Rectoplasty',
 'Rectosigmoidectomy',
 'Rectus abdominis muscle',
 'Rectus femoris muscle',
 'Reduction',
 'Refusion',
 'Rehabilitation',
 'Reimplantation',
 'Reinforcement',
 'Relaxation, scar tissue',
 'Release',
 'Relocation',
 'Removal',
 'Removal of device from',
 'Renal calyx',
 'Renal capsule',
 'Renal cortex',
 'Renal segment',
 'Renal segmental artery',
 'Reopening, operative site',
 'Repair',
 'Replacement',
 'Replacement, hip',
 'Replantation',
 'Reposition',
 'Resection',
 'Restriction',
 'Resurfacing Device',
 'Resuscitation',
 'Retraining',
 'Retropharyngeal lymph node',
 'Revision',
 'Revision of device in',
 'Revo MRI(tm) SureScan(R) pacemaker',
 'Rhinoplasty',
 'Rhizotomy',
 'Rhomboid major muscle',
 'Rhomboid minor muscle',
 'Robotic Assisted Procedure',
 'Rotation of fetal head',
 'Round window',
 'Roux-en-Y operation',
 'Rupture',
 'Salpingectomy',
 'Salpingopexy',
 'Salpingoplasty',
 'Salpinx',
 'Sartorius muscle',
 'SAVAL below-the-knee (BTK) drug-eluting stent system',
 'Scalene muscle',
 'Scan',
 'Scaphoid bone',
 'Scapholunate ligament',
 'Scaphotrapezium ligament',
 'Scapulectomy',
 'Scapulopexy',
 'Sclerotherapy, mechanical',
 'Scrotectomy',
 'Scrotoplasty',
 'Semicircular canal',
 'Semimembranosus muscle',
 'Semitendinosus muscle',
 'Septectomy',
 'Septoplasty',
 'Sequestrectomy, bone',
 'Serratus anterior muscle',
 'Serratus posterior muscle',
 'Sheffield hybrid external fixator',
 'Sheffield ring external fixator',
 'Shockwave Intravascular Lithotripsy (Shockwave IVL)',
 'Shortening',
 'Shunt creation',
 'Sialoadenectomy',
 'Sialodochoplasty',
 'Sialoectomy',
 'Sigmoidectomy',
 'Sinogram',
 'Sinusectomy',
 'Sling',
 'Small saphenous vein',
 'Soleus muscle',
 'Spacer',
 'Spectroscopy',
 'Sphenoidectomy',
 'Sphincterotomy, anal',
 'Spinal Stabilization Device',
 'Spinous process',
 'Splenectomy',
 'Splenius cervicis muscle',
 'Splenopexy',
 'SPY PINPOINT fluorescence imaging system',
 'Stapedectomy',
 'Stapedioplasty',
 'Stapes',
 "Stensen's duct",
 'Stereotactic Radiosurgery',
 'Sternoclavicular ligament',
 'Sternocleidomastoid artery',
 'Sternocleidomastoid muscle',
 'Sternotomy',
 'Stimulation, cardiac',
 'Stimulator Generator',
 'Stimulator Lead',
 'Stoma',
 'Stomatoplasty',
 'Stripping',
 'Study',
 'Subacromial bursa',
 'Subclavicular (apical) lymph node',
 'Subclavius muscle',
 'Subcostal muscle',
 'Submandibular ganglion',
 'Submandibular gland',
 'Suboccipital venous plexus',
 'Subscapular (posterior) lymph node',
 'Subscapular aponeurosis',
 'Subscapular artery',
 'Subscapularis muscle',
 'Substance Abuse Treatment',
 'Subtalar (talocalcaneal) joint',
 'Subtalar ligament',
 'Superficial circumflex iliac vein',
 'Superficial epigastric artery',
 'Superficial epigastric vein',
 'Superficial Inferior Epigastric Artery Flap',
 'Superficial palmar arch',
 'Superficial palmar venous arch',
 'Superficial temporal artery',
 'Superior epigastric artery',
 'Superior genicular artery',
 'Superior gluteal artery',
 'Superior laryngeal artery',
 'Superior oblique muscle',
 'Superior rectus muscle',
 'Superior tarsal plate',
 'Superior thoracic artery',
 'Superior thyroid artery',
 'Superior ulnar collateral artery',
 'Supplement',
 "Supraclavicular (Virchow's) lymph node",
 'Suprahyoid muscle',
 'Supraorbital vein',
 'Suprarenal gland',
 'Supraspinatus fascia',
 'Supraspinatus muscle',
 'Supraspinous ligament',
 'Supratrochlear lymph node',
 'Sural artery',
 'Surpass Streamline(tm) Flow Diverter',
 'Suspension',
 'Sustained Release Drug-eluting Intraluminal Device',
 'Suture',
 'Suture Removal',
 'Synovectomy',
 'Takedown',
 'Talocalcaneal (subtalar) joint',
 'Talocalcaneal ligament',
 'Talocalcaneonavicular joint',
 'Talocalcaneonavicular ligament',
 'Talocrural joint',
 'Talofibular ligament',
 'Talus bone',
 'Tarsectomy',
 'Tarsometatarsal ligament',
 'Tattooing',
 'TBNA (transbronchial needle aspiration)',
 'Tendonectomy',
 'Tendonoplasty, tenoplasty',
 'Tendototomy',
 'Tenectomy, tenonectomy',
 'Tenontotomy',
 'Tenosynovectomy',
 'Tenotomy',
 'Tensor fasciae latae muscle',
 'Teres major muscle',
 'Teres minor muscle',
 'Termination of pregnancy',
 'Testectomy',
 'Testing',
 'Thenar muscle',
 'Therapeutic Massage',
 'Thoracoacromial artery',
 'Thoracoplasty',
 'Thrombectomy',
 'Thrombolysis, Ultrasound assisted',
 'Thymectomy',
 'Thymopexy',
 'Thyroarytenoid muscle',
 'Thyrocervical trunk',
 'Thyroidectomy',
 'Tibialis anterior muscle',
 'Tibialis posterior muscle',
 'Tibiofemoral joint',
 'Tibioperoneal trunk',
 'Tissue Expander',
 'Tissue expander (inflatable)(injectable)',
 'Titanium Sternal Fixation System (TSFS)',
 'Tomographic (Tomo) Nuclear Medicine Imaging',
 'Tomography, computerized',
 'Tonsillectomy',
 'Total Anomalous Pulmonary Venous Return (TAPVR) repair',
 'Trachectomy',
 'Trachelectomy',
 'Trachelopexy',
 'Tracheoplasty',
 'Traction',
 'Tragus',
 'TRAM (transverse rectus abdominis myocutaneous) flap reconstruction',
 'Transection',
 'Transfer',
 'Transfusion',
 'Transplant',
 'Transplantation',
 'Transposition',
 'Transverse acetabular ligament',
 'Transverse facial artery',
 'Transverse humeral ligament',
 'Transverse process',
 'Transverse Rectus Abdominis Myocutaneous Flap',
 'Transverse scapular ligament',
 'Transverse thoracis muscle',
 'Transversospinalis muscle',
 'Transversus abdominis muscle',
 'Trapezium bone',
 'Trapezius muscle',
 'Trapezoid bone',
 'Triceps brachii muscle',
 'Trimming, excisional',
 'Triquetral bone',
 'Trochanteric bursa',
 'Turbinectomy',
 'Turbinoplasty',
 'Turbinotomy',
 'TURP (transurethral resection of prostate)',
 'Tympanic cavity',
 'Tympanic part of temoporal bone',
 'Tympanoplasty',
 'Ulnar collateral carpal ligament',
 'Ulnar collateral ligament',
 'Ulnar notch',
 'Ulnar vein',
 'Ultrafiltration',
 'Ultrasonic osteogenic stimulator',
 'Ultrasonography',
 'Ultrasound bone healing system',
 'Ultrasound Therapy',
 'Umbilical artery',
 'Uniplanar external fixator',
 'Ureteral orifice',
 'Ureterectomy',
 'Ureteroneocystostomy',
 'Ureteropelvic junction (UPJ)',
 'Ureteropexy',
 'Ureteroplasty',
 'Ureterostomy',
 'Ureterovesical orifice',
 'Urethrectomy',
 'Urethropexy',
 'Urethroplasty',
 'Uterine Artery',
 'Uterine tube',
 'Uterine vein',
 'Uvulectomy',
 'Vaginal artery',
 'Vaginal vein',
 'Vaginectomy',
 'Vaginofixation',
 'Vaginoplasty',
 'Valvotomy, valvulotomy',
 'Valvuloplasty',
 'Vascular Access Device',
 'Vasography',
 'Vasotomy',
 'Vastus intermedius muscle',
 'Vastus lateralis muscle',
 'Vastus medialis muscle',
 'Venectomy',
 'Venography',
 'Venorrhaphy',
 'Venotripsy',
 'Ventriculogram, cardiac',
 'Ventriculostomy',
 'Vermilion border',
 'Versa',
 'Version, obstetric',
 'Vertebral arch',
 'Vertebral body',
 'Vertebral foramen',
 'Vertebral lamina',
 'Vertebral pedicle',
 'Vesical vein',
 'Vesiculectomy',
 "Virchow's (supraclavicular) lymph node",
 'Virtuoso (II) (DR) (VR)',
 'Vitrectomy',
 'Vitreous body',
 'Viva (XT)(S)',
 'Vocal fold',
 'Vocational',
 'Volar (palmar) digital vein',
 'Volar (palmar) metacarpal vein',
 'Vulvectomy',
 'Washing',
 'WavelinQ EndoAVF system',
 'Window',
 'X-ray',
 'X-STOP(R) Spacer',
 'Zenith(R) Fenestrated AAA Endovascular Graft',
 'Zilver(R) PTX(R) (paclitaxel) Drug-Eluting Peripheral Stent',
 'Zonule of Zinn',
 'Zygomatic process of temporal bone']


letters = (letter for letter in index["ICD10PCS.index"]["letter"])
mainterms = [mainterms for letter in letters for mainterms in letter["mainTerm"]]
untested_terms = [term for term in mainterms if term['title'] in terms_not_tested]

successful_tests = []
unsuccessful_tests = []
terms_not_tested = []
other_problem_tests = []


def run_test(mainterm):
    try:
        if mainterm["term"]:
            pass
    except KeyError:
        other_problem_tests.append(mainterm)
        return None
    # When you have one level of subterms in a mainterm
    for subterm in mainterm['term']:
        # Reset test flag
        global test_flag
        test_flag = None

        # Execute subterm
        parser = Parser()
        parser.execute_tree(subterm)

        # Successful test
        if test_flag:
            success = True
        # Unsuccessful test
        elif not test_flag:
            # If one subterm fails, immediataly add to unsuccessful test list
            unsuccessful_tests.append(mainterm)
            # Flag used to ensure all terms are executed successfully
            success = False
            break
        # 'No Test' term
        elif test_flag == "No Test":
            # If one subterm is a "No Test", immediately add to no test list
            terms_not_tested.append(mainterm)
            # Flag used to ensure all terms are executed successfully
            success = False
            break
        # Unknown error
        else:
            # If one subterm fails, immediataly add to unsuccessful test list
            unsuccessful_tests.append(mainterm)
            # Flag used to ensure all terms are executed successfully
            success = False
            break
    # If all terms were successful, add to successful list
    # If one term is failed, break the for loop and count mainterm as not successful
    if success:
        successful_tests.append(mainterm)

count = 0
for term in untested_terms:
    run_test(term)
    count += 1
    print(count)

print(f"Number of terms NOT tested: {len(terms_not_tested)}")
print(f"Number of terms tested successfully: {len(successful_tests)}")
print(f"Number of unsuccessful tests: {len(unsuccessful_tests)}")
print(f"Number of unsuccessful tests with problems unknown: {len(other_problem_tests)}")