# -*- coding: utf-8 -*-
from odoo import models, fields, api

class BookProductSyncWizard(models.TransientModel):
    _name = 'bookstore.sync.wizard'
    _description = 'Book Product Sync Wizard'
    
    book_ids = fields.Many2many('bookstore.book', string='Books to Sync')
    sync_all = fields.Boolean('Sync All Books', default=True)
    update_existing = fields.Boolean('Update Existing Products', default=True)
    
    @api.model
    def default_get(self, fields):
        res = super(BookProductSyncWizard, self).default_get(fields)
        if 'book_ids' in fields:
            # Get all books without products
            books = self.env['bookstore.book'].search([('product_id', '=', False)])
            res['book_ids'] = [(6, 0, books.ids)]
        return res
    
    def action_sync_products(self):
        """Sync books with products"""
        books_to_sync = self.book_ids if not self.sync_all else self.env['bookstore.book'].search([])
        
        synced_count = 0
        for book in books_to_sync:
            if not book.product_id:
                book._create_product()
                synced_count += 1
            elif self.update_existing:
                book._update_product()
                synced_count += 1
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Sync Complete',
                'message': f'Successfully synced {synced_count} books with products.',
                'type': 'success',
                'sticky': False,
            }
        }
