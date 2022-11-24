#   @author Valentin CHEMIERE <valentin.chemiere@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_vals_lot_number(self, index_lot):
        # Prepare values before creating a lot number
        self.ensure_one()
        lot_number = "%s-%03d" % (self.order_id.name, index_lot)
        return {
            "name": lot_number,
            "product_id": self.product_id.id,
            "product_qty": self.product_uom_qty,
            "company_id": self.order_id.company_id.id,
        }

    def create_lot(self, index_lot=1):
        self.ensure_one()
        vals = self._prepare_vals_lot_number(index_lot)
        return self.env["stock.lot"].create(vals)

    @api.model_create_multi
    def create(self, values_list):
        for values in values_list:
            line = self.new(values)
            # we create a lot before create a line because the super method
            # must create a procurement and move
            if (
                line.order_id.state == "sale"
                and line.product_id.auto_generate_prodlot
                and not line.lot_id
                and line.product_id.tracking != "none"
            ):
                index_lot = line.order_id._get_max_lot_index() + 1
                lot_id = line.create_lot(index_lot)
                values["lot_id"] = lot_id.id
        return super().create(values_list)
