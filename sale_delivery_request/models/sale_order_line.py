from odoo import _, fields, models
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    delivery_request_line_ids = fields.One2many(
        comodel_name="sale.delivery.request.line",
        inverse_name="sale_order_line_id",
        string="Delivery Request Lines",
    )
    commitment_date_from_dr = fields.Boolean(
        help="Indicates the commitment date was set by a delivery request "
        "and should not be manually changed.",
    )

    def _get_full_move_chain(self):
        """
        Return all stock moves in the full upstream move chain linked to this
        sale order line.

        ``move_ids`` only contains the moves directly linked via
        ``sale_line_id``. Upstream moves are linked via ``move_orig_ids``.
        ``_rollup_move_origs`` walks the full chain recursively.
        """
        self.ensure_one()
        all_move_ids = self.move_ids._rollup_move_origs()
        return self.env["stock.move"].browse(all_move_ids)

    def write(self, vals):
        if "commitment_date" in vals and not self.env.context.get(
            "from_delivery_request"
        ):
            locked = self.filtered("commitment_date_from_dr")
            if locked:
                raise UserError(
                    _(
                        "The commitment date on the following lines was set "
                        "by a delivery request and cannot be changed manually: %s",
                        ", ".join(locked.mapped("product_id.display_name")),
                    )
                )
        return super().write(vals)
