import json
import os
from fuzzywuzzy import fuzz

class Visitor:
    def __init__(self, main):
        # This is the LibraryComputer object (as we passed self to the constructor) and as you learned self is a reference to the object (the object itself)
        self.main = main
    
    def get_book_data(self):

        # Check if the data.json file exists (its the file that stores the book data), if not create it with an empty dictionary
        if not os.path.exists("./data.json"):
            with open("./data.json", "w+") as f:
                json.dump({}, f, indent=4)
        
        # Read the data.json file and return its content as a dictionary
        with open("./data.json", "r") as f:
            return json.load(f)

    def is_id_available(self, id):
        # Get the book data as a dictionary
        book_data = self.get_book_data()

        # Check if the id of the book exists in the book data, if not then that means the book doesn't exist thus not available
        if not book_data.get(id):
            return False

        # It takes the number of available books (from a certain id) and converts it to a boolean,
        # As we learned any number can be converted to a boolean, and if its bigger than 0 it means when 
        # we convert it to a boolean it will return true, otherwise it will return false
        return bool(book_data[id]["available_count"])

    def change_book_data(self, action, book_id):
        # Get the book data as a dictionary
        book_data = self.get_book_data()

        # If the action is rent
        if action == "rent":

            # Increase the number of rented books
            book_data[book_id]["rented_count"] += 1

            # Decrease the number of available books (because we just took one)
            book_data[book_id]["available_count"] -= 1

            # Update the data.json file (w+ overwrites the whole file)
            with open("./data.json", "w+") as f:
                json.dump(book_data, f, indent=4)
        
        # If the action is return
        elif action == "return":

            # Decrease the number of rented books (because we just returned one)
            book_data[book_id]["rented_count"] -= 1

            # Increase the number of available books
            book_data[book_id]["available_count"] += 1
            with open("./data.json", "w+") as f:

                # Update the data.json file (w+ overwrites the whole file)
                json.dump(book_data, f, indent=4)

    def do_option(self, option):

        # Check each option and call the corresponding function
        if option == "rent book":
            self.rent_book()
        elif option == "return book":
            self.return_book()
        elif option == "see book list":
            self.see_book_list()
        elif option == "search book":
            self.search_book()
        elif option == "view book":
            self.view_book()
    
    def rent_book(self):

        # Ask the user for the book id
        book_id = input("Please enter book id: ")

        # Check if the book id is available, if so then call the change_book_data function
        # with the action "rent" and the chosen book_id
        if self.is_id_available(book_id):
            self.change_book_data("rent", book_id)
        else:

            # If the book id is not available then print a message and show the user the available options again
            print("Sorry, but we are dont have an available book with this id!")
            print("---------------")
            self.main.role_funcs()
    
    def return_book(self):

        # Ask the user for the book id
        id = input("Please enter book id: ")

        # Get book data as a dictionary
        book_data = self.get_book_data()

        # Check if the book has NOT been rented at least once
        if book_data[id]["rented_count"] <= 0:

            # If the book has NOT been rented at least once then print a message
            # and show the user the available options again
            print("We dont have any record that you have rented this book!")
            print("---------------")
            self.main.role_funcs()
        
        # If the book has been rented at least once then call the change_book_data function with
        # The action "return" and the chosen book_id
        self.change_book_data("return", id)

    def see_book_list(self):
        print("Here is our book list:")

        # Get the book data as a dictionary
        book_data = self.get_book_data()

        # Loop over all books
        for book in book_data:
            # the variable "book" is currently the key of the dictionary which is the book ID so I just
            # get the data of the book by using the book ID as a key
            book = book_data[book]

            # Print the book data for the book like this: - book name (book id): available count
            print(f"- {book['name']} ({book['id']}): {book['available_count']} available")
        print("---------------")

        # Show the user the available options again
        self.main.role_funcs()
    
    def search_book(self):

        # Ask the user for the search query, replace all spaces and lower case it
        search_query = input("Please enter search query: ").replace(" ", "").lower()

        # Get the book data as a dictionary
        book_data = self.get_book_data()
        search_ratios = []
        fuzzy_threshold = 80

        # Loop over all books
        for book in book_data:

            # Append to the search_ratios list the book id and ratio between the search query and the book search query which is the book name, description, and author with no spaces
            search_ratios.append({
                "book": book,
                "score": fuzz.partial_ratio(search_query, book_data[book]['search_query']) # partial ratio just ignores if theres extra data, if some of it is there then its 100%, its good because we just have a big string of every data of the book
            })

        # Sort the search_ratios list by the match score
        search_ratios = sorted(search_ratios, key=lambda k: k["score"], reverse=True)

        # Replace every item in the list with None if the score is lower than the fuzzy threshold
        search_ratios = map(lambda k: k if k["score"] > fuzzy_threshold else None, search_ratios)
        
        # Loop over all books in the search_ratios list
        for book in search_ratios:
            
            # If the current item is not None then print the book data for the book like this: - book name (book id): available count
            if book:
                book = book['book']
                print(f"- {book_data[book]['name']} ({book_data[book]['id']}): {book_data[book]['available_count']} available")
        print("--------------------")
        
        # Show the user the available options again
        self.main.role_funcs()

    def view_book(self):

        # Ask the user for the book id
        book_id = input("Please enter book id: ")

        # Get book data as a dictionary
        book_data = self.get_book_data()

        # If the book data contains the book id, print all the book data that is relevant to the visitor.
        if book_data.get(book_id):
            print(f"\tBook data for ID: {book_id}")
            print("\tBook Name: ", book_data[book_id]['name'])
            print("\tBook Author: ", book_data[book_id]['author'])
            print("\tBook ID: ", book_data[book_id]['id'])
            print("\tBook Release Date: ", book_data[book_id]['release_date'])
            print("\tBook Available Count: ", book_data[book_id]['available_count'])
            print("\tBook Description: ", book_data[book_id]['description'])
            print("---------------")
            # Show the user the available options again
            self.main.role_funcs()
        else:

            # If the book is not available (at all, not just for renting) then print a message saying it doesnt exist
            print("Sorry, but we are dont have an available book with this id!")
            print("---------------")

            # Show the user the available options again
            self.main.role_funcs()  