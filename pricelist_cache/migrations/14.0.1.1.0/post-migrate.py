# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import datetime
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def cancel_locked_jobs(env):
    cancel_datetime = datetime.datetime.now()
    states = ("STARTED", "DONE", "CANCELLED", "FAILED")
    query = """
        UPDATE queue_job
        SET state = 'CANCELLED',
            date_cancelled = %(date_cancelled)s
        WHERE state in %(cancel_states)s
        AND model_name = 'product.pricelist.cache';
    """
    args = {
        "date_cancelled": cancel_datetime,
        "cancel_states": states,
    }
    env.cr.execute(query, args)


def reset_cache(env):
    cache_model = env["product.pricelist.cache"]
    cache_model.cron_reset_pricelist_cache()


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("Cancelling existing product.pricelist.cache jobs")
    cancel_locked_jobs(env)
    _logger.info("Resetting the pricelist cache")
    reset_cache(env)
