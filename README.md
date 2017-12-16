# Crypto Data SQL

**Stream crypto currency prices into a SQLite data base**

## What:
These short code snippets stream market price and trading volume of different crypto currency pairs into a single SQLite3 database.
Be sure to have installed ``poloniex`` and ``gdax`` APIs to get access to their exchange.
The data is streamed a resolution of 60 sec. into your database.

## How:
Just copy ``SQLstream.py`` and ``mainSQL.py`` into your database directory. Specify the path to your SQL database in ``mainSQL.py`` and modify it according
to the currency pairs you would like to track. Finally run it. Easy.

