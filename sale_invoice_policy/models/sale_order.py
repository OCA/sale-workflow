# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2021 Digital5, S.L. (<https://digital5.es>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    invoice_policy = fields.Selection(
        [
            ("order", "Invoice what is ordered"),
            ("delivery", "Invoice what is delivered"),
        ],
        string="Invoicing Policy",
        readonly=True,
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]},
        help="Ordered Quantity: Invoice quantities ordered by the customer.\n"
        "Delivered Quantity: Invoice quantities delivered to the customer.",
    )
