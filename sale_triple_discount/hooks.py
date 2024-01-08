# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import logging

import pkg_resources

from odoo.modules.module import get_manifest

_logger = logging.getLogger(__name__)


def post_load():
    account_invoice_triple_discount_manifest = get_manifest(
        "account_invoice_triple_discount"
    )
    if not pkg_resources.parse_version(
        account_invoice_triple_discount_manifest["version"]
    ) >= pkg_resources.parse_version("16.0.2.0.0"):
        msg = (
            "Module sale_triple_discount requires module "
            "account_invoice_triple_discount >= 16.0.2.0.0"
        )
        _logger.error(msg)
        raise Exception(msg)
