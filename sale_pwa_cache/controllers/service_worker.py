# Copyright 2021 Tecnativa - Alexandre D. Díaz
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo.http import request

from odoo.addons.web_pwa_cache.controllers.service_worker import ServiceWorker


class ServiceWorker(ServiceWorker):
    def _get_js_pwa_requires(self):
        res = """
            require('sale_pwa_cache.PWA');
        """
        res += super()._get_js_pwa_requires()
        return res

    def _get_pwa_scripts(self):
        res = super()._get_pwa_scripts()
        res.append("/sale_pwa_cache/static/src/js/worker/systems/database.js")
        res.append("/sale_pwa_cache/static/src/js/worker/managers/sync.js")
        res.append("/sale_pwa_cache/static/src/js/worker/pwa.js")
        return res

    def _get_pwa_params(self):
        res = super()._get_pwa_params()
        config_parameter_obj_sudo = request.env["ir.config_parameter"].sudo()
        res["is_sale_auto_confirm"] = config_parameter_obj_sudo.get_param(
            "pwa.sale.auto.confirm", default="True"
        )
        return res
