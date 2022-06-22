# Copyright 2014 Guewen Baconnier (Camptocamp SA)
# Copyright 2013-2014 Nicolas Bessi (Camptocamp SA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleTermsTemplate(models.Model):
    _name = "sale.terms_template"
    _description = "Sale terms template"

    active = fields.Boolean(default=True)

    name = fields.Char(
        string="Name",
        required=True,
    )

    text = fields.Html(
        string="Terms template",
        translate=True,
    )

    def get_value(self, sale_order, add_context=None, post_process=True):
        """Get sales terms from template.

        Like in mail composer `text` template can use jinja or qweb syntax.

        if `partner_id` is provide, it will retreive it's lang to use the
        right translation.

        Then template is populated with model/res_id attributes according
        jinja/qweb instructions.

        :param sale_order: recordset (browsed) sale order
        :param add_context: context forwarded to the templating engine
        :param post_process: what ever to use `post_process` from the templating
                             engine. If `True` urls are transform to absolute urls
        """
        self.ensure_one()
        sale_order.ensure_one()
        lang = sale_order.partner_id.lang if sale_order.partner_id else None
        return self.env["mail.render.mixin"]._render_template(
            self.with_context(lang=lang).text,
            "sale.order",
            [sale_order.id],
            engine="jinja",
            add_context=add_context,
            post_process=post_process,
        )[sale_order.id]
