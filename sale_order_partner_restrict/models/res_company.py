# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_order_partner_restrict = fields.Selection(
        [
            ("all", "All partners"),
            ("only_parents", "Only parent accounts (no contacts)"),
            ("parents_and_contacts", "Parent accounts and contacts"),
        ],
        "Partner Restriction on Sale Orders",
        default="all",
    )
