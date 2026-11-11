# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command, api, fields, models


class SplitOrderLineWizard(models.TransientModel):
    _name = "split.order.line.wizard"
    _description = "Wizard to split Order Line"

    line_ids = fields.One2many(
        "split.order.line.wizard.line",
        "wizard_id",
        string="Preview Lines",
    )

    def _prepare_line(self, order_line, qty, packaging, items_ids):
        items_ids = items_ids.filtered(lambda r: r.product_id == order_line.product_id)
        if packaging:
            items_id = items_ids.filtered(lambda r: r.packaging_id == packaging)
        else:
            items_id = items_ids.filtered(lambda r: not r.packaging_id)

        return Command.create(
            {
                "product_id": order_line.product_id.id,
                "packaging_id": packaging.id if packaging else False,
                "product_uom_qty": qty,
                "price_unit": items_id.fixed_price if items_id else 0,
            }
        )

    @api.model
    def default_get(self, fields):
        vals = super().default_get(fields)

        order_line = self.env["sale.order.line"].browse(self.env.context["active_id"])
        order_id = order_line.order_id
        lines = []

        packaging = order_line.product_packaging_id
        total_qty = order_line.product_uom_qty

        qty = int(total_qty / packaging.qty) * packaging.qty
        remaining_qty = total_qty - qty
        items_ids = order_id.pricelist_id.item_ids
        lines.append(self._prepare_line(order_line, qty, packaging, items_ids))

        packaging_ids = (
            order_id.pricelist_id.item_ids.filtered(
                lambda r: r.product_id == order_line.product_id
            ).packaging_id
            - packaging
        )

        for pkg in packaging_ids:
            qty = int(remaining_qty / pkg.qty) * pkg.qty
            if qty > 0:
                lines.append(self._prepare_line(order_line, qty, pkg, items_ids))
                remaining_qty -= qty

        if remaining_qty:
            lines.append(
                self._prepare_line(order_line, remaining_qty, False, items_ids)
            )

        vals["line_ids"] = lines
        return vals

    def action_confirm(self):
        self.ensure_one()

        original_line = self.env["sale.order.line"].browse(
            self.env.context["active_id"]
        )
        order_id = original_line.order_id
        line = self.line_ids.filtered(
            lambda r: r.packaging_id == original_line.product_packaging_id
        )
        original_line.write(
            {
                "product_uom_qty": line.product_uom_qty,
            }
        )
        line_ids = self.line_ids - line

        for line in line_ids:
            original_line.copy(
                {
                    "order_id": order_id.id,
                    "product_uom_qty": line.product_uom_qty,
                    "product_packaging_id": line.packaging_id.id,
                    "price_unit": line.price_unit,
                }
            )


class SplitOrderLineWizardLine(models.TransientModel):
    _name = "split.order.line.wizard.line"
    _description = "Split Order Line Wizard Line"

    wizard_id = fields.Many2one(
        "split.order.line.wizard",
        required=True,
        ondelete="cascade",
    )

    product_id = fields.Many2one("product.product")
    packaging_id = fields.Many2one("product.packaging")
    product_uom_qty = fields.Float()
    price_unit = fields.Float()
