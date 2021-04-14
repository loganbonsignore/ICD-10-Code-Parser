# master_v2.py
# Master PCS_Index.json parser
# Version 2
# Logan Bonsignore - 4/12/2021

# Ask user if running test or if executing query
user_choice = input("Are you running a test? (y/n): ")
if user_choice.lower() == "y":
    testing = True
else:
    testing = False

# Begin query
import json
from pprint import pprint # Used for debugging

# Creating memory allocation to PSC Index json file
with open("Data/JSON/PCS_Index.json") as index_file:
    index = json.load(index_file)

#################################################### Testing Information ###########################################################
####################################################################################################################################

    # All code modifications made for testing are under a '### TESTING ###' tag

    # Master_Test() class
        # This class contains methods and member variables used to conduct testing
        # It is not used in the execution of queries, it is only used for testing
    # Execute functions (functions that return information to the user)
        # 'Testing blocks' are used to check for availability of data the method needs to execute properly. The 'testing block' does not return data to the user.
        # The 'testing block' creates a global variable test_flag = True if expected data is present OR a global variable test_flag = False if expected data is not present
    # Parser().execute_tree()
        # Methods from the Master_Test() class are used in place of single_level_parser.execute_single_level(mainterm) and progress_through_levels(mainterm)
            # execute_single_level(mainterm) -> test_term_with_single_level_structure(mainterm)
            # progress_through_levels(mainterm) -> test_multi_level_structure(mainterm)
        # This ensures all possible combinations of mainterms are tested without the need for user input

#################################################### Test Class Definitions #########################################################
#####################################################################################################################################

### TESTING ###
class Master_Test:
    def __init__(self):
        self.successful_tests = []
        self.unsuccessful_tests = []

    def determine_object_structure(self, term_object) -> str:
        # This method is used to determine structure types of mainterm objects
        # Returns string value indicating which type of structure the mainterm has
        single_level_structure = False
        try:
            # If the mainterm object has a "term" key, this indicates the object has either a single or multi level structure
            for subterm in term_object["term"]:
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
        else:
            raise LookupError("No object structure found. single_level_structure is False.")

    def test_term_with_no_levels(self, mainterm):
        # This method executes tests of mainterm objects that have a no level structure (no "term" key)
        # Execute mainterm that has no levels
        mainterm_parser.parent_execute(mainterm)
        # If sucessful test
        if test_flag == True:
            self.successful_tests.append(mainterm)
        # If unsucessful test
        elif test_flag == False:
            # Check for mainterm objects that are known successful when tested manually
            # Accounted for in get_next_level_title_values()
            # One subterm only contains a "_level" key, no data.
            if mainterm["title"] not in ["Radiation Therapy", "Radiation treatment"]:
                # Add subterm to list of unsuccessful tests
                self.unsuccessful_tests.append(mainterm)
        else:
            raise ValueError("Unknown test flag returned.")

    def test_term_with_single_level_structure(self, mainterm):
        # This method executes tests of individual subterms in a mainterm object with a single level structure
        global test_flag
        test_flag = None # Value of None ensures test_flag is modified in check_for_varying_subterm_structures()

        # Checking to see if any subterm structure's in a single level mainterm have a varying structure that we do not account for in our code
        self.check_for_varying_subterm_structures(mainterm)
        # Edit Master_Test.check_for_varying_subterm_structures() to decide if you want to add all mainterms with varying subterm structures to unsuccessful_tests list
        if test_flag == False:
            self.unsuccessful_tests.append(mainterm)

        # Run Parser class method to ensure successful on all terms
        parser_test = Parser()
        titles = parser_test.get_next_level_title_values(mainterm)
        self.find_matching_mainterm_to_user_input_test(mainterm)

        # If all Parser() functions pass
        # Test each subterm using execute_tree()
        for subterm in mainterm['term']:
            # Reset test flag for each subterm
            test_flag = False
            # Execute subterm to find test outcome
            # The class definitions have been modified to create a global variable that indicates the test outcome
            parser.execute_tree(subterm)
            # Reading global variable test_flag to determine test outcome
            # Successful test
            if test_flag == True:
                success = True
            # Unsuccessful test
            elif test_flag == False:
                # Check for mainterm objects that are known successful when tested manually
                # Accounted for in get_next_level_title_values()
                if mainterm["title"] in ["Radiation Therapy", "Radiation treatment"]:
                    continue
                # If one subterm fails, add a tuple of mainterm object and failing subterm object to the unsuccessful_tests list
                self.unsuccessful_tests.append((mainterm, subterm))
                # Flag used to ensure all terms are executed successfully
                success = False
            else:
                pprint(f"Mainterm: \n{mainterm}")
                pprint(f"Subterm: \n{subterm}")
                raise ValueError("Unknown test flag returned")

        # If all terms were successful, add to successful list
        # If one term is failed, break the for loop and count mainterm as not successful
        if success:
            self.successful_tests.append(mainterm)

    def test_multi_level_structure(self, mainterm):
        # This method tests all possible code combinations
        # It is built to handle up to level 5 terms
        # Add another for loop to account for a mainterm object containing 6 levels, etc.
        parser_test = Parser() # Used to test method in Parser class
        # Test Parser class method to ensure successful on all terms
        titles = parser_test.get_next_level_title_values(mainterm)
        self.find_matching_mainterm_to_user_input_test(mainterm)
        for level_1 in mainterm["term"]:
            # Check structure of mainterm object
            structure = self.determine_object_structure(level_1)
            # If not multi level structure, execute
            if structure == "single_level_structure" or structure == "no_level_structure":
                self.handle_no_level_or_single_level_structure(structure, level_1)
            # If multi level structure, execute
            elif structure == "multi_level_structure":
                # Test Parser class method to ensure successful on all terms
                titles = parser_test.get_next_level_title_values(mainterm)
                self.find_matching_mainterm_to_user_input_test(mainterm)
                # Iterate through subterm's next level
                for level_2 in level_1["term"]:
                    # Find the structure
                    structure = self.determine_object_structure(level_2)
                    # If find the end, execute test
                    if structure == "single_level_structure" or structure == "no_level_structure":
                        self.handle_no_level_or_single_level_structure(structure, level_2)
                    elif structure == "multi_level_structure":
                        # Test Parser class method to ensure successful on all terms
                        titles = parser_test.get_next_level_title_values(mainterm)
                        self.find_matching_mainterm_to_user_input_test(mainterm)
                        for level_3 in level_2["term"]:
                            # Find the structure
                            structure = self.determine_object_structure(level_3)
                            # If find the end, execute test
                            if structure == "single_level_structure" or structure == "no_level_structure":
                                self.handle_no_level_or_single_level_structure(structure, level_3)
                            elif structure == "multi_level_structure":
                                # Test Parser class method to ensure successful on all terms
                                titles = parser_test.get_next_level_title_values(mainterm)
                                self.find_matching_mainterm_to_user_input_test(mainterm)
                                for level_4 in level_3["term"]:
                                    # Find the structure
                                    structure = self.determine_object_structure(level_4)
                                    # If find the end, execute test
                                    if structure == "single_level_structure" or structure == "no_level_structure":
                                        self.handle_no_level_or_single_level_structure(structure, level_4)
                                    elif structure == "multi_level_structure":
                                        # Test Parser class method to ensure successful on all terms
                                        titles = parser_test.get_next_level_title_values(mainterm)
                                        self.find_matching_mainterm_to_user_input_test(mainterm)
                                        for level_5 in level_4["term"]:
                                            # Find the structure
                                            structure = self.determine_object_structure(level_5)
                                            # If find the end, execute test
                                            if structure == "single_level_structure" or structure == "no_level_structure":
                                                self.handle_no_level_or_single_level_structure(structure, level_1)
                                            elif structure == "multi_level_structure":
                                                raise LookupError("Found a level 6 term. Add another iteration for the next level to test method.")

    def handle_no_level_or_single_level_structure(self, structure, subterm):
        # This method is called in test_multi_level_structure()
        # This method points to other functions
        if structure == "no_level_structure":
            # Execute method built to handle no level structure
            mainterm_parser.parent_execute(subterm)
        elif structure == "single_level_structure":
            # Execute method built to handle no level structure
            self.test_term_with_single_level_structure(subterm)
        else:
            raise ValueError("Bad structure value, '{structure}', passed to this method.")
    
    def check_for_varying_subterm_structures(self, mainterm):
        """
        Args
            mainterm -> Mainterm object in focus.
            set_like_object -> set containing ordered dictionary keys which are being compared.
        Returns
            True
            LookupError
        """
        accounted_for_structures = [
            {'title', 'codes', '_level'},
            {'title', 'code', '_level'},
            {"code", "_level"},
            {"title", "code", "_level"},
        ]
        # This method is used to determine which mainterms have subterms with structures that vary from one antoher
        # Change the global variable test_flag value to count varying structures as unsuccessful
        # This method is called in Master_Test.test_term_with_single_level_structure()
        # It will raise LookupError if a mainterm structure is found that our code isn't prepared to handle
        # set_like_object is passed to the method and is a set of the first subterm's keys
        first_subterm_keys = mainterm["term"][0].keys()

        for term in mainterm["term"]:
            # Extracting keys of subterm
            term_keys = term.keys()
            # Iterating through subterm keys to check if structures vary
            for key in term_keys:
                # If the subterm's key is not in passed variable set_like_object
                # This means there is a subterm that contains a key that is different from the other subterm's keys
                if key not in first_subterm_keys:
                    # Iterate through subterms and check that keys are not in accounted_for_structures
                    for subterm in mainterm["term"]:
                        # If not in accounted_for_structures, raise LookupError
                        if subterm.keys() in accounted_for_structures:
                            pass
                        else:
                            global test_flag
                            # Use this if you DO want to add all mainterms with varying structures to the unsuccessful test list
                            # test_flag = False
                            # Use this if you DONT want to add all mainterms with varying structures to the unsuccessful test list
                            test_flag = None

    def find_matching_mainterm_to_user_input_test(self, mainterm):
        # This method is used in testing to ensure that a text value is found for each subterm in the next level when looking for a matching mainterm to user input
        # This method is the Master_Test class version of Parser.find_matching_mainterm_to_user_input()
        # This method will raise an error is it cannot find a text value in the subterm
        for term in mainterm["term"]:
            try:
                if term["title"]:
                    pass
            except KeyError:
                try:
                    if isinstance(term["see"], str):
                        pass
                    elif term["see"]["__text"]:
                        pass
                except KeyError:
                    try:
                        if isinstance(term["use"], str):
                            pass
                        elif term["use"]["__text"]:
                            pass
                    except KeyError:
                        try:
                            if term["code"]:
                                pass
                        except KeyError:
                            # If no option of text or anything else, pass
                            if {"_level"} == term.keys():
                                pass
                            # If there is an option for some sort of text, raise error
                            else:
                                pprint(mainterm)
                                raise LookupError("Couldn't find subterm key that contains text. Add new functionality in Parser.find_matching_mainterm_to_user_input().")

################################################# Query Class Definitions #####################################################
###############################################################################################################################

class Parser:
    def __init__(self):
        self.pcs_component = False # Flag to let output method know if need to account for PCS Table component.

    def execute_tree(self, mainterm):
        """
        Args:
            Mainterm -> Mainterm object in focus.
            single_level_check -> Bool value signaling to check for single level.
        Returns:
            None.
        """
        # This method acts as the 'go-to' execution funtion for this script
        # All "mainterm" objects are passed to this method
        # This method checks for levels, then executes functions built to handle the mainterm's structure
        levels = self.check_for_levels_in_mainterm(mainterm)
        # Check for levels to see which type of execute method is needed
        if levels == "level_1":
            print("--------EXECUTE SINGLE LEVEL--------")

            ### TESTING ###
            if testing:
                master_test.test_term_with_single_level_structure(mainterm)
                return

            # Used to execute mainterms that have multiple subterms "_level" key equal to "1" 
            # Does not include mainterms with subterms that have "_level" equal to "2" or greater
            self.execute_single_level(mainterm)
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
        # This method handles "mainterm" objects that contain more than 1 level
        # It iterates through levels until a final code or term is found
        # This method executes queries using sub-method Mainterm_Parser().parent_execute()
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

    def execute_single_level(self, mainterm):
        print("----------get_render_ask_execute_single_level_terms_no_varying_structures----------")
        # This method searches a mainterm with a single level structure for text choices for user to choose from
        # then, prints them out and asks user for input, then searches single level structure mainterm to find new mainterm object of focus based on user input
        # Then executes new mainterm through execute_tree()
        # Find text to use as user's choice for selected individual term in single level structure
        text_choices = self.get_next_level_title_values(mainterm)
        # Print choices to user
        print(text_choices)
        # Have user choose individual term
        user_input = input("Choose term that most correlates to this medical case: ")
        # Handle bad query if needed
        if user_input not in text_choices:
            self.handle_bad_user_query(user_input, text_choices)
        # Capture new mainterm of focus
        new_mainterm = self.find_matching_mainterm_to_user_input(mainterm, user_input)
        # Execute with new mainterm
        mainterm_parser.parent_execute(new_mainterm)

    def find_matching_mainterm_to_user_input(self, mainterm, user_input):
        # This method searches a mainterm object's subterm list to find a subterm that matches the user's input
        # Add functionality to check new keys by adding another try/except block with the key pattern you need
        # Flag used to indicate if term found
        term_found_flag = False
        for term in mainterm["term"]:
            try:
                # Look for match in "title" key
                if term["title"] == user_input:
                    new_mainterm = term
                    term_found_flag = True
                    break
            except (KeyError, TypeError):
                try:
                    # Look for match in "see" key
                    if term["see"] == user_input:
                        new_mainterm = term
                        term_found_flag = True
                        break
                    # Look for match in ["see"]["text"] key
                    elif term["see"]["__text"] == user_input:
                        new_mainterm = term
                        term_found_flag = True
                        break
                except (KeyError, TypeError):
                    try:
                        # Look for match in "use" key
                        if term["use"] == user_input:
                            new_mainterm = term
                            term_found_flag = True
                            break
                        # Look for match in ["use"]["text"] key
                        elif term["use"]["__text"] == user_input:
                            new_mainterm = term
                            term_found_flag = True
                            break
                    except (KeyError, TypeError):
                        try:
                            # Look for match in "code" key
                            if term["code"] == user_input:
                                new_mainterm = term
                                term_found_flag = True
                                break
                        except (KeyError, TypeError):
                            # Passing here because we need to check all subterms for match before raising error
                            pass

        # If term found, execute with new mainterm
        if term_found_flag:
            return new_mainterm
        # Raise error if term not found
        else:
            pprint(mainterm)
            pprint(term)
            raise LookupError("Could not find next level term that matches user input.")
    
    def get_next_level_title_values(self, mainterm):
        """
        Args
            mainterm -> Mainterm object in focus.
        Returns
            List of "title" values found on next level of mainterm.
            If no next level, returns None.
        """
        # This method returns the text value of each next level subterm in a mainterm["term"] list
        # If the "mainterm" does not have subterms, the method returns None
        text_choices = []
        try:
            for term in mainterm["term"]:
                try:
                    # Try to add the "title" value
                    text_choices.append(term["title"])
                except KeyError:
                    try:
                        # Try to add the "see" value if it's a string
                        if isinstance(term["see"], str):
                            text_choices.append(term["see"])
                        # Try to add the ["see"]["__text"] value if "see" value is a dictionary
                        elif term["see"]["__text"]:
                            text_choices.append(term["see"]["__text"])
                    except KeyError:
                        try:
                            # Try to add the "see" value if it's a string
                            if isinstance(term["use"], str):
                                text_choices.append(term["use"])
                            # Try to add the ["use"]["__text"] value if "use" value is a dictionary
                            elif term["use"]["__text"]:
                                text_choices.append(term["use"]["__text"])
                        except KeyError:
                            try:
                                # Try to add the "code" value if it's a string
                                # This will return to the user a 7 digit final code as a text value to choose which subterm they want to choose next
                                # In these situation there is no text available, only a code
                                code = term["code"]
                                text_choices.append(code)
                            except KeyError:
                                if {"_level"} == term.keys():
                                    # Pass here because mainterm contains a subterm object that doesnt contain any data other than a "_level" tag
                                    # Ex: 'Radiation Therapy' 
                                    pass
                                else:
                                    pprint(mainterm)
                                    pprint(term)
                                    raise LookupError("Could not find next level term's text to render as next level choice.")
        except KeyError:
            # If no next level terms, return None
            text_choices = None

        return text_choices
    
    def handle_bad_user_query(self, user_input, new_level_terms):
        """
        Args
            user_input -> User's choice on subterm to choose next.
            new_level_terms -> All possible choices for the user to make
        Returns:
            New user input that matches a usable term
        """
        # This method is called in progress_through_levels() and get_render_ask_next_level_terms()
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
        # This method checks for levels in the Mainterm object in focus.
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
        
    def create_new_mainterm_generator(self, index):
        """
        Args
            index -> JSON document representing the PCS Index.
        Return
            Generator object of all 'mainterm' objects
        """
        # This method is used to create a new generator object of all 'mainterm' objects
        # It is needed in situations where we are re-querying the mainterms and have already iterated through a generator object
        # If we dont create a new generator object, the next iteration on that object will start where the last iteration left off
        letters_new = (letter_new for letter_new in index["ICD10PCS.index"]["letter"])
        return (mainterms_new for letter in letters_new for mainterms_new in letter["mainTerm"])

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

        # This method is called when a mainterm has a no level structure (no "term" key)
        # Depending on the mainterm's key structure, an execute method built to handle given structure is called
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
        # This method is called in parent_execute()
        # This method points to sub-functions that handle mainterm objects containing a "use" key
        # If "use" key returns a string then it has no children, execute method built to handle.
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

        # Execute method
        # This method is called in execute_group_1()
        # This method is used to handle mainterm objects that contain a "use" key that has no children
        # This method returns a term that corresponds to a code in a PCS Table
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

        # Execute method
        # This method is called in execute_group_1()
        # This method is used to handle mainterm objects that contain a "use" key that has "tab" and "__text" keys
        # This method returns the PCS Table which the user needs to use
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
        # This method is called in parent_execute() 
        # This method points to sub-functions that handle mainterm objects containing a "see" key
        # If mainterm's "see" key returns a string then it has no children, execute method built to handle.
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

        # This method is called in execute_group_2()
        # This method handles mainterm objects with a "see" key that need to re-query the data to find another mainterm in the index
        new_term = mainterm["see"]
        print(f"--Redirected to term '{new_term}'.") # Logging
        # Create new generator object
        mainterms = self.create_new_mainterm_generator(index)
        # Ensure term_found_flag is False
        term_found_flag = False
        # Re-query mainterms to find new_mainterm object with matching "title" 
        # "title" value must match the original mainterm's "see" value
        for new_mainterm_1 in mainterms:
            # If mainterm object's 'title' value is equal to our new search term, execute
            # Using capitalized case search term for specific use cases (Ex: "Diagnostic Audiology","Diagnostic imaging","Diagnostic radiology","Radiology, diagnostic","Nuclear scintigraphy")
            if new_mainterm_1["title"] == new_term or new_mainterm_1["title"] == new_term.capitalize():
                print(f"--Found '{new_term}' on first attempt") # Logging
                term_found_flag = True
                self.execute_tree(new_mainterm_1)
                break   
        # If we did not find a match look for word patterns that indicate what's needed
        # See if structure of new_term is two separate terms separated by commas
        if not term_found_flag:
            # Split value returned from "see" key to re-query data for match
            # When a "see" value has multiple terms separated by ", " that means they have given us a subterm(s) (second, third term) to look for within the mainterm (first term)
            split_term = new_term.split(", ")
            if len(split_term) == 2:
                # If there are two terms, execute method that can handle
                term_found_flag = True
                self.execute_group_2_1_1(split_term)
            elif len(split_term) == 3:
                # If there are three terms, execute method that can handle
                term_found_flag = True
                self.custom_query(new_term)
        # If we have still not found a match look for introduction pattern
        if not term_found_flag:
            # Isolate first word from new_term
            first_word = new_term.split(" ")[0]
            # If first word is introduction... (Ex: 'Drotrecogin alfa, infusion', 'Eptifibatide, infusion')
            if first_word == "Introduction":

                ### TESTING ###
                if testing:
                    # Used to avoid raising error later
                    term_found_flag = True
                    # Indicate failed test
                    test_flag = False
                    return

                term_found_flag = True
                print("NEED method TO HANDLE. INTEGRATE TO PCS TABLE") 

        # If we still havent found a match look for wording patterns
        if not term_found_flag:
            # Look for words signifying a certain structure (Ex: Core needle biopsy, Punch biopsy)
            if "with qualifier" in new_term or "with device" in new_term:
                term_found_flag = True
                self.handle_pcs_table_component_1(new_term)
            elif "using" in new_term:
                term_found_flag = True
                self.handle_pcs_table_component_2(new_term)
        # If still no match, raise error
        if not term_found_flag:

            ### TESTING ###
            if testing:
                #Indicate failed test
                test_flag = False
                return

            pprint(mainterm)
            raise LookupError("Code not prepared for mainterm key structure -> execute_group_2_1()")

    def custom_query(self, new_term):
        print("--------custom_query--------")
        """
        Args
            new_term -> "see" value that contains 3 separate search terms in one string.
        Returns
            None.
        """
        # This method is called in execute_group_2_1()
        # These are custom querys that are hard coded because of there unique "see" value structure 
        # 'Ligation, hemorrhoid'
        if new_term == "Occlusion, Lower Veins, Hemorrhoidal Plexus":
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
                                    # Used in execute method to notify that Index gave us a PCS Table component
                                    self.pcs_component = ("qualifier", "Hemorrhoidal Plexus")
                                    self.execute_group_6(new_mainterm_4)
        # 'Myocardial Bridge Release'
        elif new_term == "Release, Artery, Coronary":
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
                                        self.execute_tree(new_mainterm_4)
                                except KeyError:
                                    if new_mainterm_4["see"] == "Mental Health Services":
                                        self.execute_tree(new_mainterm_4)
        else:

            ### TESTING ###
            if testing:
                global test_flag
                test_flag = False
                return

            raise LookupError(f"Do not have a method build to handle lookup term '{new_term}' -> custom_query()")

    def handle_pcs_table_component_1(self, new_term):
        print("--------handle_pcs_table_component_1--------")
        """
        Args
            new_term -> "see" value that contains a string representing a new search term and PCS Table component.
        Returns
            None.
        """
        # This method is called in execute_group_2_1()
        # This method parses a string containing information returned from a "see" tag
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
                self.execute_tree(mainterm_1)

    def handle_pcs_table_component_2(self, new_term):
        print("--------handle_pcs_table_component_2--------")
        # Ex: 'Clipping, aneurysm'
        # This method is called in execute_group_2_1()
        # This method parses a string containing information returned from a "see" tag
        # The string tells us what the new search term is, the PCS column header to be used (pos), and the PCS component to be used
        # Ex: 'Core needle biopsy', 'Punch biopsy'
        # Spliting text returned as value of "see" tag
        split_text = new_term.split(" ")
        # Finding new search term (always first word)
        new_search_term = split_text[0]
        # Finding pcs table column header to be used
        pcs_pos = split_text[-1]
        # Finding pcs term to be used under table's column header
        pcs_component = " ".join(split_text[2:-1])
        # Create new generator object
        mainterms = self.create_new_mainterm_generator(index)
        # Finding search term and executing
        for mainterm_1 in mainterms:
            if mainterm_1["title"] == new_search_term:
                # Flag to let output know if they gave us a pcs component
                # tuple will always have the 1st position be the pos word and second position be the component
                self.pcs_component = (pcs_pos, pcs_component)
                self.execute_tree(mainterm_1)

    def execute_group_2_1_1(self, split_term):
        print("--------execute_group_2_1_1--------")
        """
        Args
            split_term -> two individual search terms gathered from a "see" value
        Returns
            None.
        """
        # This method is called in execute_group_2_1()
        # This method re-queries the data to find new_mainterm given by "see" value
        # Once it finds the parent_search_term, it will find the child_search_term within the parent_search_term
        term_found_flag = False
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
                        term_found_flag = True
                        self.execute_tree(subterm)
                        break
        if not term_found_flag:

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

        # Execute method
        # This method is called in execute_group_2()
        # This method handles mainterm objects with a "see" key that contains "codes" and "__text" keys
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

        # Execute method
        # This method is called in execute_group_2()
        # This method handles mainterm objects with a "see" key that contains "tab" and "__text" keys
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

        # Execute method
        # This method is called in Mainterm_Parser().parent_execute() and Mainterm_Parser().parent_execute()
        # This method handles a mainterm object with keys:
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

        # Execute method
        # This method is called in Mainterm_Parser().parent_execute() and Mainterm_Parser().parent_execute()
        # This method handles a mainterm object with keys:
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

        # Execute method
        # This method is called in Mainterm_Parser().parent_execute() and Mainterm_Parser().parent_execute()
        # This method handles a mainterm object with keys:
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

        # Execute method
        # This method is called in Mainterm_Parser().parent_execute()
        # This method handles a "mainterm" with keys:
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

################################################# Execute Query - Continuous ##################################################
###############################################################################################################################

if not testing:
    # Execute queries continuously until user is done
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
                parser = Parser() # Doing this to make sure pcs_component_flag is reset to False.Reset is also added into execute functions during if self.pcs_component checks. Can move this outside of while loop if makes more sense.
                parser.execute_tree(mainterm)
                break
        user_flag = input("\nDo you want to search another term? (y/n) : ").lower()

################################################# Run Test - All Mainterms ####################################################
###############################################################################################################################

## TESTING ###
if testing:
    # Test All Mainterms
    master_test = Master_Test()
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
            # Determine outcome of test in above method
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
    print(f"Number of unsuccessful tests: {len(master_test.unsuccessful_tests)}")
    total_tests_completed = len(master_test.successful_tests) + len(master_test.unsuccessful_tests)
    print(f"Total Tests Completed: {total_tests_completed}")
    print("---------Unsuccessful Tests---------")
    for term in master_test.unsuccessful_tests:
        if isinstance(term, tuple):
            print(f"\nMainterm: {term[0]['title']} \nSubterm: {term[1]}")
        else:
            print(f"\nMainterm: {term['title']} \n {term}")

################################################# Run Test - Individual Mainterm ##############################################
###############################################################################################################################

### TESTING ###
# if testing:
    # Test Singular Mainterm

    # test_mainterm_title = "New Technology"

    # master_test = Master_Test()
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
    #             # Determine outcome of test in above method
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
    # total_tests_completed = len(master_test.successful_tests) + len(master_test.unsuccessful_tests) +
    # print(f"Total Tests Completed: {total_tests_completed}")
    # print("---------Unsuccessful Tests---------")
    # for term in master_test.unsuccessful_tests: pprint(term["title"])