# Crypto Currency SQL Database

**Stream crypto currency prices into a SQLite data base**

## What:
These short code snippets stream market, ask and bid price and trading volume of all ``BTC`` based crypto currency pairs into a single SQLite3 database.
The data is streamed every 60 sec. into your database.

## How:
Create a SQL database, e.g., ``bittrex.db``. Copy ``bittrexStream.py`` and ``mainBittrex.py`` into your database directory. Edit ``mainBittrex.py`` if you prefer different
intervals to update the database or prefer a different base currency other than ``BTC``.

Finally run it. Easy.

