diff --git a/addons/product_visible_discount/product_visible_discount.py b/addons/product_visible_discount/product_visible_discount.py
index 33d777f..2097794 100644
--- a/addons/product_visible_discount/product_visible_discount.py
+++ b/addons/product_visible_discount/product_visible_discount.py
@@ -42,7 +42,7 @@ class sale_order_line(osv.osv):
             lang=False, update_tax=True, date_order=False, packaging=False,
             fiscal_position=False, flag=False, context=None):
 
-        def get_real_price(res_dict, product_id, qty, uom, pricelist):
+        def get_real_price(res_dict, product_id, qty, uom, pricelist, context=None):
             """Retrieve the price before applying the pricelist"""
             item_obj = self.pool.get('product.pricelist.item')
             price_type_obj = self.pool.get('product.price.type')
@@ -61,14 +61,34 @@ class sale_order_line(osv.osv):
             if uom and uom != product.uom_id.id:
                 # the unit price is in a different uom
                 factor = self.pool['product.uom']._compute_qty(cr, uid, uom, 1.0, product.uom_id.id)
-            return product_read[field_name] * factor
+            res = product_read[field_name] * factor
+            if context is None:
+                context = {}
+            if context.get('fiscal_position_id') and res:
+                fp = self.pool['account.fiscal.position'].browse(
+                    cr, uid, context.get('fiscal_position_id'), context=context)
+                pricet_ids = price_type_obj.search(
+                    cr, uid, [('field', '=', field_name)], context=context)
+                assert pricet_ids, 'Missing product.price.type'
+                pricet = price_type_obj.browse(cr, uid, pricet_ids[0], context=context)
+                if fp.price_include_taxes != pricet.price_include_taxes:
+                    taxres = self.pool['account.tax'].compute_all(
+                        cr, uid, product.taxes_id, res, 1)
+                    if pricet.price_include_taxes:
+                        res = taxres['total']
+                    else:
+                        res = taxres['total_included']
+            return res
 
 
         res=super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty,
             uom, qty_uos, uos, name, partner_id,
             lang, update_tax, date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, context=context)
 
-        context = {'lang': lang, 'partner_id': partner_id}
+        if context is None:
+            context = {}
+        context_partner = context.copy()
+        context_partner.update({'lang': lang, 'partner_id': partner_id})
         result=res['value']
         pricelist_obj=self.pool.get('product.pricelist')
         product_obj = self.pool.get('product.product')
@@ -78,18 +98,18 @@ class sale_order_line(osv.osv):
             else:
                 return res
             uom = result.get('product_uom', uom)
-            product = product_obj.browse(cr, uid, product, context)
-            pricelist_context = dict(context, uom=uom, date=date_order)
+            product = product_obj.browse(cr, uid, product, context=context_partner)
+            pricelist_context = dict(context_partner, uom=uom, date=date_order)
             list_price = pricelist_obj.price_rule_get(cr, uid, [pricelist],
                     product.id, qty or 1.0, partner_id, context=pricelist_context)
 
-            so_pricelist = pricelist_obj.browse(cr, uid, pricelist, context=context)
+            so_pricelist = pricelist_obj.browse(cr, uid, pricelist, context=context_partner)
 
-            new_list_price = get_real_price(list_price, product.id, qty, uom, pricelist)
+            new_list_price = get_real_price(list_price, product.id, qty, uom, pricelist, context=context_partner)
             if so_pricelist.visible_discount and list_price[pricelist][0] != 0 and new_list_price != 0:
                 if product.company_id and so_pricelist.currency_id.id != product.company_id.currency_id.id:
                     # new_list_price is in company's currency while price in pricelist currency
-                    ctx = context.copy()
+                    ctx = context_partner.copy()
                     ctx['date'] = date_order
                     new_list_price = self.pool['res.currency'].compute(cr, uid,
                         product.company_id.currency_id.id, so_pricelist.currency_id.id,
