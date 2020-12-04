# Copyright 2020 Tecnativa - Alexandre D. Díaz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.web_pwa_oca.controllers.main import PWA


class PWA(PWA):
    def _get_pwa_params(self):
        res = super()._get_pwa_params()
        res["prefetched_urls"] += [
            "/web_widget_one2many_product_picker/static/src/xml/one2many_product_picker_quick_create.xml",
        ]
        return res
