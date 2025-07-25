# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class BookstoreController(http.Controller):

    @http.route('/bookstore', type='http', auth='public', website=True)
    def bookstore_home(self, **kwargs):
        """Bookstore homepage"""
        books = request.env['bookstore.book'].sudo().search([('is_published', '=', True)])
        categories = request.env['bookstore.category'].sudo().search([])
        
        return request.render('bookstore.bookstore_home', {
            'books': books,
            'categories': categories,
        })

    @http.route('/bookstore/book/<int:book_id>', type='http', auth='public', website=True)
    def book_detail(self, book_id, **kwargs):
        """Book detail page"""
        book = request.env['bookstore.book'].sudo().browse(book_id)
        if not book.exists() or not book.is_published:
            return request.not_found()
        
        return request.render('bookstore.book_detail', {
            'book': book,
        })
    
    @http.route('/bookstore/sync_products', type='http', auth='user', website=True)
    def sync_products(self, **kwargs):
        """Sync all books with products for admin users"""
        if not request.env.user.has_group('base.group_system'):
            return request.not_found()
        
        books = request.env['bookstore.book'].sudo().search([])
        synced_count = 0
        updated_count = 0
        
        for book in books:
            if not book.product_id:
                book._create_product()
                synced_count += 1
            else:
                book._update_product()
                updated_count += 1
        
        message = f"Sync complete! Created {synced_count} new products, updated {updated_count} existing products."
        return request.render('bookstore.sync_result', {
            'message': message,
            'synced_count': synced_count,
            'updated_count': updated_count,
        })
        
    @http.route('/bookstore/clear_data', type='http', auth='user', website=True)  
    def clear_old_data(self, **kwargs):
        """Clear old product data and resync"""
        if not request.env.user.has_group('base.group_system'):
            return request.not_found()
            
        # Find orphaned products (products with book-like codes but no corresponding book)
        orphaned_products = request.env['product.product'].sudo().search([
            ('default_code', 'like', 'BOOK_%'),
            ('id', 'not in', request.env['bookstore.book'].search([]).mapped('product_id.id'))
        ])
        
        orphaned_count = len(orphaned_products)
        orphaned_products.unlink()
        
        # Resync all books
        books = request.env['bookstore.book'].sudo().search([])
        for book in books:
            if not book.product_id:
                book._create_product()
            else:
                book._update_product()
        
        message = f"Data cleared! Removed {orphaned_count} orphaned products and synced {len(books)} books."
        return request.render('bookstore.sync_result', {
            'message': message,
            'orphaned_count': orphaned_count,
            'books_count': len(books),
        })


class BookstoreWebsiteSale(WebsiteSale):
    
    @http.route(['/shop/book/<int:book_id>'], type='http', auth="public", website=True)
    def book_product_detail(self, book_id, **kwargs):
        """Show book as product in shop"""
        book = request.env['bookstore.book'].sudo().browse(book_id)
        if not book.exists() or not book.is_published or not book.product_id:
            return request.not_found()
        
        # Redirect to the product page
        return request.redirect('/shop/product/%s' % book.product_id.id)
    
    @http.route(['/shop/books'], type='http', auth="public", website=True)
    def shop_books(self, **kwargs):
        """Show all books in shop format"""
        domain = [('is_published', '=', True), ('product_id', '!=', False)]
        books = request.env['bookstore.book'].sudo().search(domain)
        
        return request.render('bookstore.shop_books', {
            'books': books,
        })
