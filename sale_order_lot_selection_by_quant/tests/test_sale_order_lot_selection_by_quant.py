from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestSOLotSelectionByQuant(HttpCase):
    def setUp(self):
        super().setUp()
        self.warehouse = self.env.ref("stock.warehouse0")
        self.stock_quant_model = self.env["stock.quant"]
        self.stock_prod_lot_model = self.env["stock.production.lot"]
        self.prd_cable = self.env.ref("stock.product_cable_management_box")
        self.prd_cable.tracking = "lot"
        name = "TESTSOLQUANT"
        self.so = self.env["sale.order"].create(
            {
                "name": name,
                "user_id": self.env.ref("base.user_admin").id,
                "partner_id": self.env.ref("base.res_partner_3").id,
                "order_line": [(0, 0, {"product_id": self.prd_cable.id})],
            }
        )
        # Compatibility with sale_isolated_quotation
        if self.so.name != name:
            self.so.name = name

        self.lot = self.stock_prod_lot_model.create(
            {
                "name": "TEST-LOT",
                "product_id": self.prd_cable.id,
                "company_id": self.env.company.id,
            }
        )

        self.quant = self.stock_quant_model.create(
            {
                "product_id": self.prd_cable.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "lot_id": self.lot.id,
                "quantity": 10.0,
            }
        )

    def test_SO_lot_selection_by_quant(self):
        self.start_tour(
            "/web",
            "test_SO_lot_selection_by_quant",
            login="admin",
        )
