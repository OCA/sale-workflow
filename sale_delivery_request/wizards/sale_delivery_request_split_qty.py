from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleDeliveryRequestSplitQty(models.TransientModel):
    _name = "sale.delivery.request.split.qty"
    _description = "Split Delivery Request Line Quantity"

    delivery_request_line_id = fields.Many2one(
        comodel_name="sale.delivery.request.line",
        string="Request Line",
        required=True,
        ondelete="cascade",
    )
    original_qty = fields.Float(
        string="Original Quantity",
        digits="Product Unit of Measure",
        readonly=True,
    )
    split_qty = fields.Float(
        string="Quantity to Split",
        digits="Product Unit of Measure",
        required=True,
    )

    @api.constrains("split_qty", "original_qty")
    def _check_split_qty(self):
        for wiz in self:
            if wiz.split_qty <= 0:
                raise ValidationError(_("Split quantity must be greater than zero."))
            if wiz.split_qty >= wiz.original_qty:
                raise ValidationError(
                    _(
                        "Split quantity (%(split)s) must be less than "
                        "the original quantity (%(original)s).",
                        split=wiz.split_qty,
                        original=wiz.original_qty,
                    )
                )

    def action_split(self):
        self.ensure_one()
        line = self.delivery_request_line_id
        remaining = line.quantity - self.split_qty

        ctx_line = line.with_context(skip_qty_check=True)
        ctx_line.quantity = remaining

        later_lines = line.delivery_request_id.line_ids.filtered(
            lambda x, seq=line.sequence, lid=line.id: x.sequence > seq
            or (x.sequence == seq and x.id > lid)
        )
        if later_lines:
            for later in later_lines:
                later.sequence = later.sequence + 1

        self.env["sale.delivery.request.line"].with_context(skip_qty_check=True).create(
            {
                "delivery_request_id": line.delivery_request_id.id,
                "sale_order_line_id": line.sale_order_line_id.id,
                "quantity": self.split_qty,
                "sequence": line.sequence + 1,
            }
        )
        return {"type": "ir.actions.act_window_close"}


class SaleDeliveryRequestAssignDate(models.TransientModel):
    _name = "sale.delivery.request.assign.date"
    _description = "Assign Date to All Delivery Request Lines"

    delivery_request_id = fields.Many2one(
        comodel_name="sale.delivery.request",
        string="Delivery Request",
        required=True,
        ondelete="cascade",
    )
    promised_date = fields.Date(
        required=True,
    )

    def action_assign(self):
        self.ensure_one()
        self.delivery_request_id.line_ids.filtered(
            lambda x: not x.promised_date_absolute
        ).write({"promised_date_absolute": self.promised_date})
        return {"type": "ir.actions.act_window_close"}
