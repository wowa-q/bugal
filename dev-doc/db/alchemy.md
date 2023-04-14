# Useage of SQLALCHEMY in nutshell

## ORM

### Session

[ORM Session](https://docs.sqlalchemy.org/en/20/tutorial/dbapi_transactions.html#tutorial-executing-orm-session)

The interactive object is the [Session](https://docs.sqlalchemy.org/en/20/orm/session_api.html#sqlalchemy.orm.Session). If the session is used it refers internally to a connection, which is used to emit SQL instructions.

```python
from sqlalchemy.orm import Session

stmt = text("SELECT x, y FROM some_table WHERE y > :y ORDER BY x, y")
with Session(engine) as session:
    result = session.execute(stmt, {"y": 6})
    for row in result:
        print(f"x: {row.x}  y: {row.y}")

```

#### Class members

- new
- no_autoflush
- deleted
- dirty
- is_active
- __init__()
- add()
- add_all()
- begin()
- begin_nested()
- bind_mapper()
- bind_table()
- bulk_insert_mappings()
- bulk_save_objects()
- bulk_update_mappings()
- close()
- close_all()
- commit()
- connection()
- delete()
- enable_relationship_loading()
- execute()
- expire()
- expire_all()
- expunge()
- expunge_all()
- flush()
- get()
- get_bind()
- get_nested_transaction()
- get_transaction()
- identity_key()
- identity_map
- in_nested_transaction()
- in_transaction()
- info, invalidate()
- is_modified()
- merge()
- object_session()
- prepare()
- query()
- refresh()
- rollback()
- scalar()
- scalars()

### Using a sessional

[Session Basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html#id1)

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# an Engine, which the Session will use for connection
# resources
engine = create_engine("postgresql+psycopg2://scott:tiger@localhost/")

# create session and add objects
with Session(engine) as session:
    session.add(some_object)
    session.add(some_other_object)
    session.commit()

```

`sessionmaker` can be used, so session can be created without always passing the engine:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# an Engine, which the Session will use for connection
# resources, typically in module scope
engine = create_engine("postgresql+psycopg2://scott:tiger@localhost/")

# a sessionmaker(), also in the same scope as the engine
Session = sessionmaker(engine)

# we can now construct a Session() without needing to pass the
# engine each time
with Session() as session:
    session.add(some_object)
    session.add(some_other_object)
    session.commit()
# closes the session
```

#### Querying

The select can be used to filter data and to retrieve them from the DB:

```python
from sqlalchemy import select
from sqlalchemy.orm import Session

with Session(engine) as session:
    # query for ``User`` objects (User is a table in DB)
    statement = select(User).filter_by(name="ed")

    # list of ``User`` objects
    user_obj = session.scalars(statement).all()

    # query for individual columns
    statement = select(User.name, User.fullname)

    # list of Row objects
    rows = session.execute(statement).all()
```

The methode `scalars` executes the statement and returns the result not as a row, but scalars (pure values).

#### Adding items

With `Session.add()` new instances are added

```python
user1 = User(name="user1")
user2 = User(name="user2")
session.add(user1)
session.add(user2)

session.commit()  # write changes to the database

# or to add a list of instances:
session.add_all([item1, item2, item3])
```

#### Deleting items

### Table Metadata

[Table Metadata](https://docs.sqlalchemy.org/en/20/tutorial/metadata.html#tutorial-orm-table-metadata)

In ORM usage the Python classes are mapped to a table. The class attributes are linked to a column of a table. `Users` class is a table in the DB. `name`, `lastname` etc are the columns in this table.

To create such a table in DB `DeclarativeBase` can be used:

```python
from sqlalchemy.orm import DeclarativeBase
class Base(DeclarativeBase):
    pass
```

The classes will need to subclass the `Base` class. The `Base` class will automatically create `MetaData` and every subclass will be associated with the `MetaData`. So `MetaData` is a collection of tables. These are the [members](https://docs.sqlalchemy.org/en/20/core/metadata.html#sqlalchemy.schema.MetaData) of it:

- clear()
- create_all()
- drop_all()
- reflect()
- remove()
- sorted_tables
- tables

Now the tables can be created:

```python
from typing import List
from typing import Optional
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]]

    addresses: Mapped[List["Address"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"

class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str]
    user_id = mapped_column(ForeignKey("user_account.id"))

    user: Mapped[User] = relationship(back_populates="addresses")

    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"
```

The classes automatically generate `__init__()` method if we don't create own. The generated method accepts all attributes names as optional keyword arguments.
`sandy = User(name="sandy", fullname="Sandy Cheeks")`

__The example above is from SQLAlchemy 2.0. In the older version instead of `mapped_column()`, which returns a `Column`, the `Column` constructor was used.__

#### Table reflection - how to generate Table from existing DB

```python
some_table = Table("some_table", metadata_obj, autoload_with=engine)
```

The object `some_table` has now all the information of the columns of the table.

[Reflection DB Objects](https://docs.sqlalchemy.org/en/20/core/reflection.html)

## Working with data

- [data inseart](https://docs.sqlalchemy.org/en/20/tutorial/data_insert.html)

### Add a new line with data

`inseart()` can be used to inseart data into a table in fact ot inseart a new row.

```python
from sqlalchemy import insert

stmt = insert(user_table).values(name="spongebob", fullname="Spongebob Squarepants")

with engine.connect() as conn:
     result = conn.execute(stmt)
     conn.commit()
```

where stm means:

```sql
INSERT INTO user_account (name, fullname) VALUES (:name, :fullname)
```

### Update data from table

To copy data from table the inseart in the other table:

```python
select_stmt = select(user_table.c.id, user_table.c.name + "@aol.com")

insert_stmt = insert(address_table).from_select(
    ["user_id", "email_address"], select_stmt
)
```

### Retriving data from DB

[select](https://docs.sqlalchemy.org/en/20/tutorial/data_select.html)

```python
from sqlalchemy import select

stmt = select(user_table).where(user_table.c.name == "spongebob")

with engine.connect() as conn:
    for row in conn.execute(stmt):
        print(row)      # -> (1, 'spongebob', 'Spongebob Squarepants')
# OR
with Session(engine) as session:
    for row in session.execute(stmt):
        print(row)      # -> (User(id=1, name='spongebob', fullname='Spongebob Squarepants'),)

```

ORM like: `Session.execute()`

The SQL EXISTS keyword is an operator that is used with scalar subqueries to return a boolean true or false depending on if the SELECT statement would return a row. Here how this can be achieved with Alchemy:

```python
subq = (
     select(func.count(address_table.c.id)).where(user_table.c.id == address_table.c.user_id).group_by(address_table.c.user_id).having(func.count(address_table.c.id) > 1)).exists()

with engine.connect() as conn:
    result = conn.execute(select(user_table.c.name).where(subq))
    print(result.all())

```

### ORM Data manipulation

[orm data manipulation](https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html)

#### Insearting rows

##### Create Objects

Instances of Classes represent rows

```python
squidward = User(name="squidward", fullname="Squidward Tentacles")
krabs = User(name="ehkrabs", fullname="Eugene H. Krabs")

```

The `__init__()` constructor was automatically generated by ORM, so it can be used to instantiate the Table-Classes. The __primary key__ must not be set, if the automatic increament of the data base shall be used. When the class was instantiated the `id` has the value of `None`, since the database hasn't generated it yet.

##### Add objects to a session

```python
session = Session(engine)
session.add(squidward)      # the object is now pending
session.add(krabs)

# pending object can be shown with
session.new
```

##### Flushing

The change to the data base is done in one step ("*flush*"): `session.flush()`.

```python
session.flush()
session.commit() # to let the data base to store the changes
```

After flushing the objects are now in a state persistent -> the primary key is now generated and `krabs.id` is not `None` anymore.

#### Reading data

##### By using __primary key__

```python
some_squidward = session.get(User, 4)
```

This will use the values from memory, or emit SELECT command to the data base to get the data.

##### By using __SELECT__

`sandy = session.execute(select(User).filter_by(name="sandy")).scalar_one()`

#### Deleting data

Deletion can be done by `Session.delete()`. However, nothing will happen until the next flushing.

```python
patrick = session.get(User, 3)

session.delete(patrick)         # nothing happened yet
session.commit()                # now patrick was deleted
patrick in session              # False
```

__When we are done with the session, we should explicitly close it:__ `session.close()`.

## Relationship between tables

[releation](https://docs.sqlalchemy.org/en/20/tutorial/orm_related_objects.html)

```python
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "user_account"

    # ... mapped_column() mappings

    addresses: Mapped[list["Address"]] = relationship(back_populates="user")


class Address(Base):
    __tablename__ = "address"

    # ... mapped_column() mappings

    user: Mapped["User"] = relationship(back_populates="addresses")

u1 = User(name='peter', fullname='park')
u1.addresses    # empty list
```
