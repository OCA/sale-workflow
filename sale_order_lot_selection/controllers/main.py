# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.product.controllers.product_document import ProductDocumentController


class SaleOrderLotSelectionProductDocumentController(ProductDocumentController):
    def get_additional_create_params(self, **kwargs):
        super_values = super().get_additional_create_params(**kwargs)
        if kwargs.get("lot_id"):
            super_values.update(lot_id=kwargs.get("lot_id"))
        return super_values
