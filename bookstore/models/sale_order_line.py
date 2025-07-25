# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    def _get_max_line_qty(self):
        """Get maximum quantity for line - fix for cart error"""
        if self.product_id and self.product_id.type == 'product':
            # For physical products, limit to available stock
            available_qty = self.product_id.with_context(warehouse=self.order_id.warehouse_id.id).qty_available
            return max(available_qty, 1)  # Always allow at least 1
        else:
            # For services or other types, no limit
            return 9999
    
    def _get_displayed_quantity(self):
        """Get the quantity to display in cart"""
        return self.product_uom_qty or 1
