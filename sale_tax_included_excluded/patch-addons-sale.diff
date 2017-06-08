diff --git a/addons/sale/sale.py b/addons/sale/sale.py
index 2273a88..ec882f8 100644
--- a/addons/sale/sale.py
+++ b/addons/sale/sale.py
@@ -1049,10 +1049,10 @@ class sale_order_line(osv.osv):
         product_uom_obj = self.pool.get('product.uom')
         partner_obj = self.pool.get('res.partner')
         product_obj = self.pool.get('product.product')
-        context = {'lang': lang, 'partner_id': partner_id}
         partner = partner_obj.browse(cr, uid, partner_id)
         lang = partner.lang
-        context_partner = {'lang': lang, 'partner_id': partner_id}
+        context_partner = context.copy()
+        context_partner.update({'lang': lang, 'partner_id': partner_id})
 
         if not product:
             return {'value': {'th_weight': 0,
@@ -1130,11 +1130,13 @@ class sale_order_line(osv.osv):
                     'Please set one before choosing a product.')
             warning_msgs += _("No Pricelist ! : ") + warn_msg +"\n\n"
         else:
+            ctx_priceget = context.copy()
+            ctx_priceget.update({
+                'uom': uom or result.get('product_uom'),
+                'date': date_order,
+                })
             price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
-                    product, qty or 1.0, partner_id, {
-                        'uom': uom or result.get('product_uom'),
-                        'date': date_order,
-                        })[pricelist]
+                    product, qty or 1.0, partner_id, context=ctx_priceget)[pricelist]
             if price is False:
                 warn_msg = _("Cannot find a pricelist line matching this product and quantity.\n"
                         "You have to change either the product, the quantity or the pricelist.")
