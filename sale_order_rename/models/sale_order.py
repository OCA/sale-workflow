# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2025 Openforce Srls Unipersonale (www.openforce.it)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.constrains("name")
    def _check_unique_name_in_company(self):
        so_obj = self.env["sale.order"]
        for so in self:
            domain = [
                ("name", "=", so.name),
                ("company_id", "=", so.company_id.id),
                ("id", "!=", so.id),
            ]
            if so_obj.search_count(domain):
                _logger.error(
                    "Sale Order name %(so_name)s exists for company:" " %(company)s",
                    {
                        "so_name": so.name,
                        "company": so.company_id.name,
                    },
                )
                raise UserError(_("Sale Order name must be unique within a company!"))
