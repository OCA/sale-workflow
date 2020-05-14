# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Copyright 2020 Tecnativa - Pedro M. Baeza
# Copyright 2020 Druidoo - Iván Todorovich

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    type_id = fields.Many2one(
        comodel_name="sale.order.type",
        string="Type",
        compute="_compute_type_id",
        readonly=False,
        store=True,
    )
    warehouse_id = fields.Many2one(
        compute="_compute_warehouse_id", store=True, readonly=False,
    )
    picking_policy = fields.Selection(
        compute="_compute_picking_policy", store=True, readonly=False,
    )
    payment_term_id = fields.Many2one(
        compute="_compute_payment_term_id", store=True, readonly=False,
    )
    pricelist_id = fields.Many2one(
        compute="_compute_pricelist_id", store=True, readonly=False,
    )
    incoterm = fields.Many2one(compute="_compute_incoterm", store=True, readonly=False)

    @api.depends("partner_id", "company_id")
    def _compute_type_id(self):
        for record in self:
            if not record.partner_id:
                record.sale_type_id = self.env["sale.order.type"].search([], limit=1)
            else:
                sale_type = (
                    record.partner_id.with_context(
                        force_company=record.company_id.id
                    ).sale_type
                    or self.partner_id.commercial_partner_id.with_context(
                        force_company=record.company_id.id
                    ).sale_type
                )
                if sale_type:
                    record.type_id = sale_type

    @api.depends("type_id")
    def _compute_warehouse_id(self):
        if hasattr(super(), "_compute_warehouse_id"):
            super()._compute_warehouse_id()
        for rec in self:
            if rec.type_id.warehouse_id:
                rec.warehouse_id = rec.type_id.warehouse_id

    @api.depends("type_id")
    def _compute_picking_policy(self):
        if hasattr(super(), "_compute_picking_policy"):
            super()._compute_picking_policy()
        for rec in self:
            if rec.type_id.picking_policy:
                rec.picking_policy = rec.type_id.picking_policy

    @api.depends("type_id")
    def _compute_payment_term_id(self):
        if hasattr(super(), "_compute_payment_term_id"):
            super()._compute_payment_term_id()
        for rec in self:
            if rec.type_id.payment_term_id:
                rec.payment_term_id = rec.type_id.payment_term_id

    @api.depends("type_id")
    def _compute_pricelist_id(self):
        if hasattr(super(), "_compute_pricelist_id"):
            super()._compute_pricelist_id()
        for rec in self:
            if rec.type_id.pricelist_id:
                rec.pricelist_id = rec.type_id.pricelist_id

    @api.depends("type_id")
    def _compute_incoterm(self):
        if hasattr(super(), "_compute_incoterm"):
            super()._compute_incoterm()
        for rec in self:
            if rec.type_id.incoterm_id:
                rec.incoterm = rec.type_id.incoterm_id

    @api.model
    def create(self, vals):
        if vals.get("name", "/") == "/" and vals.get("type_id"):
            sale_type = self.env["sale.order.type"].browse(vals["type_id"])
            if sale_type.sequence_id:
                vals["name"] = sale_type.sequence_id.next_by_id()
        return super(SaleOrder, self).create(vals)

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        if self.type_id.journal_id:
            res["journal_id"] = self.type_id.journal_id.id
        if self.type_id:
            res["sale_type_id"] = self.type_id.id
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    route_id = fields.Many2one(compute="_compute_route_id", store=True, readonly=False)

    @api.depends("order_id.type_id")
    def _compute_route_id(self):
        if hasattr(super(), "_compute_route_id"):
            super()._compute_route_id()
        for rec in self:
            rec.route_id = rec.order_id.type_id.route_id
