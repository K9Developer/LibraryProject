import json
import os
from fuzzywuzzy import fuzz
import hashlib

class Librarian:
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

    def change_book_data(self, action, data):
        # Get the book data as a dictionary
        book_data = self.get_book_data()

        # If the action is add_new (Which mean add a new book thats not in the data.json file)
        if action == "add_new":

            # Add the new entry of book to the book data. dict.update: https://www.programiz.com/python-programming/methods/dictionary/update
            book_data.update(data)

            # Update the data.json file (w+ overwrites the whole file)
            with open("./data.json", "w+") as f:
                json.dump(book_data, f, indent=4)
        
        # If the action is add_old (Which mean add a book thats already in the data.json file)
        elif action == "add_old":
            
            # Add 1 to the available count of that book
            book_data[data]["available_count"] += 1

            # Update the data.json file (w+ overwrites the whole file)
            with open("./data.json", "w+") as f:
                json.dump(book_data, f, indent=4)

        # if the action is change_password
        elif action == "change_password":
            
            # Hash the given password and write it to the password_hash.hash file (w+ overwrites the whole file)
            with open("./password_hash.hash", "w+") as f:
                f.write(hashlib.sha256(data.encode()).hexdigest()[:64])

    def do_option(self, option):

        # Check each option and call the corresponding function
        if option == "add book":
            self.add_book()
        elif option == "see rented books":
            self.see_rented_books()
        elif option == "change password":
            self.change_password()
        elif option == "see book stock":
            self.see_book_stock()
    
    def book_exists(self, book_id):
        # Check if the book id exists in the book data
        book_data = self.get_book_data()
        return book_id in book_data

    def add_book(self):

        # Ask the user for the book id
        book_id = input("Please enter book id (press enter to auto generate): ")

        # If the book ID has not been chosen (the user just pressed enter without inputting anything)
        if book_id == "":

            # Convert all book ids to integers from the book data and put the into a sorted list,
            # then grab the last element (biggest one) and add 1 to it to create a new ID
            # that will be the biggest one and that would ensure thats a new ID
            id_list = int(list(self.get_book_data().keys())[-1])+1

            # Convert that id to a string
            book_id = str(id_list)

            # Let the user know what ID we chose
            print(f"Id chosen: {book_id}")

        # If a book with that ID already exists
        if self.book_exists(book_id):

            # Call the change_book_data function with the action "add_old" and the book id which means we
            # Are trying to add an existing book. (note that there can be multiple books with the same ID, that only means they are the same and that
            # we have a few of an existing one)
            self.change_book_data("add_old", book_id)
            
            print("Thank you, added book! (book exists)")
            print("---------------")
            
            # Show the user the available options again
            self.main.role_funcs()
        else:
            # If the book is new, ask the user for all new book info
            book_name = input("Please enter book name: ")
            book_author = input("Please enter book author: ")
            book_release_date = input("Please enter the book's release date (DD/MM/YYYY): ")
            book_description = input("Please enter book description: ")

            # Assemble the search query with the name, author, id and description of the book and make it lower case
            book_search_query = book_name+book_author+book_description+book_id
            book_search_query = book_search_query.lower()
            
            # Put all the book data into a dictionary
            book_data = {
                book_id: {
                    "name": book_name,
                    "id": book_id,
                    "available_count": 1,
                    "rented_count": 0,
                    "release_date": book_release_date,
                    "description": book_description,
                    "author": book_author,
                    "search_query": book_search_query
                }
            }

            # Call the change_book_data function with the action "add_new" and the book data so we can just add that book to the book data dict
            self.change_book_data("add_new", book_data)

    def see_rented_books(self):

        # Get the book data as a dictionary
        book_data = self.get_book_data()
        print("Rented books list:")

        # Loop over all books
        for book in book_data:

            # Check if the book has been rented at least once
            if book_data[book]["rented_count"] > 0:

                # Print the book data for the book like this: -book name (book id): rented count
                print(f"- {book_data[book]['name']} ({book_data[book]['id']}): {book_data[book]['rented_count']} rented")
        print("-----------------")

        # Show the user the available options again
        self.main.role_funcs()

    def check_password(self, password):

        # Convert the given password to a 64 bit hash
        curr_pass_hash = hashlib.sha256(password.encode()).hexdigest()[:64]
        
        # If the password file exists check if its contents (the saved password) matches the given password, if so return True
        if os.path.exists("./password_hash.hash"):
            with open("./password_hash.hash", "r") as f:
                return f.read() == curr_pass_hash
        # If the file doesnt exist and we somehow ended up here (altough there are some checks before that)
        # Just return True (because there is no password set)
        return True

    def change_password(self):

        confirmed_pass = ""
        allowed = False
        
        # If the password file exists (which means there was a password set before)
        if os.path.exists("./password_hash.hash"):

            # Ask the librarian for their current password in order to change it
            confirmed_pass = input("Please confirm your current password: ")
        else:
            
            # If the password has not been set before just allow the librarian to change it
            allowed = True

        # if the password file exists and the password is correct or the password file doesn't exist
        if self.check_password(confirmed_pass) or allowed:

            # Ask the librarian for their new password
            password = input("Enter the password you'd like: ")

            # Call the change_password function with the change_password action and the password 
            self.change_book_data("change_password", password)

            print("Thank you, password changed!")
            print("---------------")
            
            # Show the user the available options again
            self.main.role_funcs()
        else:

            # If the password is incorrect then print a message and show the user the available options again
            print("Password is incorrect!")
            print("---------------")
            self.main.role_funcs()
    
    def see_book_stock(self):

        # Get the book data as a dictionary
        book_data = self.get_book_data()
        print("Available books list:")

        # Loop over all books
        for book in book_data:

            # Check if at least one book of that ID is available
            if book_data[book]["available_count"] > 0:

                # Print the book data for the book like this: -book name (book id): available count
                print(f"- {book_data[book]['name']} ({book_data[book]['id']}): {book_data[book]['available_count']} available")
        print("-----------------")

        # Show the user the available options again
        self.main.role_funcs()