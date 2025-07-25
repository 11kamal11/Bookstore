# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class BookstoreController(http.Controller):

    @http.route('/bookstore', type='http', auth='public', website=True)
    def bookstore_home(self, **kwargs):
        books = request.env['bookstore.book'].sudo().search([('is_published', '=', True)])
        categories = request.env['bookstore.category'].sudo().search([])
        
        return request.render('bookstore.bookstore_home', {
            'books': books,
            'categories': categories,
        })

    @http.route('/bookstore/book/<int:book_id>', type='http', auth='public', website=True)
    def book_detail(self, book_id, **kwargs):
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
        for book in books:
            if not book.product_id:
                book._create_product()
            else:
                book._update_product()
        
        return request.render('bookstore.sync_complete', {
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
        products = books.mapped('product_id')
        
        return request.render('website_sale.products', {
            'products': products,
            'search': 'books',
            'category': False,
            'attrib_values': [],
            'attrib_set': set(),
            'keep': {},
            'categories': request.env['product.public.category'].search([]),
            'pager': {},
            'bins': lambda x: [products[i:i+4] for i in range(0, len(products), 4)],
        })
