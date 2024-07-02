# Copyright 2023 ForgeFlow S.L.
# Copyright 2024 OERP Canada <https://www.oerp.ca>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    auto_cancel_expired_so = fields.Boolean(
        string="Auto Cancel Expired SaleOrder",
        default=True,
        help="If unchecked, you will be able to restrict \n"
        "this contact's expired SO from being auto-canceled.",
    )
