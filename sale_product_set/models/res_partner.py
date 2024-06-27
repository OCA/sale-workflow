# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import models
from odoo.tools import str2bool

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    def write(self, vals):
        res = super().write(vals)
        ir_config_param = self.env["ir.config_parameter"].sudo()

        if "active" in vals and str2bool(
            ir_config_param.get_param("sale_product_set.archive_partner_product_sets")
        ):
            partner_product_sets = (
                self.env["product.set"]
                .with_context(active_test=False)
                .search([("partner_id", "in", self.ids)])
            )
            partner_product_sets.sudo().write({"active": vals["active"]})
            _logger.debug(
                "product.set archive state changed to <active | inactive> for partners %s",
                ",".join(str(x) for x in self.ids),
            )
        return res
