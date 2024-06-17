from odoo import _, api, exceptions, fields, models
from odoo.tools import groupby


class SaleOrderBlockWizard(models.TransientModel):
    _name = "sale.order.block.wizard"
    _description = "Sale Order Block Wizard"
    _transient_max_hours = 0.25  # 15 minutes until destroyed

    sale_line_block_ids = fields.One2many(
        comodel_name="sale.order.block.wizard.line",
        inverse_name="wizard_id",
        string="Sale Block Lines",
    )
    confirmation_allowed = fields.Boolean(
        string="Allowed to confirm",
        compute="_compute_confirmation_allowed",
    )
    is_uom_adjustable = fields.Boolean(
        compute="_compute_is_adjustable",
        store=True,
        readonly=True,
        compute_sudo=True,
    )
    is_packaging_adjustable = fields.Boolean(
        compute="_compute_is_adjustable",
        store=True,
        readonly=True,
        compute_sudo=True,
    )

    @api.depends_context("uid")
    @api.depends("sale_line_block_ids.company_id")
    def _compute_confirmation_allowed(self):
        """Compute if the user is allowed to confirm the sale orders."""
        self.confirmation_allowed = (
            self.env.user
            in self.sale_line_block_ids.company_id.sale_line_block_allowed_groups.users
        )

    @api.depends(
        "sale_line_block_ids.product_packaging_allowed_max_qty",
        "sale_line_block_ids.product_uom_allowed_max_qty",
    )
    def _compute_is_adjustable(self):
        """Compute if the sale lines are adjustable."""
        for record in self:
            lines = record.mapped("sale_line_block_ids")
            record.is_packaging_adjustable = bool(
                lines.filtered(lambda l: l.product_packaging_allowed_max_qty > 0.0)
            )
            record.is_uom_adjustable = bool(
                lines.filtered(lambda l: l.product_uom_allowed_max_qty > 0.0)
            )

    def confirm(self):
        """Confirm the sale orders ignoring next possible wizards."""
        if not all(self.mapped("confirmation_allowed")):
            raise exceptions.UserError(
                _("You are not allowed to confirm these orders.")
            )
        orders = self.mapped("sale_line_block_ids.order_id")
        orders.message_post(
            body=_("Order confirmed with errors by %s.", self.env.user.name),
            subtype_id=self.env.ref("mail.mt_note").id,
        )
        return orders.with_context(skip_block_no_stock_check=True).action_confirm()

    def action_adjust_uom_quantity(self):
        """Adjust the quantity of the sale lines to the maximum allowed by the UoM."""
        return self.sale_line_block_ids._action_adjust_uom_quantity()

    def action_adjust_packaging_quantity(self):
        """Adjust the quantity of the sale lines to the maximum allowed by the packaging."""
        return self.sale_line_block_ids._action_adjust_packaging_quantity()

    def action_move_to_new_order(self):
        """Move the sale lines to a new sale order."""
        return self.sale_line_block_ids._action_move_to_new_order()

    @api.constrains("sale_line_block_ids")
    def _check_sale_line_block_ids(self):
        """Check that all sale lines are from the same company."""
        for record in self:
            companies = record.mapped(
                "sale_line_block_ids.sale_line_id.order_id.company_id"
            )
            if len(companies) > 1:
                raise exceptions.UserError(
                    _("Cannot launch wizard from sale orders from different companies.")
                )


class SaleOrderBlockWizardLine(models.TransientModel):
    _name = "sale.order.block.wizard.line"
    _description = "Sale Order Block Wizard Line"
    _transient_max_hours = 0.25  # 15 minutes until destroyed

    wizard_id = fields.Many2one(
        comodel_name="sale.order.block.wizard",
        string="Wizard",
        required=True,
    )
    sale_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Sale Line",
        required=True,
    )
    company_id = fields.Many2one(
        related="sale_line_id.order_id.company_id",
        string="Company",
        readonly=True,
        store=True,
    )
    order_id = fields.Many2one(
        related="sale_line_id.order_id",
        string="Sale Order",
        readonly=True,
        store=True,
    )
    product_id = fields.Many2one(
        related="sale_line_id.product_id",
        string="Product",
        readonly=True,
        store=True,
    )
    product_uom_qty = fields.Float(
        related="sale_line_id.product_uom_qty",
        string="Qty. (UoM)",
        readonly=True,
    )
    product_uom = fields.Many2one(
        related="sale_line_id.product_uom",
        string="UoM",
        readonly=True,
        store=True,
    )
    product_uom_allowed_max_qty = fields.Float(
        string="Max. Qty. (UoM)",
        compute="_compute_allowed_max_qty",
        readonly=True,
        store=True,
        compute_sudo=True,
    )
    product_packaging_qty = fields.Float(
        related="sale_line_id.product_packaging_qty",
        string="Qty. (Pkg.)",
        readonly=True,
        store=True,
    )
    product_packaging_id = fields.Many2one(
        related="sale_line_id.product_packaging_id",
        string="Packaging",
        readonly=True,
        store=True,
    )
    product_packaging_allowed_max_qty = fields.Float(
        string="Max. Qty. (Pkg.)",
        compute="_compute_allowed_max_qty",
        readonly=True,
        store=True,
        compute_sudo=True,
    )

    @api.depends("sale_line_id", "product_uom_qty", "company_id.sale_line_field_block")
    def _compute_allowed_max_qty(self):
        """Compute the maximum allowed quantity by UoM and Packaging of storable products."""
        self.product_uom_allowed_max_qty = 0.0
        self.product_packaging_allowed_max_qty = 0.0
        for record in self:
            field_to_check = record.company_id.sale_line_field_block
            if not field_to_check:
                self.env.cr.postcommit.add(record.unlink)
                continue
            if record.sale_line_id.product_type != "product":
                self.env.cr.postcommit.add(record.unlink)
                continue
            allowed_max_qty = record.sale_line_id[field_to_check.name]
            if (
                allowed_max_qty > 0
                and record.sale_line_id.product_uom_qty <= allowed_max_qty
            ):
                self.env.cr.postcommit.add(record.unlink)
                continue
            record.product_uom_allowed_max_qty = allowed_max_qty
            if record.product_packaging_id:
                record.product_packaging_allowed_max_qty = (
                    allowed_max_qty // record.product_packaging_id.qty
                )

    def _get_adjustable_records(self, packaging=False):
        """Return the records that can be adjusted by UoM or Packaging."""
        if packaging:
            return self.filtered(
                lambda r: r.product_packaging_allowed_max_qty > 0.0
                and r.product_packaging_qty > r.product_packaging_allowed_max_qty
            )
        return self.filtered(
            lambda r: r.product_uom_allowed_max_qty > 0.0
            and r.product_uom_qty > r.product_uom_allowed_max_qty
        )

    def _get_reopen_action(self):
        """Return the action to reopen the wizard."""
        action = (
            self.env.ref("sale_block_no_stock.sale_order_block_wizard_action")
            .sudo()
            .read()[0]
        )
        action["context"] = {
            "default_sale_line_block_ids": [
                (0, 0, {"sale_line_id": line.id})
                for line in self.mapped("sale_line_id")
            ]
        }
        return action

    def _action_move_to_new_order(self):
        """Move the sale lines to a new sale order."""
        mt_note_id = self.env.ref("mail.mt_note").id
        partner_id = self.env.user.partner_id.id
        new_orders = self.env["sale.order"].browse()
        for order, records in groupby(self, lambda r: r.order_id):
            new_order = order.copy(default={"order_line": None})
            new_order.message_post_with_view(
                "mail.message_origin_link",
                values={"self": new_order, "origin": order, "edit": True},
                subtype_id=mt_note_id,
                author_id=partner_id,
            )
            for record in records:
                record.sale_line_id.write({"order_id": new_order.id})
            new_orders |= new_order
        return new_orders

    def _action_adjust_uom_quantity(self):
        """Adjust the quantity of the sale lines to the maximum allowed by the UoM."""
        adjustable_records = self._get_adjustable_records()
        for record in adjustable_records:
            record.sale_line_id.product_uom_qty = record.product_uom_allowed_max_qty
        if not self - adjustable_records:
            return
        return (self - adjustable_records)._get_reopen_action()

    def _action_adjust_packaging_quantity(self):
        """Adjust the quantity of the sale lines to the maximum allowed by the packaging."""
        adjustable_records = self._get_adjustable_records(packaging=True)
        for record in adjustable_records:
            record.sale_line_id.product_packaging_qty = (
                record.product_packaging_allowed_max_qty
            )
            record.sale_line_id.product_uom_qty = (
                record.product_packaging_id.qty
                * record.product_packaging_allowed_max_qty
            )
        if not self - adjustable_records:
            return
        return (self - adjustable_records)._get_reopen_action()
