# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.tools.sql import column_exists, create_column, table_exists

logger = logging.getLogger(__name__)


def _set_is_pricelist_cache_computed(cursor):
    table_name = "product_pricelist"
    column_name = "is_pricelist_cache_computed"
    if column_exists(cursor, table_name, column_name):
        return
    logger.info(f"creating column {column_name} on table {table_name}")
    create_column(cursor, table_name, column_name, "boolean")
    query = """
        UPDATE product_pricelist
        SET is_pricelist_cache_computed = true;
    """
    cursor.execute(query)


def _set_is_pricelist_cache_available(cursor):
    table_name = "product_pricelist"
    column_name = "is_pricelist_cache_available"
    if column_exists(cursor, table_name, column_name):
        return
    logger.info(f"creating column {column_name} on table {table_name}")
    create_column(cursor, table_name, column_name, "boolean")
    query = """
        UPDATE product_pricelist
        SET is_pricelist_cache_available = true;
    """
    cursor.execute(query)


def _set_parent_pricelist_ids(cursor):
    table_name = "product_pricelist_potato"
    if table_exists(cursor, table_name):
        return
    logger.info(f"creating table {table_name}")
    create_table_query = """
        CREATE TABLE product_pricelist_potato (
            child_id INTEGER NOT NULL,
            parent_id INTEGER NOT NULL,
            PRIMARY KEY(child_id, parent_id)
        );
        CREATE INDEX ON product_pricelist_potato (child_id, parent_id);
    """
    cursor.execute(create_table_query)
    fill_table_query = """
        INSERT INTO product_pricelist_potato (child_id, parent_id)
        SELECT pricelist_id, base_pricelist_id
        FROM product_pricelist_item
        WHERE pricelist_id IS NOT NULL
        AND base_pricelist_id IS NOT NULL
        AND applied_on = '3_global'
        AND base = 'pricelist';
    """
    cursor.execute(fill_table_query)


def migrate(cursor, version):
    # New fields have been introduced on product.pricelist.
    _set_is_pricelist_cache_available(cursor)
    _set_is_pricelist_cache_computed(cursor)
    _set_parent_pricelist_ids(cursor)
