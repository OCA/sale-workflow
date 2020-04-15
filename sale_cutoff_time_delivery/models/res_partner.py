# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "time.cutoff.mixin"]

    order_delivery_cutoff_preference = fields.Selection(
        [
            ("warehouse_cutoff", "Use global (warehouse) cutoff time"),
            ("partner_cutoff", "Use partner's cutoff time"),
        ],
        string="Delivery orders cutoff preference",
        default="warehouse_cutoff",
        required=True,
        help="Define the cutoff time for delivery orders:\n\n"
        "* Use global (warehouse) cutoff time: Delivery order for sale orders"
        " will be postponed to the next warehouse cutoff time\n"
        "* Use partner's cutoff time: Delivery order for sale orders"
        " will be postponed to the next partner's cutoff time\n\n"
        "Example: If cutoff is set to 09:00, any sale order confirmed before "
        "09:00 will have its delivery order postponed to 09:00, and any sale "
        "order confirmed after 09:00 will have its delivery order postponed "
        "to 09:00 on the following day.",
    )

    def get_cutoff_time(self):
        res = super().get_cutoff_time()
        res["tz"] = self.tz
        return res
