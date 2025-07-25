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
    
    @api.model
    def create(self, vals):
        """Create book and automatically create related product"""
        book = super(Book, self).create(vals)
        book._create_product()
        return book
    
    def write(self, vals):
        """Update book and sync with related product"""
        result = super(Book, self).write(vals)
        for book in self:
            if book.product_id:
                book._update_product()
            else:
                book._create_product()
        return result
    
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
    product_category_id = fields.Many2one('product.category', string='Related Product Category', ondelete='cascade')
    
    @api.model
    def create(self, vals):
        """Create category and automatically create related product category"""
        category = super(BookCategory, self).create(vals)
        category._create_product_category()
        return category
    
    def _create_product_category(self):
        """Create a product.category record for this book category"""
        if not self.product_category_id:
            category_vals = {
                'name': f'Books - {self.name}',
                'parent_id': False,
            }
            
            product_category = self.env['product.category'].create(category_vals)
            self.product_category_id = product_category.id
