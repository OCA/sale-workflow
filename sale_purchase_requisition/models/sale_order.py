# Copyright 2023 Moduon Team S.L. <info@moduon.team>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

PURCH_REQ_FROZEN_STATES = {"in_progress", "open", "done", "cancel"}


class SaleOrder(models.Model):
    _inherit = "sale.order"

    purchase_requisition_ids = fields.One2many(
        comodel_name="purchase.requisition",
        inverse_name="sale_id",
        string="Purchase requisitions",
    )
    open_purchase_requisition_count = fields.Integer(
        compute="_compute_opened_purchase_requisition_count",
        help="Number of purchase requisitions in open state",
        string="Open Purchase Requisitions",
    )
    purchase_requisition_sync_warning = fields.Char(
        compute="_compute_purchase_requisition_sync_warning",
        help="Warning message to be displayed when order lines "
        "are not synced with purchase requisitions",
    )

    def action_view_purchase_requisitions(self):
        """Return action to view purchase requisitions related to this sale order"""
        action = {
            "name": _("Purchase Requisition(s) for %s", self.name),
            "type": "ir.actions.act_window",
            "res_model": "purchase.requisition",
            "view_mode": "form",
            "context": {
                "search_default_draft": 1,
                "search_default_confirmed": 1,
                "search_default_done": 1,
            },
        }
        if len(self.purchase_requisition_ids) > 1:
            action["view_mode"] = "tree,form"
            action["domain"] = [("id", "in", self.purchase_requisition_ids.ids)]
        elif len(self.purchase_requisition_ids) == 1:
            action["res_id"] = self.purchase_requisition_ids.ids[0]
        return action

    def _prepare_purchase_requisition_lines(self):
        """Prepare purchase requisition lines data from sale order lines"""
        self.ensure_one()
        pur_req_lines = []
        for line in self.order_line:
            if line.product_id.purchase_ok:
                pur_req_lines.append(
                    [
                        0,
                        0,
                        {
                            "product_id": line.product_id.id,
                            "product_qty": line.product_uom_qty,
                            "product_uom_id": line.product_uom.id,
                            "line_order_id": line.id,
                        },
                    ]
                )
        return pur_req_lines

    def action_create_purchase_requisition(self):
        return {
            "name": _("Purchase Requisition for %s", self.name),
            "type": "ir.actions.act_window",
            "res_model": "purchase.requisition",
            "view_mode": "form",
            "context": {
                "default_sale_id": self.id,
                "default_line_ids": self._prepare_purchase_requisition_lines(),
                "default_origin": self.name,
                "default_user_id": False,
                "default_date_end": self.validity_date,
            },
        }

    def write(self, vals):
        pre_outsynced_prs = self._unsynced_prs()
        res = super().write(vals)
        if "order_line" not in vals:
            return res
        post_outsynced_prs = self._unsynced_prs()
        new_outsynced_prs = post_outsynced_prs - pre_outsynced_prs
        prl_model = self.env["purchase.requisition.line"]
        for sale in self:
            if sale.state not in {"draft", "sent"}:
                continue  # Order cannot modify purchase requisitions
            for sale_line in sale.order_line.filtered("product_id.purchase_ok"):
                # Step 1. Update purchase requisition lines
                for pr_line in sale_line.purchase_requisition_line_ids:
                    if pr_line.requisition_id.state in PURCH_REQ_FROZEN_STATES:
                        continue  # Purchase Requisition line cannot be modified
                    pr_line.sudo().write(
                        {
                            "product_id": sale_line.product_id.id,
                            "product_qty": sale_line.product_uom_qty,
                            "product_uom_id": sale_line.product_uom.id,
                        }
                    )
                # Step 2. Create new purchase requisition line if does not exist
                if not sale_line.purchase_requisition_line_ids:
                    editable_purch_reqs = sale.purchase_requisition_ids.filtered(
                        lambda pr: pr.state not in PURCH_REQ_FROZEN_STATES
                    )
                    for purchase_requisition in editable_purch_reqs:
                        prl_model.sudo().create(
                            {
                                "requisition_id": purchase_requisition.id,
                                "line_order_id": sale_line.id,
                                "product_id": sale_line.product_id.id,
                                "product_qty": sale_line.product_uom_qty,
                                "product_uom_id": sale_line.product_uom.id,
                            }
                        )
            # Create activity for purchase agent in the purchase.requisition
            # if this write sets it out-of-sync with the sale order
            for prid in self.purchase_requisition_ids.filtered(
                lambda x: x.state != "draft"
            ):
                if prid in new_outsynced_prs:
                    self.env["mail.activity"].sudo().create(
                        {
                            "activity_type_id": self.env.ref(
                                "mail.mail_activity_data_todo"
                            ).id,
                            "user_id": prid.user_id.id or prid.sale_user_id.id,
                            "res_id": prid.id,
                            "res_model_id": self.env.ref(
                                "purchase_requisition.model_purchase_requisition"
                            ).id,
                            "summary": _("Resolve differences with the sales order"),
                        }
                    )
        return res

    def action_cancel(self):
        """Cancel the sale order and cancel or close the purchase requisition."""
        res = super().action_cancel()
        purchase_requisitions = self.mapped("purchase_requisition_ids")
        purchase_requisitions.filtered(
            lambda pr: pr.state not in {"open", "done", "cancel"}
        ).action_cancel()
        purchase_requisitions.filtered(lambda pr: pr.state == "open").action_done()
        return res

    @api.returns("purchase.requisition", lambda value: value.id)
    def _unsynced_prs(self):
        """Get purchase requisitions that are out-of-sync with sale orders."""
        unsynced_prs = self.env["purchase.requisition"].browse()
        for sale in self:
            # Check if all products are in sale and purchase requisition
            so_p_ids = set(
                sale.order_line.mapped("product_id").filtered("purchase_ok").ids
            )
            for purchase_requisition in sale.purchase_requisition_ids:
                if so_p_ids ^ set(
                    purchase_requisition.line_ids.mapped("product_id").ids
                ):
                    # Symetric difference
                    unsynced_prs |= purchase_requisition
            # Check if quantities are the same in sale line and purchase requisition line
            lines_to_check = sale.order_line.filtered(
                # Exclude lines that cannot be purchase or already has unsynced prs
                lambda sol: sol.product_id.purchase_ok
                and sol.purchase_requisition_line_ids.requisition_id not in unsynced_prs
            )
            for line in lines_to_check:
                unsynced_prs |= line.purchase_requisition_line_ids.filtered(
                    # Convert quantity to the same UoM as the line
                    lambda prl: prl.requisition_id.state != "cancel"
                    and prl.product_uom_id._compute_quantity(
                        prl.product_qty, line.product_uom
                    )
                    != line.product_uom_qty
                ).mapped("requisition_id")
        return unsynced_prs

    def _compute_purchase_requisition_sync_warning(self):
        """Show warning message when order lines are not synced with purchase requisitions."""
        for sale in self:
            sale.update({"purchase_requisition_sync_warning": None})
            not_synced_prs = sale._unsynced_prs()
            if not_synced_prs:
                sale.purchase_requisition_sync_warning = _(
                    "Some lines are not synced on these Purchase Requisitions:"
                    " %s please update this lines manually",
                    ",".join(not_synced_prs.mapped("name")),
                )

    def _compute_opened_purchase_requisition_count(self):
        """Count the number of purchase requisitions that are not cancelled."""
        for sale in self:
            sale.open_purchase_requisition_count = len(
                sale.purchase_requisition_ids.filtered(lambda pr: pr.state != "cancel")
            )


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    purchase_requisition_line_ids = fields.One2many(
        comodel_name="purchase.requisition.line",
        inverse_name="line_order_id",
        string="Purchase requisition lines",
    )

    def unlink(self):
        """Delete purchase requisition lines when sale order line is deleted."""
        for sol in self.filtered(lambda l: l.purchase_requisition_line_ids):
            sol.purchase_requisition_line_ids.filtered(
                lambda prl: prl.requisition_id.state not in PURCH_REQ_FROZEN_STATES
            ).unlink()
        return super().unlink()
