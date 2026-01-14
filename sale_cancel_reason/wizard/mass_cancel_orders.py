# © 2013 Guewen Baconnier, Camptocamp SA
# © 2022 Landoo Sistemas de Informacion SL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class SaleMassCancelOrders(models.TransientModel):
    _inherit = "sale.mass.cancel.orders"

    reason_id = fields.Many2one(
        "sale.order.cancel.reason", string="Reason", required=True
    )

    def action_mass_cancel(self):
        self.sale_order_ids.write({"cancel_reason_id": self.reason_id.id})
        return super().action_mass_cancel()
