# © 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import fields, models
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval

from odoo.addons.base.models.ir_ui_view import (
    transfer_modifiers_to_node,
    transfer_node_to_modifiers,
)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _default_commitment_date(self):
        if self.env.company.sale_commitment_date_required:
            return fields.Datetime.now()
        return False

    commitment_date_required = fields.Boolean(
        related="company_id.sale_commitment_date_required"
    )
    commitment_date = fields.Datetime(default=_default_commitment_date)

    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        # Overridden to set a 'required' modifier on 'commitment_date' field
        # based on the configuration.
        # It is done this way because the 'commitment_date_div' block on the
        # order form provided by the 'sale' addon is entirely replaced by the
        # 'sale_stock' addon.
        # This implementation will take care of adding the 'required' modifier
        # as soon as this field is rendered on the form.
        result = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if result["name"] == "sale.order.form":
            result["arch"] = self._fields_view_get_adapt_attrs(result["arch"])
        return result

    def _fields_view_get_adapt_attrs(self, view_arch):
        """Adapt the attrs of elements in the view."""
        doc = etree.XML(view_arch)
        self._add_commitment_date_attrs_required(doc)
        new_view = etree.tostring(doc, encoding="unicode")
        return new_view

    def _add_commitment_date_attrs_required(self, doc):
        xpath_expr = "//field[@name='commitment_date']"
        attrs_key = "required"
        nodes = doc.xpath(xpath_expr)
        for field in nodes:
            attrs = safe_eval(field.attrib.get("attrs", "{}"))
            required_domain = [("commitment_date_required", "=", True)]
            # Take into account existing 'required' attrs if any
            if attrs.get(attrs_key):
                required_domain = expression.OR([attrs[attrs_key], required_domain])
            attrs[attrs_key] = required_domain
            field.set("attrs", str(attrs))
            modifiers = {}
            transfer_node_to_modifiers(
                field, modifiers, self.env.context, current_node_path=["tree"]
            )
            transfer_modifiers_to_node(modifiers, field)
