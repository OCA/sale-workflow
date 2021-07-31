# Copyright 2014-2021 Akretion France (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2016-2021 Sodexis (http://sodexis.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CreateRentalProduct(models.TransientModel):
    _name = "create.rental.product"
    _description = "Create the Rental Service Product"

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get("active_model") == "product.product":
            hw_product = self.env["product.product"].browse(
                self.env.context["active_id"]
            )
        elif self.env.context.get("active_model") == "product.template":
            hw_product_tmpl = self.env["product.template"].browse(
                self.env.context["active_id"]
            )
            assert len(hw_product_tmpl.product_variant_ids) == 1
            hw_product = hw_product_tmpl.product_variant_ids
        else:
            raise UserError(_("Wrong active_model. Should never happen."))
        hw_product = hw_product.with_context(display_default_code=False)
        res.update(
            {
                "hw_product_id": hw_product.id,
                "name": _("Rental of a %s") % hw_product.display_name,
            }
        )
        if hw_product.default_code:
            res["default_code"] = _("RENT-%s") % hw_product.default_code
        return res

    hw_product_id = fields.Many2one(
        "product.product", string="Product to Rent", readonly=True, required=True
    )
    name = fields.Char(string="Rental Service Name", required=True)
    default_code = fields.Char(string="Default Code")
    sale_price_per_day = fields.Float(
        string="Rental Price per Day",
        required=True,
        digits="Product Price",
        default=1.0,
    )
    categ_id = fields.Many2one(
        "product.category", string="Product Category", required=True
    )
    copy_image = fields.Boolean(string="Copy Product Image")

    @api.model
    def _prepare_rental_product(self):
        day_uom_id = self.env.ref("uom.product_uom_day").id
        vals = {
            "type": "service",
            "sale_ok": True,
            "purchase_ok": False,
            "uom_id": day_uom_id,
            "uom_po_id": day_uom_id,
            "list_price": self.sale_price_per_day,
            "name": self.name,
            "default_code": self.default_code,
            "rented_product_id": self.hw_product_id.id,
            "must_have_dates": True,
            "categ_id": self.categ_id.id,
            "invoice_policy": "order",
        }
        if self.copy_image:
            vals["image_1920"] = self.hw_product_id.image_1920
        return vals

    def create_rental_product(self):
        self.ensure_one()
        pp_obj = self.env["product.product"]
        #  check that a rental product doesn't already exists ?
        product = pp_obj.create(self._prepare_rental_product())
        action = {
            "name": pp_obj._description,
            "type": "ir.actions.act_window",
            "res_model": pp_obj._name,
            "view_mode": "form,tree,kanban",
            "nodestroy": False,  # Close the wizard pop-up
            "target": "current",
            "res_id": product.id,
        }
        return action
