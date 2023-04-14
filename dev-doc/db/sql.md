# SQLite Basics

The SQL commands can be tried here:
[Trying platform]([ug.md](https://www.sqlitetutorial.net/tryit/query/sqlite-select/#3))

---

## SELECT - query data from table

Example comand:

``` sql
SELECT DISTINCT column_list
FROM table_list
  JOIN table ON join_condition
WHERE row_filter
ORDER BY column
LIMIT count OFFSET offset
GROUP BY column
HAVING group_filter;
```

+ Use `ORDER BY` clause to __sort__ the result set
+ Use `DISTINCT` clause to __query unique rows__ in a table
+ Use `WHERE` clause to __filter rows__ in the result set
+ Use `LIMIT OFFSET` clauses to __constrain the number of rows__ returned
+ Use `INNER JOIN` or `LEFT JOIN` to query data from __multiple tables__ using join.
+ Use `GROUP BY` to get the __group rows__ into groups and apply aggregate function for each group.
+ Use `HAVING` clause to __filter groups__

### simple use

`SELECT` column_list `FROM` table;

1. specify the table in the `FROM` clause
2. specify the column or a list of coumns, separated by `,` in the `SELECT` clause

table: `tracks`
|TrackId       |Name        |Price
|----------    |---         | ----
|1   	       |blabla1   	|1€
|2   	       |blabla2  	|2€
|3             |blubla3 	|3€
|4             |blabul4     |4€

`SELECT` trackid, name, price `FROM` tracks;

to select all columns from the table is possible:

`SELECT` * `FROM` tracks;

---

## DISCTINCT - to remove duplicate rows from the result

`SELECT DISCTINCT` column_list `FROM` table;

The selected columns will be used to evaluate the duplicate. `NULL` values are considered as duplicates.

---

## WHERE - to filter the results

`SELECT` column_list `FROM` table `WHERE` search_condition;

`WHERE` can be used to filter rows from the results by query.

The query has following form: `left_expression COMPARISON_OPERATOR right_expression`

### Examples

+ `WHERE` column1 = 100;
+ `WHERE` column2 `IN` (1,2,3);
+ `WHERE` column3 `LIKE` 'an%';
+ `WHERE` column4 `BETWEEN` 10 `AND` 20;

Besides the `SELECT` clause, `WHERE` can be used in  `UPDATE` and `DELETE` clause

### Comparison operators supported

|Operator   | Meaning           |
|---        |---                |
|=          | Equal             |
|!=  or  <> | not Equal         |
|<          | lesser            |
|>          | greater           |
|<=         | lessor or equal   |
|>=         | greater or equal  |

### Logical operators supported

|Operator   | Meaning           |
|---        |---                |
|ALL        | return 1 if all expressions are 1 |
|AND        | return 1 if both expressions are 1, or 0 if one of the are 1         |
|ANY        | return 1 if any one of a set of comparisions is 1           |
|BETWEEN    | return 1 if a value is within the range           |
|EXISTS     | return 1 if a subquery contains any rows   |
|IN         | return 1 if a value is in a list of values  |
|LIKE       | return 1 if a value matches a pattern             |
|GLOBE      | return 1 if a value matches a pattern __case sensitive__  using UNIX wildcards        |
|NOT        | reverses the value of other operators |
|OR         | return true if either expression is 1            |

``` sql
    SELECT
        name,
        milliseconds,
        bytes,
        albumid
    FROM
        tracks
    WHERE
        albumid = 1
    AND milliseconds > 250000;
```

with the `LIKE` example

``` sql
    SELECT
        name,
        albumid,
        composer
    FROM
        tracks
    WHERE
        composer LIKE '%Smith%'
    ORDER BY
        albumid;
```

#### GLOB operator

+ (*) matches any number of characters
+ (?) matches exatly one character
+ [] list wildcard to match one character from a list e.g. [xyz]match any single x, y, or z
    + it allows also a range of characters e.g. [a-zA-Z-9]
        + ^ can be used to exclude a character from the list e.g. [^0-9] match everything except a number

`WHERE` column3 `GLOB` 'Man*';

---

## ORDER BY - to specify the order of provided data

`SELECT` column_list `FROM` table `ORDER BY` column1 `ASC`, column2 `DESC`;

---

## INSERT - to inseart new rows into table

---

## UPDATE - to update existing data in the table

---

## DELETE - to delete rows from the table

---

## REPLACE - to replace or insert row into table

---

## Data types

|Storage Class | Meaning           | Example |
|---           |---                |--- |
| NULL         | missing information or unknown             | |
| INTEGER      | whole numbers pos. or negative             | 1 |
| REAL         | decimal values, 8-byte floats             | 1.2 |
| TEXT         | Character data. various character encodingsare supported   | ' correct text'
| BLOB         | binary large object, to store any kind of data             | x'100'

The type can be checked by `typeof()` function e.g.

``` sql
    `SELECT` 
            typeof(100),
            typeof(10.0),
            typeof('100'),
            typeof(x'100'),
            typeof(NULL);
```

---

## Date & Time

If you use the TEXT storage class to store date and time value, you need to use the __ISO8601__ string format as follows: YYYY-MM-DD HH:MM:SS.SSS

To insert date and time into a table `datetime_text()` function can be used e.g. `SELECT datetime('now');` or `SELECT datetime('now', 'localtime');`

``` sql
INSERT INTO datetime_text (d1, d2)
VALUES(datetime('now'),datetime('now', 'localtime'));
```
