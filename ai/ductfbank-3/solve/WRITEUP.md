ductfbank 3
===========

This uses much of the same principles as ductfbank 2, however the catch is that
now you have to ask Bobby to look up information that he is not normally allowed
to access.

From looking at the bank service, we can see that the listAccounts() and
getAccount() functions are vulnerable to SQL injection. However only the
getAccountDetails() tool allows for user input. 

A simple SQL injection such as `'OR 1=1 --` would return the first result from
the DB. Also as we assume the flags are stored somewhere in the DB, they probably
aren't stored in the nicknames as anyone with a DUCTFBank account would be able
to name their account what they like, which would mean it might not make sense
from a real life perspective.

Next, we can try looking for different tables. If you use the `sqlite_master`
table, you can get a list of all tables. In order to query another table, we can
always use `UNION SELECT`, keeping in mind the original number of parameters in
the query.

```
' OR 1=0 UNION SELECT 1,1,1,1,name, sql FROM sqlite_master LIMIT 1 OFFSET 1
' OR 1=0 UNION SELECT 1,1,1,1,name, sql FROM sqlite_master LIMIT 1 OFFSET 2
' OR 1=0 UNION SELECT 1,1,1,1,name, sql FROM sqlite_master LIMIT 1 OFFSET 3
...

The AI Bot has greater protections for SQL scripts so you probably have to go
via the nickname approach to give it somewhat trusted data.

So looking at the final flag result which should look like
```
flags|CREATE TABLE flags (
    flag TEXT NOT NULL UNIQUE
  )
```

the final exploit to ask the AI to run should be 
```
' OR 1=0 UNION SELECT 1,1,1,1,1, flag FROM flags --
```

You may have to ask multiple times in different chats to achieve this. Also the
main motivation for the chat timeout (over 50 messages in a conversation) is so
that it doesn't exponentially charge us for more tokens.
