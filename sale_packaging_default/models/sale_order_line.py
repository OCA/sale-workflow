# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, fields, models
from odoo.tools import str2bool


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_packaging_required = fields.Boolean(
        compute="_compute_is_packaging_required",
        store=True,
        readonly=True,
    )

    def onchange(self, values, field_name, field_onchange):
        """Record which field was being changed."""
        if isinstance(field_name, list):
            names = set(field_name)
        elif field_name:
            names = {field_name}
        else:
            names = set()
        _self = self.with_context(changing_fields=names)
        return super(SaleOrderLine, _self).onchange(values, field_name, field_onchange)

    @api.depends("product_id")
    def _compute_product_uom_id(self):
        """Set a default packaging (UoM) for sales if possible."""
        res = super()._compute_product_uom_id()
        for line in self:
            # If Odoo defaulted to the base UoM,
            # override it with the default packaging UoM
            if line.product_id and line.product_uom_id == line.product_id.uom_id:
                default_uom = line._get_default_packaging(line.product_id)
                if default_uom:
                    line.product_uom_id = default_uom
        return res

    def _get_sale_packagings(self):
        """Return valid sale packaging UoMs for the line's product."""
        self.ensure_one()
        if not self.product_id:
            return self.env["uom.uom"]
        if "sales" in self.env["uom.uom"]._fields:  # pragma: no cover
            return self.product_id.uom_ids.filtered_domain([("sales", "=", True)])
        return self.product_id.uom_ids

    @api.model
    def _get_default_packaging(self, product):
        """Find the first UoM marked for sales."""
        if not product:
            return self.env["uom.uom"]
        if "sales" in self.env["uom.uom"]._fields:  # pragma: no cover
            packagings = product.uom_ids.filtered_domain([("sales", "=", True)])
        else:
            packagings = product.uom_ids
        return packagings[:1]

    @api.depends("product_id.uom_ids", "company_id")
    def _compute_is_packaging_required(self):
        packaging_required_param = self.env["ir.config_parameter"].get_param(
            "sale_packaging_default.packaging_required", default="0"
        )
        is_required = str2bool(packaging_required_param)
        for record in self:
            if not is_required:
                record.is_packaging_required = False
                continue
            sale_packagings = record._get_sale_packagings()
            record.is_packaging_required = bool(sale_packagings)
