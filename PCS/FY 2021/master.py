# master_test.py
# Logan Bonsignore - 4/12/2021

# Description:
    # This script tests that all possible combinations of index terms can be executed successfully
    # Comment/uncomment testing & production code blocks to switch between test and production functionality

user_choice = input("Are you running a test? (y/n): ")
if user_choice.lower() == "y":
    testing = True
else:
    testing = False

import json
from pprint import pprint # Used for debugging

# Creating memory allocations to PSC Index, PCS Tables, PCS Definitions json files
with open("Data/JSON/PCS_Index.json") as index_file:
    index = json.load(index_file)
with open("Data/JSON/PCS_Tables.json") as table_file:
    tables = json.load(table_file)
with open("Data/JSON/PCS_Definitions.json") as definitions_file:
    defs = json.load(definitions_file)

# To test the script like it would run in production, comment out all 'testing blocks' and uncomment all code blocks that were commented out for test
# Code blocks next to a TESTING tag will need to be uncommented

# Script modifications made for testing:
    # All script modifications are under a '### TESTING ###' tag
        # Search the document for "TESTING" to see where testing modifications have been made
    # Modification specifics:
        # Master_Test() class
            # This class contains function and member variables used to conduct testing
            # It is not needed to run a production script, it is only used for testing
        # Testing block at all 'raise' statements
            # With the added testing blocks, the script will indicate a failed test if an error is raised for any mainterm during testing
        # Testing block added to all execute functions (functions that return information to the user) (search the document for 'Execute Function' in notes at top of function definition)
            # TESTING blocks are created to check for data the function is expecting, without returning it to the user
            # The testing block returns test_flag = True if expected data is present
            # The testing block returns test_flag = False if expected data is not present
        # Parser().execute_tree()
            # Functions from the Master_Test() class are used in place of single_level_parser.execute_single_level(mainterm) and self.progress_through_levels(mainterm)
            # single_level_parser.execute_single_level(mainterm) -> test_term_with_single_level_structure(mainterm)
            # self.progress_through_levels(mainterm) -> test_multi_level_structure(mainterm)
            # This insures all possible combinations of mainterms are tested without the need for user input
    # Known Errors:
        # Upon test completion there are mainterms that will show as failed but are actually successful when tested on production script (master_parse.py)
        # This is becuase the Master_Test().test_term_with_single_level_structure() function does not currently account for special mainterm structures passed to it
        # Ex: 'New Technology'. Fails all the {"title", "tab", "_level"} structures even though they are successful in production document
        # The test may return multiple errors for a single mainterm because each subterm in the mainterm throws the same error OR \
        # PCS_Index.json points to that mainterm more than once

### TESTING ###
# Class only used for testing
class Master_Test:
    def __init__(self):
        self.successful_tests = []
        self.unsuccessful_tests = []
        self.terms_not_tested = []

    def determine_object_structure(self, term_object) -> str:
        # Returns string value indicating which type of structure the mainterm has
        try:
            # If the mainterm object has a "term" key, this indicates the object has either
            # a single or multi level structure
            if term_object["term"]:
                subterm_list = term_object["term"]
                for subterm in subterm_list:
                    try:
                        # If any subterm object has a "term" key, this indicates the Mainterm object has
                        # a multi level structure
                        if subterm["term"]:
                            # Subterm contains levels, mainterm object has multi level structure
                            # Move onto next mainterm object to test
                            return "multi_level_structure"
                    # If none of the subterms have a "term" key,
                    # this indicates the mainterm has a sigle level structure
                    except KeyError:
                        # If subterm does not contain a "term" key, it has a sigle level structure
                        # Mark single_level_structure as True
                        single_level_structure = True
        except KeyError:
            # If the mainterm object does not have a "term" key, it has a no level structure
            return "no_level_structure"
        # If single_level_structure is True and the code did not return "multi level structure"
        if single_level_structure:
            # Indicate single_level_structure
            return "single_level_structure"

    def test_term_with_no_levels(self, mainterm):
        # Execute with mainterm to find test result
        parser.execute_tree(mainterm)
        # If sucessful test
        if test_flag == True:
            self.successful_tests.append(mainterm)
        # If unsucessful test
        elif test_flag == False:
            # Add subterm to list of unsuccessful tests
            self.unsuccessful_tests.append(mainterm)
        # If not tested
        elif test_flag == "No Test":
            self.terms_not_tested.append(mainterm)
        else:
            raise ValueError("Unknown test flag returned.")

    def test_term_with_single_level_structure(self, mainterm):
        # This function tests individual subterms in a mainterm object
        # It is only set up to test a single level at a time
        # Change the class definitions to account for which is a passing and which is a failing test
        # Will need to change if statements to account for what you want in this test'

        global test_flag
        test_flag = None # Ensures test_flag is modified used in check_for_varying_subterm_structures()

        # Checking to see if any subterm structure's in a single level mainterm have a varying structure that we do not account for in our code
        # Will throw error if found structure not ready for
        first_subterm = mainterm["term"][0]
        error = Parser().check_for_varying_subterm_structures(mainterm, first_subterm.keys())
        # If error is "error", there was an error in check_for_varying_subterm_structures(). Need debug.
        if error == "Error":
            self.unsuccessful_tests.append(mainterm)
            return

        for subterm in mainterm['term']:
            # Reset test flag for each subterm
            test_flag = False
            # Execute subterm to find test outcome
            # The class definitions have been modified to create a global variable that indicates the test outcome
            parser = Parser()
            parser.execute_tree(subterm)
            # Reading global variable test_flag to determine test outcome
            # Successful test
            if test_flag == True:
                success = True
            # Unsuccessful test
            elif test_flag == False:
                # If one subterm fails, add a tuple of mainterm object and failing subterm object to the unsuccessful_tests list
                self.unsuccessful_tests.append(mainterm)
                # Flag used to ensure all terms are executed successfully
                success = False
                # Move onto next subterm
                continue
            # 'No Test' term
            elif test_flag == "No Test":
                # If one subterm is a "No Test", add mainterm object to terms_not_tested list
                self.terms_not_tested.append(mainterm)
                # Flag used to ensure all terms are executed successfully
                success = False
                # Move on to next mainterm, one or more subterms contain a multi level structure
                return
            else:
                pprint(f"Mainterm: \n{mainterm}")
                pprint(f"Subterm: \n{subterm}")
                raise ValueError("Unknown test flag returned")
        # If all terms were successful, add to successful list
        # If one term is failed, break the for loop and count mainterm as not successful
        if success:
            self.successful_tests.append(mainterm)

    def test_multi_level_structure(self, mainterm):
        for level_1 in mainterm["term"]:
            # Check structure of mainterm object
            structure = self.determine_object_structure(level_1)
            # If not multi level structure, execute
            if structure == "single_level_structure" or structure == "no_level_structure":
                self.handle_no_level_or_single_level_structure(structure, level_1)
            # If multi level structure, execute
            elif structure == "multi_level_structure":
                # Iterate through subterm's next level
                for level_2 in level_1["term"]:
                    # Find the structure
                    structure = self.determine_object_structure(level_2)
                    # If find the end, execute test
                    if structure == "single_level_structure" or structure == "no_level_structure":
                        self.handle_no_level_or_single_level_structure(structure, level_2)
                    else:
                        for level_3 in level_2["term"]:
                            # Find the structure
                            structure = self.determine_object_structure(level_3)
                            # If find the end, execute test
                            if structure == "single_level_structure" or structure == "no_level_structure":
                                self.handle_no_level_or_single_level_structure(structure, level_3)
                            else:
                                for level_4 in level_3["term"]:
                                    # Find the structure
                                    structure = self.determine_object_structure(level_4)
                                    # If find the end, execute test
                                    if structure == "single_level_structure" or structure == "no_level_structure":
                                        self.handle_no_level_or_single_level_structure(structure, level_4)
                                    else:
                                        for level_5 in level_4["term"]:
                                            # Find the structure
                                            structure = self.determine_object_structure(level_5)
                                            # If find the end, execute test
                                            if structure == "single_level_structure" or structure == "no_level_structure":
                                                self.handle_no_level_or_single_level_structure(structure, level_1)
                                            else:
                                                raise LookupError("Found a level 6 term. Add another iteration for the next level to test function.")
            else:
                raise LookupError(f"Returned structure, '{structure}', is not recognized.")

    def handle_no_level_or_single_level_structure(self, structure, subterm):
        if structure == "no_level_structure":
            mainterm_parser.parent_execute(subterm)
        elif structure == "single_level_structure":
            self.test_term_with_single_level_structure(subterm)
        else:
            raise ValueError("Bad structure value, '{structure}', passed to this function.")

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

            ### TESTING ###
            if testing:
                master_test.test_term_with_single_level_structure(mainterm)
                return

            # Used to execute mainterms that have multiple subterms "_level" key equal to "1" 
            # Does not include mainterms with subterms that have "_level" equal to "2" or greater
            single_level_parser.execute_single_level(mainterm)
        elif not levels:
            print("--------PARENT EXECUTE--------")
            # Used to execute mainterms that do not have levels
            mainterm_parser.parent_execute(mainterm)
        else:
            print("--------PROGRESS THROUGH LEVELS--------")

            ### TESTING ###
            if testing:
                master_test.test_multi_level_structure(mainterm)
                return

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
        # This function executes queries using sub-function Mainterm_Parser().parent_execute()
        level_flag = True
        while level_flag:
            # Returns all "title" values from the next level of subterms
            new_level_terms = self.get_next_level_title_values(mainterm)
            if new_level_terms == None:
                # If no next level choices, execute with final subterm
                mainterm_parser.parent_execute(mainterm)
                level_flag = False
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
                    user_input = self.handle_bad_user_query(user_input, new_level_terms)
                # Find new mainterm object based on user choice above
                mainterm = self.find_matching_mainterm_to_user_input(mainterm, user_input)
                # Check for levels on new mainterm
                levels = self.check_for_levels_in_mainterm(mainterm)
                if not levels:
                    # If no more levels, execute with final mainterm
                    # If more levels, start another while loop iteration
                    level_flag = False
                    mainterm_parser.parent_execute(mainterm)
    
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
                        # If no 'title' or 'see' match, raise error
                        raise LookupError("Could not find user's term in next_level_choices. Checked for a 'see', 'title', and 'code' tag. -> progress_through_levels()")
    
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
            LookupError
        """
        accounted_for_structures = [
            {'title', 'codes', '_level'}, # Accounted for in execute_single_level_5
            {'title', 'code', '_level'}, # Accounted for in execute_single_level_5
            {"code", "_level"}, # Accounted for in execute_single_level_4()
            {"title", "code", "_level"}, # Accounted for in execute_single_level_4()
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

                            ### TESTING ###
                            if testing:
                                # Used in Master_Test.test_single_level_structure() to indicate a varying subterm structure
                                return "Error"

                            pprint(mainterm)
                            raise LookupError("One subterm in the mainterm contains a key that is different from the other subterm keys and it is not accounted for.")

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
                            raise LookupError("Could not find term to use as 'title' of subterm. -> get_render_ask_next_level_terms()")

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

        ### TESTING ###
        if testing:
            global test_flag

        # This function points to a sub-function built to handle incoming mainterm structures
        # It returns LookupError if presented a mainterm structure it cannot handle
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

                ### TESTING ###
                if testing:
                    # Indicate failed test
                    test_flag = False
                    return
                
                raise LookupError("Code not prepared for mainterm's keys -> execute_single_level()")


        else:

            ### TESTING ###
            if testing:
                # Indicate failed test
                test_flag = False
                return

            raise LookupError("Code not prepared mainterm's keys -> execute_single_level()") 
            
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

            ### TESTING ###
            if testing:
                global test_flag
                # Indicate failed test
                test_flag = False
                return

            raise LookupError("Code not prepared for mainterm key structure -> execute_single_level_1")

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
                raise LookupError("Code not prepared for mainterm key structure -> execute_single_level_1_1()")

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
                # If we didnt find a valid response, raise LookupError
                if not self.term_found_flag:
                    raise LookupError("Code not prepared for mainterm key structure -> execute_single_level_3")
            else:
                raise LookupError("Code not prepared for mainterm key structure -> execute_single_level_3")
        
    def execute_single_level_4(self, mainterm):
        print("--------execute_single_level_4--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            Information to user in form of print(). Will integrate with PCS Table.
        """

        ### TESTING ###
        if testing:
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
                return
            except:
                master_test.hello = True
                # Indicates failed test
                test_flag = False
                return

        # Execute function
        # This function is called in execute_single_level()
        # This function handles mainterm objects with subterms that contain a "code" key
        # Not using a "title" tag if present in subterm. Add that in if needed.
            # Example: 'Telemetry'
        # Get number of final code's available 
        len_choices = len(mainterm["term"])
        # Get list of available codes
        choices = [term["code"] for term in mainterm["term"]]
        # Return codes to user
        print(f"""
You have {len_choices} choices for final codes related to term '{mainterm['title']}'. Choose the code that works best for this medical case. No further guidance given.""")
        print(choices)
        # Check to see if given a 'qualifier' or 'device'
        # Always found in 'see' key
        if self.pcs_component:
            print(f"Use {self.pcs_component[0]} '{self.pcs_component[1]}' in the PCS table.")
            # Resetting pcs_component flag
            self.pcs_component = False

    def execute_single_level_5(self, mainterm):
        print("--------execute_single_level_5--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            None.
        """
        # Execute function
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
                        raise LookupError("Unknown subterm structure found. Need function to handle -> execute_single_level_5()")

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

        ### TESTING ###
        if testing:
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
                return
            except:
                test_flag = False
                return

        # Execute function
        # This function handles mainterms with 'code' and 'codes' keys on the same level of subterms
        # Ex: 'Abortion'
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
        if len(final_codes) > 0:
            print(f"""
Choices for Final codes: {final_codes}""")
        if len(partial_codes) > 0:
            print(f"Choices for un-finished codes: {partial_codes}")
        # If nothing is found, raise LookupError
        if len(partial_codes) == 0 and len(final_codes) == 0:
            raise LookupError("Not prepared for mainterm structure -> execute_single_level_5()")
        # Check to see if given a 'qualifier' or 'device'
        # Always found in 'see' key
        if self.pcs_component:
            print(f"Use {self.pcs_component[0]} '{self.pcs_component[1]}' in the PCS table.")
            # Resetting pcs_component flag
            self.pcs_component = False

class Mainterm_Parser(Parser):
    def parent_execute(self, mainterm):
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            None
        """

        ### TESTING ###
        if testing:
            global test_flag

        # This function is called when there are no levels in the Mainterm object in focus
        # Depending on the mainterm's key structure, an execute function built to handle given structure is called
        if {"title", "use"} == mainterm.keys():
            self.execute_group_1(mainterm)
        elif {'code', '_level'} == mainterm.keys():
            self.execute_group_4(mainterm)
        elif {"use", "_level"} == mainterm.keys():
            self.execute_group_1(mainterm)
        elif {"title", "see"} == mainterm.keys():
            self.execute_group_2(mainterm)
        elif {"see", "_level"} == mainterm.keys():
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
        elif {"title", "see", "_level"} == mainterm.keys():
            self.execute_group_2(mainterm)
        elif {"title", "codes", "_level"} == mainterm.keys():
            self.execute_group_6(mainterm)
        elif {'title', 'tab', '_level'} == mainterm.keys():
            self.execute_group_5(mainterm)
        elif {"_level"} == mainterm.keys():

            ### TESTING ###
            if testing:
                #Indicate failed test
                test_flag = False
                return

            pprint(mainterm)
            raise LookupError("Code not prepared for mainterm key structure -> parent_execute()")

        else:

            ### TESTING ###
            if testing:
                #Indicate failed test
                test_flag = False
                return

            pprint(mainterm)
            raise LookupError("Code not prepared for mainterm key structure -> parent_execute()")
    
    def execute_group_1(self, mainterm):
        print("--------execute_group_1--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            None.
        """
        # This function is called in parent_execute() and parent_execute()
        # This function points to sub-functions that handle mainterm objects containing a "use" key
        # If "use" key returns a string then it has no children, execute function built to handle.
        if isinstance(mainterm["use"], str):
            self.execute_group_1_1(mainterm)
        # If the "use" key has children, execute based on children's key structure
        elif {"tab", "__text"} == mainterm["use"].keys():
            self.execute_group_1_2(mainterm)
        else:

            ### TESTING ###
            if testing:
                #Indicate failed test
                global test_flag
                test_flag = False
                return

            pprint(mainterm)
            raise LookupError("Code not prepared for mainterm key structure -> execute_group_1()")
    
    def execute_group_1_1(self, mainterm):
        print("--------execute_group_1_1--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            Information to user in form of print(). Will integrate with PCS Table.
        """

        ### TESTING ###
        if testing:
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
                return
            except:
                # Indicate failed test
                test_flag = False
                return

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
        print(f"""
Use the code associated with term '{mainterm['use']}' in the PCS Table.""")
        # Check to see if given a 'qualifier' or 'device'
        # Always found in 'see' key
        if self.pcs_component:
            print(f"Use {self.pcs_component[0]} '{self.pcs_component[1]}' in the PCS table.")
            # Resetting pcs_component flag
            self.pcs_component = False

    def execute_group_1_2(self, mainterm):
        print("--------execute_group_1_2--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            Information to user in form of print(). Will integrate with PCS Table.
        """

        ### TESTING ###
        if testing:
            global test_flag
            try:
                table = mainterm["use"]["tab"]
                text = mainterm["use"]["__text"]
                if self.pcs_component:
                    comp_1 = self.pcs_component[0]
                    comp_2 = self.pcs_component[1]
                    # Resetting pcs_component flag
                    self.pcs_component = False
                    # Indicate successful test
                test_flag = True
                return
            except KeyError:
                # Indicate failed test
                test_flag = False
                return

        # Execute Function
        # This function is called in execute_group_1()
        # This function is used to handle mainterm objects that contain a "use" key that has no children
        # This function returns the PCS Table which the user needs to use
        # It also returns text that may correspond to a pos. 4-7 code in a PCS Row inside that PCS Table
        table = mainterm["use"]["tab"]
        text = mainterm["use"]["__text"]
        print(f"""
Go to table {table}, use PCS Row containing text '{text}' in pos. 4-7 values.""")
        # Check to see if given a 'qualifier' or 'device'
        # Always found in 'see' key
        if self.pcs_component:
            print(f"Use {self.pcs_component[0]} '{self.pcs_component[1]}' in the PCS table.")
            # Resetting pcs_component flag
            self.pcs_component = False

    def execute_group_2(self, mainterm):
        print("--------execute_group_2--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            None.
        """
        # This function is called in parent_execute() and parent_execute()
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

            ### TESTING ###
            if testing:
                global test_flag
                #Indicate failed test
                test_flag = False
                return

            pprint(mainterm)
            raise LookupError("Code not prepared for mainterm key structure -> parent_execute()")

    def execute_group_2_1(self, mainterm):
        print("--------execute_group_2_1--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            None.
        """

        ### TESTING ###
        if testing:
            global test_flag

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

                ### TESTING ###
                if testing:
                    # Used to avoid raising error later
                    self.term_found_flag = True
                    # Indicate failed test
                    test_flag = False
                    return

                self.term_found_flag = True
                print("NEED FUNCTION TO HANDLE. INTEGRATE TO PCS TABLE") 

        # If we still havent found a match
        if not self.term_found_flag:
            # Look for words signifying a certain structure (Ex: Core needle biopsy, Punch biopsy)
            if "with qualifier" in new_term or "with device" in new_term:
                self.term_found_flag = True
                self.handle_pcs_table_component(new_term)
        # If still now match, throw LookupError
        if not self.term_found_flag:

            ### TESTING ###
            if testing:
                #Indicate failed test
                test_flag = False
                return

            pprint(mainterm)
            raise LookupError("Code not prepared for mainterm key structure -> execute_group_2_1()")

    def custom_search(self, new_term):
        print("--------custom_search--------")
        """
        Args
            new_term -> "see" value that contains 3 separate search terms in one string.
        Returns
            None.
        """

        ### TESTING ###
        if testing:
            global test_flag

        # This function is called in execute_group_2_1()
        # These are custom searches that are hard coded because of there unique "see" value structure 
        # 'Ligation, hemorrhoid'
        if new_term == "Occlusion, Lower Veins, Hemorrhoidal Plexus":

            ### TESTING ###
            if testing:
                test_flag = True
                return

            # Create new 'mainterms' generator object
            mainterms = self.create_new_mainterm_generator(index)
            # Find first search terms object with 'title' value of "Occlusion"
            for new_mainterm_2 in mainterms:
                if new_mainterm_2["title"] == "Occlusion":
                    # Find second search terms object with 'title' value of "Vein"
                    for new_mainterm_3 in new_mainterm_2["term"]:
                        if new_mainterm_3["title"] == "Vein":
                            # Find third search term's object with 'title' value of "Lower"
                            for new_mainterm_4 in new_mainterm_3["term"]:
                                if new_mainterm_4["title"] == "Lower":
                                    code = new_mainterm_4["codes"]
                                    # Used in execute function to notify that Index gave us a PCS Table component
                                    self.pcs_component = ("qualifier", "Hemorrhoidal Plexus")
                                    self.execute_group_6(new_mainterm_4)
        # 'Myocardial Bridge Release'
        elif new_term == "Release, Artery, Coronary":

            ### TESTING ###
            if testing:
                test_flag = True
                return

            # Create new 'mainterms' generator object
            mainterms = self.create_new_mainterm_generator(index)
            for new_mainterm_2 in mainterms:
                # Search for 'mainterm' object with 'title' value of "Release"
                if new_mainterm_2["title"] == "Release":
                    for new_mainterm_3 in new_mainterm_2["term"]:
                        # Search for subterm object with 'title' value of "Artery"
                        if new_mainterm_3["title"] == "Artery":
                            for new_mainterm_4 in new_mainterm_3["term"]:
                                # Search for subterm object with 'title' value of "Coronary"
                                if new_mainterm_4["title"] == "Coronary":
                                    self.execute_tree(new_mainterm_4)
        # Psychotherapy -> Individual -> Mental Health Services
        elif new_term == "Psychotherapy, Individual, Mental Health Services":

            ### TESTING ###
            if testing:
                test_flag = True
                return

            # Create new 'mainterms' generator object
            mainterms = self.create_new_mainterm_generator(index)
            for new_mainterm_2 in mainterms:
                # Search for 'mainterm' object with 'title' value of "Release"
                if new_mainterm_2["title"] == "Psychotherapy":
                    for new_mainterm_3 in new_mainterm_2["term"]:
                        # Search for subterm object with 'title' value of "Artery"
                        if new_mainterm_3["title"] == "Individual":
                            for new_mainterm_4 in new_mainterm_3["term"]:
                                # Search for subterm object with 'title' value of "Coronary"
                                try:
                                    if new_mainterm_4["title"] == "Mental Health Services":
                                        self.execute_tree(new_mainterm_4, single_level_check=True)
                                except KeyError:
                                    if new_mainterm_4["see"] == "Mental Health Services":
                                        self.execute_tree(new_mainterm_4, single_level_check=True)
        else:

            ### TESTING ###
            if testing:
                test_flag = False
                return

            raise LookupError(f"Do not have a function build to handle lookup term '{new_term}' -> custom_search()")

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

            ### TESTING ###
            if testing:
                global test_flag
                #Indicate failed test
                test_flag = False
                return

            raise LookupError("Code not prepared for mainterm key structure -> execute_group_2_1_1()")
    
    def execute_group_2_2(self, mainterm):
        print("--------execute_group_2_2--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            Information to user in form of print(). Will integrate with PCS Table.
        """

        ### TESTING ###
        if testing:
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
                return
            except:
                test_flag = False
                return

        # Execute Function
        # This function is called in execute_group_2()
        # This function handles mainterm objects with a "see" key that contains "codes" and "__text" keys
        code = mainterm["see"]["codes"]
        text = mainterm["see"]["__text"]
        print(f"""
Go to table '{code[:3]}', located at '{text}'.
Position 4 and greater code(s): '{code[3:]}'
Each code corresponds to it's respective position number.""")
        # Check to see if given a 'qualifier' or 'device'
        # Always found in 'see' key
        if self.pcs_component:
            print(f"Use {self.pcs_component[0]} '{self.pcs_component[1]}' in the PCS table.")
            # Resetting pcs_component flag
            self.pcs_component = False
        
    def execute_group_2_3(self, mainterm):
        print("--------execute_group_2_3--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            Information to user in form of print(). Will integrate with PCS Table.
        """

        ### TESTING ###
        if testing:
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
                return
            except:
                test_flag = False
                return

        # Execute Function
        # This function is called in execute_group_2()
        # This function handles mainterm objects with a "see" key that contains "tab" and "__text" keys
        table = mainterm["see"]["tab"]
        text = mainterm["see"]["__text"]
        print(f"""
Go to table '{table}', located at sections '{text}'.
The 'sections' may also correspond to a pos. 4-7 value in a PCS Row in the given PCS Table""")
        # Check to see if given a 'qualifier' or 'device'
        # Always found in 'see' key
        if self.pcs_component:
            print(f"Use {self.pcs_component[0]} '{self.pcs_component[1]}' in the PCS table.")
            # Resetting pcs_component flag
            self.pcs_component = False

    def execute_group_4(self, mainterm):
        print("--------execute_group_4--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            Information to user in form of print(). Will integrate with PCS Table.
        """

        ### TESTING ###
        if testing:
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
                return
            except:
                test_flag = False
                return

        # Execute Function
        # This function is called in Mainterm_Parser().parent_execute() and Mainterm_Parser().parent_execute()
        # This function handles a mainterm object with keys:
#             {"title", "code"}
#             {'code', '_level'}
#             {'title', 'code', '_level'}
        try:
            # If "mainterm" has a "title" key, display "title" in return
            print(f"""
Use final code: {mainterm['code']} with description '{mainterm['title']}'.""")
        except KeyError:
            # If no title key, only display "code"
            print(f"""
Use final code: {mainterm['code']}. No further information given.""")
        # Check to see if given a 'qualifier' or 'device'
        # Always found in 'see' key
        if self.pcs_component:
            print(f"Use {self.pcs_component[0]} '{self.pcs_component[1]}' in the PCS table.")
            # Resetting pcs_component flag
            self.pcs_component = False
        
    def execute_group_5(self, mainterm):
        print("--------execute_group_5--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            Information to user in form of print(). Will integrate with PCS Table.
        """

        ### TESTING ###
        if testing:
            global test_flag
            try:
                table = mainterm["tab"]
                title = mainterm["title"]
                if self.pcs_component:
                    comp_1 = self.pcs_component[0]
                    comp_2 = self.pcs_component[1]
                    # Resetting pcs_component flag
                    self.pcs_component = False
                test_flag = True
                return
            except:
                test_flag = False
                return

        # Execute Function
        # This function is called in Mainterm_Parser().parent_execute() and Mainterm_Parser().parent_execute()
        # This function handles a mainterm object with keys:
            # {"title", "tab"}
            # {'title', 'tab', '_level'}
        table = mainterm["tab"]
        print(f"""
Go to table: {table}. No additional guidance given.""")
        # Check to see if given a 'qualifier' or 'device'
        # Always found in 'see' key
        if self.pcs_component:
            print(f"Use {self.pcs_component[0]} '{self.pcs_component[1]}' in the PCS table.")
            # Resetting pcs_component flag
            self.pcs_component = False

    def execute_group_6(self, mainterm):
        print("--------execute_group_6--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            Information to user in form of print(). Will integrate with PCS Table.
        """

        ### TESTING ###
        if testing:
            global test_flag
            try:
                code = mainterm["codes"]
                if self.pcs_component:
                    comp_1 = self.pcs_component[0]
                    comp_2 = self.pcs_component[1]
                    # Resetting pcs_component flag
                    self.pcs_component = False
                test_flag = True
                return
            except:
                test_flag = False
                return

        # Execute Function
        # This function is called in Mainterm_Parser().parent_execute() and Mainterm_Parser().parent_execute()
        # This function handles a mainterm object with keys:
            # "title", "codes"}
            # {'title', 'codes', '_level'}
        code = mainterm["codes"]
        print(f"""
Go to table: {code[:3]}
Position 4 and greater code(s): '{code[3:]}'
Each code corresponds to it's respective position number.""")
        # Check to see if given a 'qualifier' or 'device'
        # Always found in 'see' key
        if self.pcs_component:
            print(f"Use {self.pcs_component[0]} '{self.pcs_component[1]}' in the PCS table.")
            # Resetting pcs_component flag
            self.pcs_component = False

    def execute_group_7(self, mainterm):
        print("--------execute_group_7--------")
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            Information to user in form of print(). Will integrate with PCS Table.
        """

        ### TESTING ###
        if testing:
            global test_flag
            try:
                code = mainterm["code"]
                codes_list = mainterm["term"]
                codes = [codes["code"] for codes in codes_list]
                test_flag = True
                return
            except:
                test_flag = False
                return

        # Execute Function
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
        # Check to see if given a 'qualifier' or 'device'
        # Always found in 'see' key
        if self.pcs_component:
            print(f"Use {self.pcs_component[0]} '{self.pcs_component[1]}' in the PCS table.")
            # Resetting pcs_component flag
            self.pcs_component = False

################################################ End Class Definitions #################################################
########################################################################################################################
if not testing:
    # Execute Production Code

    single_level_parser = Single_Level_Parser()
    mainterm_parser = Mainterm_Parser()

    user_flag = "y" # Flag used to determine if user wants to choose another term
    while user_flag == "y":
        # Create generator object of all 'letter' objects
        letters = (letter for letter in index["ICD10PCS.index"]["letter"])
        # Create generator object of all 'mainterm' objects
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


                                    ## TESTING ###
####################################################################################
####################################################################################
if testing:
    # Test All Mainterms

    master_test = Master_Test()
    single_level_parser = Single_Level_Parser()
    mainterm_parser = Mainterm_Parser()

    letters = (letter for letter in index["ICD10PCS.index"]["letter"])
    # Create generator object of all 'mainterm' objects
    mainterms = (mainterms for letter in letters for mainterms in letter["mainTerm"])
    # Search 'mainterms' for matching mainterm to user query
    for mainterm in mainterms:
        parser = Parser()
        # Find structure of mainterm
        structure = master_test.determine_object_structure(mainterm)
        # If the mainterm object has no levels
        if structure == "no_level_structure":
            master_test.test_term_with_no_levels(mainterm)
        # If mainterm object has a single level structure
        elif structure == "single_level_structure":
            # Test all subterms in that single level structure
            master_test.test_term_with_single_level_structure(mainterm)
            # Determine outcome of test in above function
        # If the mainterm object has a multi level structure
        elif structure == "multi_level_structure":
            # Test all subterms in that multi level structure
            master_test.test_multi_level_structure(mainterm)
        # If unknown structure, throw error
        else:
            print(structure)
            pprint(mainterm)
            raise ValueError("Unknown structure returned.")

    print(f"Number of successful tests: {len(master_test.successful_tests)}")
    print(f"Number of unsuccessful tests: {len(master_test.unsuccessful_tests)} (some unsuccessful tests are executed successfully in production code)")
    print(f"Number of terms not tested: {len(master_test.terms_not_tested)}")
    total_tests_completed = len(master_test.successful_tests) + len(master_test.unsuccessful_tests) + len(master_test.terms_not_tested)
    print(f"Total Tests Completed: {total_tests_completed}")
    print("---------Unsuccessful Tests---------")
    for term in master_test.unsuccessful_tests: pprint(term["title"])

#####################################################################################
#####################################################################################
# if testing:
    # Test Singular Mainterm

    # test_mainterm_title = "New Technology"

    # master_test = Master_Test()
    # single_level_parser = Single_Level_Parser()
    # mainterm_parser = Mainterm_Parser()

    # letters = (letter for letter in index["ICD10PCS.index"]["letter"])
    # # Create generator object of all 'mainterm' objects
    # mainterms = (mainterms for letter in letters for mainterms in letter["mainTerm"])
    # # Search 'mainterms' for matching mainterm to user query
    # for mainterm in mainterms:
    #     if mainterm["title"] == test_mainterm_title:
    #         parser = Parser()
    #         # Find structure of mainterm
    #         structure = master_test.determine_object_structure(mainterm)
    #         # If the mainterm object has no levels
    #         if structure == "no_level_structure":
    #             master_test.test_term_with_no_levels(mainterm)
    #         # If mainterm object has a single level structure
    #         elif structure == "single_level_structure":
    #             # Test all subterms in that single level structure
    #             master_test.test_term_with_single_level_structure(mainterm)
    #             # Determine outcome of test in above function
    #         # If the mainterm object has a multi level structure
    #         elif structure == "multi_level_structure":
    #             # Test all subterms in that multi level structure
    #             master_test.test_multi_level_structure(mainterm)
    #         # If unknown structure, throw error
    #         else:
    #             print(structure)
    #             pprint(mainterm)
    #             raise ValueError("Unknown structure returned.")

    # print(f"Number of successful tests: {len(master_test.successful_tests)}")
    # print(f"Number of unsuccessful_tests: {len(master_test.unsuccessful_tests)}")
    # print(f"Number of terms not tested: {len(master_test.terms_not_tested)}")
    # total_tests_completed = len(master_test.successful_tests) + len(master_test.unsuccessful_tests) + len(master_test.terms_not_tested)
    # print(f"Total Tests Completed: {total_tests_completed}")
    # print("---------Unsuccessful Tests---------")
    # for term in master_test.unsuccessful_tests: pprint(term["title"])

#####################################################################################
#####################################################################################
# Terms That Need Debug

# This list is returned as Master_Test().unsuccessful_tests 
# I've copied the list to here and renamed terms_to_debug
# This list is maintained manually by developers
# Test all combinations of each term manually on production script to ensure success or fail
# If mainterm is commented out it means the term has been manually tested successfully
# When manually testing a term, always search PCS_Index.json for the term and test all possible outcomes (can be multiple in separate mainterms)

terms_to_debug = [
    'Clipping, aneurysm', # Failed "see" lookup: 'Occlusion using Extraluminal Device', 'Restriction using Extraluminal Device'
    'Drotrecogin alfa, infusion', # Introduction...
    'Eptifibatide, infusion', # Introduction...
    ["Insertion", "Antimicrobial envelope"], # Introduction... ###### TRY IT
    'Immunization', # Introduction...
    'Immunotherapy', # Introduction...
    'Immunotherapy, antineoplastic', # Introduction... w/ subterms
    ['Induction of labor', 'Oxytocin'], # Introduction...
    ['Lengthening', "Bone, with device"], # Failed "see" lookup: 'Insertion of Limb Lengthening Device'
    ['Localization', "Imaging"], # Failed "see" lookup: 'Imaging'
    ['Nutrition, concentrated substances', 'Parenteral (peripheral) infusion'], # Introduction...
    'Parenteral nutrition, total', # Introduction...
    'Peripheral parenteral nutrition', # Introduction...
    'PPN (peripheral parenteral nutrition)', # Introduction... 
    'Radiation Therapy',
    'Radiation treatment',
    ['Replacement of existing device', 'Root operation to place new device, e.g., Insertion, Replacement, Supplement'], # Failed "see" lookup: 'Root operation to place new device, e.g., Insertion, Replacement, Supplement'
    'Sclerotherapy, via injection of sclerosing agent', # Introduction...
    'Telemetry', # Varying subterm structure needs to be accounted for
    'Total parenteral nutrition (TPN)', # Introduction...
    'Vaccination', # Introduction...
]

# print("---------Unsuccessful Tests After Manual Verification---------")
# pprint(terms_to_debug)
# print(f"\nNumber of term combinations to debug: {(len(terms_to_debug))}")

#####################################################################################
#####################################################################################

old_terms_to_debug = [
    # 'Angioscopy',
    # 'Antimicrobial envelope',
    # 'Cerebral Embolic Filtration',
    # 'Antimicrobial envelope',
    'Clipping, aneurysm', # Failed "see" lookup: 'Occlusion using Extraluminal Device', 'Restriction using Extraluminal Device'
    # 'Bowel, Small',
    # 'Gastrointestinal, Upper',
    # 'DownStream(R) System',
    'Drotrecogin alfa, infusion', # Introduction...
    # 'Orbital Atherectomy Technology'
    'Eptifibatide, infusion', # Introduction...
    ["Insertion", "Antimicrobial envelope"], # Introduction...
    'Immunization', # Introduction...
    'Immunotherapy', # Introduction...
    'Immunotherapy, antineoplastic', # Introduction... w/ subterms
    ['Induction of labor', 'Oxytocin'], # Introduction...
    ['Lengthening', "Bone, with device"], # Failed "see" lookup: 'Insertion of Limb Lengthening Device'
    ['Localization', "Imaging"], # Failed "see" lookup: 'Imaging'
    # 'Intraoperative Knee Replacement Sensor'         
    # 'Atezolizumab Antineoplastic'                       # Start 'New Technology' subterms
    # 'Bamlanivimab Monoclonal Antibody'
    # 'Baricitinib'
    # 'Bezlotoxumab Monoclonal Antibody'
    # 'Blinatumomab Antineoplastic Immunotherapy'
    # 'Brexanolone'
    # 'Brexucabtagene Autoleucel Immunotherapy'
    # 'Caplacizumab'
    # 'CD24Fc Immunomodulator'
    # 'Cefiderocol Anti-infective'
    # 'Ceftazidime-Avibactam Anti-infective'
    # 'Ceftolozane/Tazobactam Anti-infective'
    # 'Cerebral Embolic Filtration',
    # 'Coagulation Factor Xa, Inactivated',
    # 'COVID-19 Vaccine',
    # 'COVID-19 Vaccine Dose 1',
    # 'COVID-19 Vaccine Dose 2',
    # 'Cytarabine and Daunorubicin Liposome Antineoplastic',
    # 'Defibrotide Sodium Anticoagulant',
    # 'Durvalumab Antineoplastic',
    # 'Eculizumab',
    # 'Engineered Autologous Chimeric Antigen Receptor T-cell Immunotherapy',
    # 'Etesevimab Monoclonal Antibody',
    # 'Fosfomycin Anti-infective',
    # 'Idarucizumab, Dabigatran Reversal Agent',
    # 'Imipenem-cilastatin-relebactam Anti-infective',
    # 'Intraoperative Knee Replacement Sensor',
    # 'Iobenguane I-131 Antineoplastic',
    # 'Isavuconazole Anti-infective',
    # 'Lefamulin Anti-infective',
    # 'Lisocabtagene Maraleucel Immunotherapy',
    # 'Meropenem-vaborbactam Anti-infective',
    # 'Mineral-based Topical Hemostatic Agent',
    # 'Nerinitide',
    # 'Omadacycline Anti-infective',
    # 'Other New Technology Monoclonal Antibody',
    # 'Other New Technology Therapeutic Substance',
    # 'Plasma, Convalescent (Nonautologous)',
    # 'Plazomicin Anti-infective',
    # 'REGN-COV2 Monoclonal Antibody',
    # 'Remdesivir Anti-infective',
    # 'Sarilumab',
    # 'Synthetic Human Angiotensin II',
    # 'Tagraxofusp-erzs Antineoplastic',
    # 'Tocilizumab',                                   # End 'New Technology' subterms
    ['Nutrition, concentrated substances', 'Parenteral (peripheral) infusion'], # Introduction...
    # 'Occlusion, REBOA (resuscitative endovascular balloon occlusion of the aorta)',
    'Parenteral nutrition, total', # Introduction...
    'Peripheral parenteral nutrition', # Introduction...
    'PPN (peripheral parenteral nutrition)', # Introduction... 
    # 'Group',
    # 'Radiation Therapy',
    # 'Radiation treatment',
    # 'REBOA (resuscitative endovascular balloon occlusion of the aorta)',
    # 'Resuscitative endovascular balloon occlusion of the aorta (REBOA)',
    ['Replacement of existing device', 'Root operation to place new device, e.g., Insertion, Replacement, Supplement'], # Failed "see" lookup: 'Root operation to place new device, e.g., Insertion, Replacement, Supplement'
    'Sclerotherapy, via injection of sclerosing agent', # Introduction...
    # 'Stress test',
    # 'Supersaturated Oxygen therapy',
    'Telemetry', # Varying subterm structure needs to be accounted for
    'Total parenteral nutrition (TPN)', # Introduction...
    'Vaccination', # Introduction...
]