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

    def create_prodlot(self, index_lot=1):
        self.ensure_one()
        vals = self._prepare_vals_lot_number(index_lot)
        return self.env["stock.production.lot"].create(vals)

    @api.model
    def create(self, values):
        line = self.new(values)
        # we create a lot before create a line because the super method
        # must create a procurement and move
        if (
            line.order_id.state == "sale"
            and line.product_id.auto_generate_prodlot
            and not line.lot_id
            and line.product_id.tracking != "none"
        ):
            # when a new line is added to confirmed sale order
            # get the max index_lot from the other lines
            index_lot = 0
            lot_ids = line.order_id.order_line.filtered(lambda l: l.lot_id).mapped(
                "lot_id"
            )
            for lot in lot_ids:
                lot_name = lot.name
                index_str = lot_name.replace(line.order_id.name + "-", "")
                last_index = int(index_str) if index_str.isdigit() else 0
                index_lot = max(index_lot, last_index)
            index_lot += 1
            lot_id = line.create_prodlot(index_lot)
            values["lot_id"] = lot_id.id
        line = super().create(values)
        return line
