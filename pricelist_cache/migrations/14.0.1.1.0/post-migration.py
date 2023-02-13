# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import SUPERUSER_ID, api

logger = logging.getLogger(__name__)


def _update_job_function_method(env):
    old_method = "update_product_pricelist_cache"
    new_method = "create_product_pricelist_cache"
    function = env["queue.job.function"].search([("method", "=", old_method)])
    if function.exists():
        logger.info(f"rename queue function to {new_method}")
        function.method = new_method


def migrate(cursor, version):
    env = api.Environment(cursor, SUPERUSER_ID, {})
    _update_job_function_method(env)
