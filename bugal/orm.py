"""Definition of DB Tables
"""
# TODO: can be used for refactoring, but not now used
import logging
from sqlalchemy import Table, MetaData, Column, Integer, String, Date
from sqlalchemy.orm import mapper  # relationship


from bugal import model


logger = logging.getLogger(__name__)
metadata = MetaData()

transaction = Table(
    "transaction",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("text", String),
    Column("status", String),
    Column("debitor", String),
    Column("verwendung", String),
    Column("konto", String),
    Column("value", Integer),
    Column("debitor_id", String),
    Column("mandats_ref", String),
    Column("customer_ref", String),
    Column("src_konto", String),
    Column("checksum", String),
)

history = Table(
    "history",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("file_name", String),
    Column("file_type", String),
    Column("account", String),
    Column("min_date", Date),
    Column("max_date", Date),
    Column("import_date", String),
    Column("checksum", String)

)

propert = Table(
    "property",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("inout", String),
    Column("name", String),
    Column("type", String),
    Column("cycle", String),
    Column("number", Integer),
    Column("sum", Integer),
)

rules = Table(
    # TODO: complete definition
    "rules",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("pattern", String),
    Column("inout", String),
    Column("property_id", String),
    Column("cycle", String),
    Column("number", Integer),
    Column("sum", Integer),
)

mapping = Table(
    "mapping",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("transaction_id", Integer),
    Column("property_id", Integer),
    Column("type", String),
    Column("number", Integer),
    Column("value", Integer),
)


def start_mappers():
    """Mapps btw. the DB Tables and DataClass objects
    """
    mapper(model.History, history)
    # mapper(model.Transaction, transaction)
    # mapper(model.Property, propert)
    # mapper(model.Rules, rules)
    # mapper(model.Mapping, mapping)
