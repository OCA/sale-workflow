from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class SaleDeliveryRequestLine(models.Model):
    _name = "sale.delivery.request.line"
    _description = "Delivery Request Line"
    _order = "sequence, id"

    delivery_request_id = fields.Many2one(
        comodel_name="sale.delivery.request",
        string="Delivery Request",
        required=True,
        ondelete="cascade",
        index=True,
    )
    sale_order_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Sale Order Line",
        required=True,
        ondelete="cascade",
    )
    sale_order_id = fields.Many2one(
        related="delivery_request_id.sale_order_id",
        store=True,
    )
    state = fields.Selection(
        related="delivery_request_id.state",
        store=True,
    )
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one(
        related="sale_order_line_id.product_id",
        store=True,
    )
    product_uom = fields.Many2one(
        related="sale_order_line_id.product_uom",
    )
    quantity = fields.Float(
        digits="Product Unit of Measure",
        required=True,
    )
    sol_remaining_qty = fields.Float(
        string="Remaining Qty",
        compute="_compute_sol_remaining_qty",
        digits="Product Unit of Measure",
        help="Total remaining quantity on the sale order line "
        "minus quantities already assigned in other request lines.",
    )
    promised_date_absolute = fields.Date(
        string="Promised Date",
        help="Date entered by Planning. Stored for reference. "
        "The actual delivery date is recalculated at SO confirmation.",
        copy=False,
    )
    business_days_offset = fields.Integer(
        help="Number of business days between request date and "
        "the promised absolute date. Used to recalculate the "
        "final promised date at SO confirmation.",
        copy=False,
    )
    can_be_merged = fields.Boolean(
        compute="_compute_can_be_merged",
        store=True,
    )

    @api.depends("delivery_request_id.line_ids.sale_order_line_id")
    def _compute_can_be_merged(self):
        for line in self:
            sol = line.sale_order_line_id
            line_id = line.id
            siblings = line.delivery_request_id.line_ids.filtered(
                lambda x, sol=sol, line_id=line_id: x.sale_order_line_id == sol
                and x.id != line_id
            )
            line.can_be_merged = bool(siblings)

    @api.depends(
        "sale_order_line_id.product_uom_qty",
        "sale_order_line_id.qty_delivered",
    )
    def _compute_sol_remaining_qty(self):
        for line in self:
            sol = line.sale_order_line_id
            if sol:
                line.sol_remaining_qty = sol.product_uom_qty - sol.qty_delivered
            else:
                line.sol_remaining_qty = 0.0

    @api.constrains("quantity")
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_("Quantity must be greater than zero."))

    @api.constrains("quantity", "sale_order_line_id", "delivery_request_id")
    def _check_total_quantity(self):
        """
        Ensure total quantity across all request lines for the same
        sale order line does not exceed the remaining quantity.
        """
        for line in self:
            sol = line.sale_order_line_id
            request = line.delivery_request_id
            if not sol or not request:
                continue
            same_sol_lines = request.line_ids.filtered_domain(
                [
                    ("sale_order_line_id", "=", sol.id),
                ]
            )
            total_qty = sum(same_sol_lines.mapped("quantity"))
            remaining = sol.product_uom_qty - sol.qty_delivered
            precision = self.env["decimal.precision"].precision_get(
                "Product Unit of Measure"
            )
            if round(total_qty - remaining, precision) > 0:
                raise ValidationError(
                    _(
                        "Total requested quantity (%(total)s) for "
                        "product '%(product)s' exceeds the remaining "
                        "quantity (%(remaining)s) on the sale order line.",
                        total=total_qty,
                        product=sol.product_id.display_name,
                        remaining=remaining,
                    )
                )

    def action_split_quantity(self):
        """
        Open the split quantity wizard.
        """
        self.ensure_one()
        if self.state != "pending":
            raise UserError(_("You can only split lines in pending requests."))
        return {
            "name": _("Split Quantity"),
            "type": "ir.actions.act_window",
            "res_model": "sale.delivery.request.split.qty",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_delivery_request_line_id": self.id,
                "default_original_qty": self.quantity,
            },
        }

    def action_merge_lines(self):
        """
        Merge this line back into its siblings that share the same
        sale order line within the same delivery request.
        """
        self.ensure_one()
        if self.state != "pending":
            raise UserError(_("You can only merge lines in pending requests."))
        siblings = self.delivery_request_id.line_ids.filtered(
            lambda x: x.sale_order_line_id == self.sale_order_line_id
        )
        if len(siblings) < 2:
            raise UserError(_("No sibling lines to merge with."))
        # Keep the first line (by sequence/id), sum quantities, remove the rest
        keep = siblings[0]
        total_qty = sum(siblings.mapped("quantity"))
        (siblings - keep).unlink()
        keep.write(
            {
                "quantity": total_qty,
                "promised_date_absolute": False,
            }
        )
        return True
