# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    required_identification = fields.Boolean(default=False)
    product_tmpl_category_ids = fields.One2many(
        "product.template.id_category", "product_tmpl_id"
    )

    @api.constrains("product_tmpl_category_ids")
    def _check_product_tmpl_category_ids(self):
        ProductTemplateIdCategory = self.env["product.template.id_category"]
        for product_templ in self:
            category_ids = ProductTemplateIdCategory.sudo()._read_group(
                [
                    ("product_tmpl_id", "=", product_templ.id),
                ],
                ["category_id"],
                ["category_id:count"],
                order="category_id:count DESC",
            )
            if category_ids and category_ids[0][1] > 1:
                category_ids = list(filter(lambda x: x[1] > 1, category_ids))
                raise ValidationError(
                    self.env._(
                        "There are repeated categories in the identifications "
                        "configuration, the quantities are shown below.\n%(categories)s"
                    )
                    % {
                        "categories": "\n".join(
                            f"{category[0].name}:\u2009{category[1]}"
                            for category in category_ids
                        )
                    }
                )

    def _eval_expression_identification(self, record=None):
        messages = []
        for product in self:
            failed_categories = self.env["product.template.id_category"]
            for prod_category in product.product_tmpl_category_ids:
                if not prod_category._eval_value(record or product):
                    failed_categories |= prod_category
            if failed_categories:
                categories = "\n".join(
                    self.env._("\u2003\u2022\u2009%(category)s%(details)s")
                    % {
                        "category": category.category_id.name,
                        "details": f" ({category.message})" if category.message else "",
                    }
                    for category in failed_categories
                )
                messages.append(
                    self.env._("\n%(product)s\n%(categories)s")
                    % {"product": product.name, "categories": categories}
                )
        if messages:
            raise ValidationError(
                self.env._(
                    "Some identifications were detected that could not be validated. "
                    "\nWe recommend reviewing your settings and the data you entered "
                    "to correct the problem. %(details)s"
                )
                % {"details": "".join(messages)}
            )
        return True
