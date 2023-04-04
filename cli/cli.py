#!/usr/bin/env python3

# A Click CLI with the following commands:
#   gets a book by ID and prints the book using pprint.
#   gets a customer by ID and prints the customer using pprint.

import click
import requests
import pprint

CUSTOMERS_SERVER = "http://localhost:8001/customers"
BOOKS_SERVER = "http://localhost:8000/books"


@click.group()
def main():
    pass


@main.command()
@click.argument("book_id", type=int)
def book(book_id):
    book = requests.get(f"{BOOKS_SERVER}/{book_id}").json()
    pprint.pprint(book)


@main.command()
@click.argument("customer_id", type=int)
def customer(customer_id):
    customer = requests.get(f"{CUSTOMERS_SERVER}/{customer_id}").json()
    pprint.pprint(customer)


if __name__ == "__main__":
    main()
