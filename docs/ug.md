# Users Guide

## Overview 

This chapter provides an overview what is needed to use the **bugal** Tool. The bugal stays for bugalteria and its purpose is to track own financial activities, by using the extract from the bancking.

### What is needed to use the bugal tool

The bugal tool works with a command line interface or with a web front end. In the followng chapters the modes of the tool will be described.

## CLI mode

### Following commands are supported

#### Create-new-DB

``` --cmd Create-new-DB --db_name example.db ```

with this command new DB file will be created

##### Parameter

- ` --db_name example.db ` file name or path to the DB files

#### Import-new-csv

``` --cmd Import-new-csv --db_name example.db --csv_name 1001670080.csv ```

With this command the csv file will be imported and archived

##### Parameter

- ``` --csv_name 1001670080.csv ``` file name or path to the csv files

##### Requirements

- db muss bereits exisitieren
- csv datei muss unter xyz abgelegt werden
- die csv Datei muss original von DKB sein

#### Print Excel Report

``` --cmd print_xls --db_name example.db --year 2016 --month 01 ```

The command prints a new excel report. Transactions are filter for a month.

##### Parameter

- `--db_name [path]`: which DB shall be used for getting data
- `--year [int]`: for which year needs to be filtered
- `--month [int]`: for which month shall be filtered

##### Requirements

1. db needs to exist

#### Import from Excel

``` --cmd import_xls --db_name example.db --xls_name template.xlsx ```

##### Parameter

- `--db_name [path]`: which DB shall be used for getting data
- `--xls_name [path]`: Excel file to be imported

##### Requirements

1. db needs to exist
2. the excel file was initially created from **bugal**
3. all transactions have a hash value
4. ..

#### Importierte Attribute

|Excel Attribut |DB Attribut|
|---            |---        |
|Kategorie      |Cathegory  |
