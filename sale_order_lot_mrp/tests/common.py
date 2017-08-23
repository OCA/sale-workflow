# -*- coding: utf-8 -*-
# © 2017 Today Akretion (http://www.akretion.com).
# @author  Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.addons.stock.tests import common2


class TestMrpLotCommon(common2.TestStockCommon):

    @classmethod
    def setUpClass(cls):
        super(TestMrpLotCommon, cls).setUpClass()

        cls.manufactureroute = \
            cls.env.ref('mrp.route_warehouse0_manufacture')
        cls.mto_route = \
            cls.env.ref('stock.route_warehouse0_mto')
        # Update demo products
        cls.workcenter_1 = cls.env['mrp.workcenter'].create({
            'name': 'Nuclear Workcenter',
            'capacity': 2,
            'time_start': 10,
            'time_stop': 5,
            'time_efficiency': 80,
        })
        cls.routing_1 = cls.env['mrp.routing'].create({
            'name': 'Simple Line',
        })
        cls.operation_1 = cls.env['mrp.routing.workcenter'].create({
            'name': 'Gift Wrap Maching',
            'workcenter_id': cls.workcenter_1.id,
            'routing_id': cls.routing_1.id,
            'time_cycle': 15,
            'sequence': 1,
        })
        vals = {
            'type': 'product',
            'sale_ok': True,
            'procure_method': 'make_to_order',
            'tracking': 'lot',
            'auto_generate_prodlot': True,
        }
        cls.product_1 = cls.env.ref('product.product_product_3')
        cls.product_2 = cls.env.ref('product.product_product_27')
        kit_vals = {
            'name': 'Kit of manifactured product',
            'categ_id': cls.env.ref('product.product_category_5').id,
            'standard_price': 3303,
            'list_price': 4000,
            'type': 'product',
            'sale_ok': True,
            'procure_method': 'make_to_order',
            'route_ids': [(6, 0, [cls.mto_route.id, cls.manufactureroute.id])],
            'tracking': 'lot',
            'auto_generate_prodlot': True,
        }

        cls.product_3 = cls.env['product.product'].create(kit_vals)
        cls.bom_1 = cls.env['mrp.bom'].create({
            'product_tmpl_id': cls.product_3.product_tmpl_id.id,
            'product_id': cls.product_3.id,
            'product_qty': 1,
            'product_uom': cls.product_3.uom_id.id,
            'type': 'phantom',
        })
        cls.env['mrp.bom.line'].create({
            'bom_id': cls.bom_1.id,
            'product_id': cls.product_1.id,
            'product_qty': 1,
            'product_uom': cls.product_1.uom_id.id,
        })
        cls.env['mrp.bom.line'].create({
            'bom_id': cls.bom_1.id,
            'product_id': cls.product_2.id,
            'product_qty': 1,
            'product_uom': cls.product_2.uom_id.id,
        })
        (cls.product_1 | cls.product_2 | cls.product_3).write(vals)
