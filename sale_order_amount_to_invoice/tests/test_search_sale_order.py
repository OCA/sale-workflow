# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.tests.common import TransactionCase


class test_search_sale_orders(TransactionCase):
    """
    """
    def _init_modules(self):
        self.m_model_data = self.registry("ir.model.data")
        self.m_proc = self.registry("procurement.order")
        self.m_product = self.registry("product.product")
        self.m_shop = self.registry("sale.shop")
        self.m_so = self.registry("sale.order")

    def _create_products(self):
        self.pack_id = self.m_product.create(
            self.cr, self.uid, {
                "name": "Test Case Product P",
                "procure_method": "make_to_stock",
                "supply_method": "produce",
                "type": "product",
            })
        self.product_id = self.m_product.create(
            self.cr, self.uid, {
                "name": "Test Unit Product P",
                "procure_method": "make_to_stock",
                "supply_method": "produce",
                "type": "product",
            })
        self.material_id = self.m_product.create(
            self.cr, self.uid, {
                "name": "Test Unit Raw Material",
                "procure_method": "make_to_stock",
                "supply_method": "buy",
            })

    def _ref(self, module, xmlid):
        return self.m_model_data.get_object_reference(self.cr, self.uid,
                                                      module, xmlid)[1]

    def setUp(self):
        super(test_move_splitting, self).setUp()
        self._init_modules()

        self.unit = self._ref("product", "product_uom_unit")

        self._create_products()

    def run_schedulers_three_times(self):
        for i in range(3):
            self.m_proc.run_scheduler(self.cr, self.uid)

    def create_pack_sale_order_and_procure(self, partner_id=None,
                                           partner_address=None):
        cr, uid = self.cr, self.uid
        partner_id = partner_id or self._ref("base", "res_partner_2")
        partner_add = partner_address or self._ref("base", "res_partner_address_3")

        sale_order = self.m_so.create(
            self.cr, self.uid,
            {"partner_id": partner_id,
             "partner_invoice_id": partner_add,
             "partner_shipping_id": partner_add,
             "pricelist_id": 1,
             "shop_id": self.shop_id,
             "order_line": [
                 (0, 0, {"product_id": self.pack_id,
                         "product_uom": self.unit,
                         "product_uom_qty": 10.0,
                         "price_unit": 10.0,
                         "name": "Product P"})],
             })

        self.m_so.action_button_confirm(cr, uid, [sale_order])
        self.run_schedulers_three_times()

    def test_propagate(self):
        self.create_pack_sale_order_and_procure()
        self.create_pack_sale_order_and_procure()
        self.create_pack_sale_order_and_procure()

        sale_orders = self.m_so.search(
            cr, uid, [('amount_to_invoice', '>', 0.0)]
        )

        self.assertNotEquals(sale_orders, [])
