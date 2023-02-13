# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from psycopg2 import sql

_logger = logging.getLogger(__name__)


def lock_jobs(cr):
    query = """
        SELECT id
        FROM queue_job
        WHERE model_name = 'product.pricelist.cache'
        AND state NOT IN (
            'STARTED', 'DONE', 'CANCELLED', 'FAILED'
        )
        FOR UPDATE;
    """
    cr.execute(query)


def set_parent_pricelists(cr):
    # pylint: disable=E8103
    args = {
        "table_name": sql.Identifier(
            "product_pricelist_cache__parent_pricelist_ids_rel"
        ),
        "column_left": sql.Identifier("pricelist_id"),
        "column_right": sql.Identifier("parent_pricelist_id"),
    }
    create_table_query = sql.SQL(
        """
        CREATE TABLE IF NOT EXISTS {table_name} (
            {column_left} INTEGER NOT NULL,
            {column_right} INTEGER NOT NULL
        );
        """
    )
    cr.execute(create_table_query.format(**args))
    create_index_query = sql.SQL(
        """CREATE INDEX ON {table_name} ({column_left}, {column_right});"""
    )
    cr.execute(create_index_query.format(**args))
    fill_data_query = sql.SQL(
        """
        INSERT INTO {table_name} ({column_left}, {column_right})
        SELECT p.id, pi.base_pricelist_id
        FROM product_pricelist p
        JOIN product_pricelist_item pi ON p.id = pi.pricelist_id
        WHERE pi.base_pricelist_id IS NOT NULL;
        """
    )
    cr.execute(fill_data_query.format(**args))


def migrate(cr, version):
    _logger.info("Locking existing product.pricelist.cache jobs")
    lock_jobs(cr)
    _logger.info("Setup product_pricelist.parent_pricelist_ids")
    set_parent_pricelists(cr)
