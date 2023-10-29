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


def update_queue_job_method_name(cr):
    query = """
        UPDATE queue_job_function qjf
        SET method = 'create_product_pricelist_cache'
        FROM ir_model_data ird
        WHERE ird.res_id = qjf.id
        AND ird.model = 'queue.job.function'
        AND ird.module = 'pricelist_cache'
        AND ird.name = 'job_function_pricelist_cache_update';
    """
    cr.execute(query)

def migrate(cr, version):
    _logger.info("Locking existing product.pricelist.cache jobs")
    lock_jobs(cr)
    _logger.info("Setup product_pricelist.parent_pricelist_ids")
    update_queue_job_method_name(cr)
