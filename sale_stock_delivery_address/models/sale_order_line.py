# Copyright 2020 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    dest_address_id = fields.Many2one(
        comodel_name="res.partner",
        string="Destination Address",
        help="If set this address will be the delivery address instead of the "
        "one specified in the Sales Order header.",
    )

    def _get_procurement_group_key(self):
        """ Return a key with priority to be used to regroup lines in multiple
        procurement groups. The higher the priority number is the more
        preference the criteria has.
        """
        priority = 15
        key = super(SaleOrderLine, self)._get_procurement_group_key()
        # Check priority
        if key[0] >= priority:
            return key
        if self.dest_address_id:
            return (priority, self.dest_address_id)
        return (priority, key)

    @api.onchange("dest_address_id")
    def _onchange_dest_address_id(self):
        if self.order_id.partner_id:
            domain = {
                "dest_address_id": [
                    "|",
                    ("id", "=", self.order_id.partner_id.id),
                    ("parent_id", "=", self.order_id.partner_id.id),
                ],
            }
        else:
            domain = {
                "dest_address_id": [],
            }
        return {"domain": domain}
