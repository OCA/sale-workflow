# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    # Price was based on commitment/delivery date by default before, so enable
    # the new option on all pricelists.
    if not version:
        return
    _logger.info("Enable price based on delivery date for all pricelists...")
    env = api.Environment(cr, SUPERUSER_ID, {})
    pricelists = env["product.pricelist"].search([])
    pricelists.write({"price_based_on_delivery_date": True})
