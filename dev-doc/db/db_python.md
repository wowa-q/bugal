```python
import sqlite 3 as sql

connection = sql.connect("hr.db") # will connect or create new BD

# create cursor
cursor = connection.cursor() # will create cursor

cursor.execute(''' SQL TEXT TO BE EXECUTED''')
# Example to create a table with the name employees
cursor.execute('''CREATE TABLE IF NOT EXISTS employees
                (Emp_ID INT, Name TEXT, Position TEXT);''')

# Insert new data
name = 'Paul'
position = 'Engineer'
cusror.execute('''`INSERT INTO` Tablename (Name, Position) VALUES (?, ?)''', (name, position))

# changes on DB has to be committed
connection.commit()

# the connection to the DB needs to be closed
connection.close()

```
