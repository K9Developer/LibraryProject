from fuzzywuzzy import fuzz
from Librarian import Librarian
from Visitor import Visitor
import os
from time import sleep as wait

# Class for the library computer
class LibraryComputer:

    # INIT method that is called when the class is instantiated (created)
    def __init__(self):

        # Initiate the librarian and visitor classes, as we pass self to the constructor which means those classes have
        # access to the functions and variables of this class
        self.visitor = Visitor(self)
        self.librarian = Librarian(self)

        # Initiate the roles and variables
        self.chosen_role = None
        self.roles = ["visitor", "librarian"]
        self.role_options = {
            "librarian": [
                "add book",
                "see rented books",
                "change password",
                "see book stock"
            ],
            "visitor": [
                "rent book",
                "return book",
                "see book list",
                "search book",
                "view book"
            ]
        }

        print("Welcome to the Library Computer.")
        print("----------------------------------------")

    def fuzzy_match_to_list(self, string, lst):

        # Setup function variables
        matches = []
        fuzzy_threshold = 80

        # Loop over every item in the given list
        for item in lst:

            # Get the score of the match between the current item of the list and the given string,
            # if the score is greater than the threshold add to the match list
            ratio_score = fuzz.ratio(string, item)
            if ratio_score > fuzzy_threshold:
                matches.append({
                    "item": item,
                    "score": ratio_score
                })
        
        # Sort the matches by score
        return sorted(matches, key=lambda k: k["score"], reverse=True)

    def verify_role(self, role):

        # Check if the role is in the list of roles
        if role.lower() in self.roles:
            return {"verified": True}
        
        # if its not in the list return False and a list of the most similar items of the role from the role list
        return {
            "verified": False,
            "option_meant": self.fuzzy_match_to_list(role, self.roles)
        }

    def verify_option(self, option):
        # If the length of the option is of length of one then that means the option is an ID and not an option name
        # And because the option id is just the index (but +1) we just use it as the index-1
        # ^^^ Thats just to convert an option id to an option name
        if len(option) == 1:
            option = self.role_options[self.chosen_role][int(option)-1]
        
        # If the option name is inside the possible options for a given role, verify it, and return True. (with the option name incase the user entered an ID)
        if option.lower() in self.role_options[self.chosen_role]:
            return {"verified": True, "option": option}
        
        # If its not verified return False and a list of the most similar items of the option from the role options list
        return {
            "verified": False,
            "option": option,
            "option_meant": self.fuzzy_match_to_list(option, self.role_options[self.chosen_role])
        }


    def role_funcs(self):
        # Add some delay just for cosmetics
        wait(2)

        print("Here are the options you can do:")

        # Loop over each option in the role options and print them like this: option_index+1. option_name (option_id)
        for index, func_option in enumerate(self.role_options[self.chosen_role]):
            print(f"\t{index+1}. {func_option} (id: {index+1})".title())
        
        # Get the chosen option from the user and verify it.
        option = input("What function do you choose? (id/name): ")
        option_verified = self.verify_option(option)
        
        # If the option is verfied then just check the role and if its a visitor call the do_option function for the visitor, same for the librarian
        if option_verified["verified"]:
            if self.chosen_role == "visitor":
                self.visitor.do_option(option_verified["option"])
            elif self.chosen_role == "librarian":
                self.librarian.do_option(option_verified["option"])
        else:
            # Incase there was no match for the option, print a message (with the most similar option if it exists) and ask for the option again
            print(f"There was no match for {option_verified['option']}, {('did you mean ' + option_verified['option_meant'][0]['item'] + '? ') if len(option_verified['option_meant'])else ''}please try again.")
            print("---------------------\n")
            self.role_funcs()

    def ask_role(self):

        # Asks the user to choose a role
        role = input("Please choose your role [librarian/visitor]: ")

        # Verify the role
        role_verified = self.verify_role(role)

        # If it is verified and the role is librarian
        if role_verified["verified"]:
            self.chosen_role = role
            if self.chosen_role == "librarian":

                # Check if the password hash file exists (which means a password has been chosen before)
                if os.path.exists("./password_hash.hash"):
                    password = input("Please enter your password: ")

                    # Check the password with the function in the Librarian class,
                    # if its incorrect just ask for the roles again after saying its incorrect
                    if not self.librarian.check_password(password):
                        print("Wrong password!")
                        print("---------------")
                        self.ask_role()
            
            # Greet the user and show them their options according to the chosen role
            print(f"Welcome, {self.chosen_role}!")
            self.role_funcs()
        else:

            # If the user entered an unknown role just print a message (with the most similar role if it exists) and ask for the role again
            print(f"There was no match for {role}, {('did you mean ' + role_verified['option_meant'][0]['item'] + '? ') if len(role_verified['option_meant'])else ''}please try again.")
            print("---------------------\n")
            self.ask_role()


# This will run only if this python file runs directly (not as a module or imported from another file)
if __name__ == "__main__":
    # Create the computer object and ask for the role
    computer = LibraryComputer()
    computer.ask_role()