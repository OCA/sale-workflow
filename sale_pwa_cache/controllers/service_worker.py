# Copyright 2021 Tecnativa - Alexandre D. Díaz
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.addons.web_pwa_cache.controllers.service_worker import ServiceWorker


class ServiceWorker(ServiceWorker):
    def _get_pwa_scripts(self):
        res = super()._get_pwa_scripts()
        res.append("/sale_pwa_cache/static/src/js/worker/systems/database.js")
        return res
