from odoo import models, fields, api, tools, _
from odoo.exceptions import ValidationError


class RestockWizard(models.TransientModel):
    _name = 'bookstore.restock.wizard'
    _description = 'Restock Books Wizard'

    book_id = fields.Many2one('bookstore.book', string='Book', required=True)
    current_stock = fields.Integer(related='book_id.stock_quantity', string='Current Stock', readonly=True)
    quantity_to_add = fields.Integer(string='Quantity to Add', required=True, default=1)
    reason = fields.Text(string='Reason for Restock')
    new_cost_price = fields.Float(string='New Cost Price (optional)')
    
    def action_restock(self):
        """Process the restock operation"""
        if self.quantity_to_add <= 0:
            raise ValidationError("Quantity to add must be positive.")
        
        # Update stock quantity
        self.book_id.stock_quantity += self.quantity_to_add
        
        # Update cost price if provided
        if self.new_cost_price > 0:
            self.book_id.cost_price = self.new_cost_price
        
        # Create a log entry
        self.env['bookstore.stock.log'].create({
            'book_id': self.book_id.id,
            'operation': 'restock',
            'quantity': self.quantity_to_add,
            'reason': self.reason,
            'user_id': self.env.user.id,
            'date': fields.Datetime.now(),
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Book "%s" restocked with %d units.') % (self.book_id.name, self.quantity_to_add),
                'type': 'success',
            }
        }


class StockLog(models.Model):
    _name = 'bookstore.stock.log'
    _description = 'Stock Movement Log'
    _order = 'date desc'

    book_id = fields.Many2one('bookstore.book', string='Book', required=True)
    operation = fields.Selection([
        ('restock', 'Restock'),
        ('sale', 'Sale'),
        ('adjustment', 'Adjustment'),
        ('return', 'Return'),
    ], string='Operation', required=True)
    quantity = fields.Integer(string='Quantity')
    reason = fields.Text(string='Reason')
    user_id = fields.Many2one('res.users', string='User', required=True)
    date = fields.Datetime(string='Date', required=True)
    
    # Related fields for reporting
    book_title = fields.Char(related='book_id.name', string='Book Title', store=True)
    book_category = fields.Char(related='book_id.category_id.name', string='Category', store=True)


class BookReport(models.Model):
    _name = 'bookstore.book.report'
    _description = 'Book Sales Report'
    _auto = False
    _rec_name = 'book_id'

    book_id = fields.Many2one('bookstore.book', string='Book')
    category_id = fields.Many2one('bookstore.category', string='Category')
    total_sold = fields.Integer(string='Total Sold')
    total_revenue = fields.Float(string='Total Revenue')
    stock_quantity = fields.Integer(string='Current Stock')
    profit_margin = fields.Float(string='Profit Margin %')
    
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    row_number() OVER () AS id,
                    b.id AS book_id,
                    b.category_id,
                    b.total_sold,
                    (b.total_sold * b.price) AS total_revenue,
                    b.stock_quantity,
                    b.profit_margin
                FROM bookstore_book b
                WHERE b.active = true
            )
        """ % self._table)
