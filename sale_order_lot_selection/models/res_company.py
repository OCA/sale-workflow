# Copyright (C) 2024 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    allow_to_change_lot_on_confirmed_so = fields.Boolean(
        "Allow to change lot on confirmed sale order",
        help="If checked, it will allow to change the lot on the confirmed sale order.",
    )
