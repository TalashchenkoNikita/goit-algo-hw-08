import pickle
import re
from collections import UserDict
from datetime import datetime, timedelta


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Birthday(Field):
    def __init__(self, value):
        pattern = r"^\d{2}\.\d{2}\.\d{4}$"
        if not re.match(pattern, value):
            print("Неправильний формат дати, має бути - DD.MM.YYYY")
            raise ValueError()
        self.value = value


class Phone(Field):
    def __init__(self, value):
        if len(value) == 10:
            self.value = value
        else:
            print("Номер телефону не є дійсним")
            raise ValueError()


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        new_phone = Phone(phone)
        self.phones.append(new_phone)

    def add_birthday(self, birthday):
        birthday = Birthday(birthday)
        self.birthday = birthday

    def remove_phone(self, phone):
        for phone_num in self.phones:
            if phone_num.value == phone:
                self.phones.remove(phone_num)

    def edit_phone(self, phone, new_phone):
        for i, phone_num in enumerate(self.phones):
            if phone_num.value == phone:
                self.phones[i] = Phone(new_phone)

    def find_phone(self, phone):
        for contact in self.phones:
            if contact.value == phone:
                return contact

    def find_birthday(self):
        return self.birthday.value

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name: Name):
        return self.data.get(str(name))

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def all_contacts(self):
        return [str(record) for record in self.data.values()]

    def get_upcoming_birthdays(self):
        upcoming_birthdays_list = []
        current_date = datetime.now().date()
        for user in self.data.values():
            next_birthday_date = datetime.strptime(
                user.birthday.value, "%d.%m.%Y").date().replace(year=current_date.year)
            if (next_birthday_date - current_date).days < 0:
                next_birthday_date = next_birthday_date.replace(
                    year=current_date.year + 1)
            if (next_birthday_date - current_date).days < 7:
                birthday_person = {"name": user.name.value,
                                   "congratulation_date": next_birthday_date.strftime("%Y.%m.%d")}
                if next_birthday_date.weekday() >= 5:
                    birthday_person.update({"congratulation_date":
                                                (next_birthday_date + timedelta(
                                                    days=7 - next_birthday_date.weekday())).strftime("%Y.%m.%d")})
                upcoming_birthdays_list.append(birthday_person)
        return upcoming_birthdays_list


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Incorrect value"
        except IndexError:
            return "Give me a name"
        except KeyError:
            return "Name not found"

    return inner


@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    return book.find(name)


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def add_birthday(args, book: AddressBook):
    name, date, *_ = args
    record = book.find(name)
    message = "Birthday updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Birthday added."
    if date:
        record.add_birthday(date)
    return message


@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record is None:
        return "Name not found"
    return record.find_birthday()


@input_error
def birthdays(book: AddressBook):
    return book.get_upcoming_birthdays()


@input_error
def update_contact(args, book: AddressBook):
    name, phone, new_phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        message = "Contact does not exist."
    if new_phone:
        record.edit_phone(phone, new_phone)
    return message


@input_error
def get_all(book: AddressBook):
    return book.all_contacts()


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)
        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book)
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "change":
            print(update_contact(args, book))
        elif command == "all":
            print(get_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
