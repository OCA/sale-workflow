# Copyright 2023 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    picking_note = fields.Html(
        string="Picking Internal Note",
        help="The notes will be added to the sales order and pickings but will not be printed "
        "on the delivery slip.",
    )
    picking_customer_note = fields.Text(
        string="Picking Customer Comments",
        help="The notes will be added to the sales order and pickings and will be printed on "
        "the delivery slip.",
    )
