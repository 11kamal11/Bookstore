# -*- coding: utf-8 -*-
from odoo import models, fields, api

class Book(models.Model):
    _name = 'bookstore.book'
    _description = 'Book'
    _rec_name = 'name'

    name = fields.Char('Book Title', required=True)
    author = fields.Char('Author', required=True)
    isbn = fields.Char('ISBN')
    price = fields.Float('Price')
    description = fields.Text('Description')
    category_id = fields.Many2one('bookstore.category', string='Category')
    product_id = fields.Many2one('product.product', string='Related Product', ondelete='cascade')
    is_published = fields.Boolean('Published on Website', default=True)
    
    def _create_product(self):
        """Create a product.product record for this book"""
        if not self.product_id:
            product_vals = {
                'name': self.name,
                'list_price': self.price or 0.0,
                'standard_price': self.price or 0.0,
                'description_sale': self.description or '',
                'type': 'product',
                'is_published': self.is_published,
                'website_published': self.is_published,
                'sale_ok': True,
                'purchase_ok': False,
                'detailed_type': 'product',
                'default_code': f'BOOK_{self.isbn}' if self.isbn else f'BOOK_{self.id}',
            }
            
            product = self.env['product.product'].create(product_vals)
            self.product_id = product.id
    
    def _update_product(self):
        """Update the related product"""
        if self.product_id:
            self.product_id.write({
                'name': self.name,
                'list_price': self.price or 0.0,
                'standard_price': self.price or 0.0,
                'description_sale': self.description or '',
                'is_published': self.is_published,
                'website_published': self.is_published,
                'default_code': f'BOOK_{self.isbn}' if self.isbn else f'BOOK_{self.id}',
            })
    
    def action_publish_website(self):
        """Publish book on website"""
        self.write({'is_published': True})
        if self.product_id:
            self.product_id.write({'website_published': True})
    
    def action_unpublish_website(self):
        """Unpublish book from website"""
        self.write({'is_published': False})
        if self.product_id:
            self.product_id.write({'website_published': False})


class BookCategory(models.Model):
    _name = 'bookstore.category'
    _description = 'Book Category'
    _rec_name = 'name'

    name = fields.Char('Category Name', required=True)
    description = fields.Text('Description')
    book_ids = fields.One2many('bookstore.book', 'category_id', string='Books')
