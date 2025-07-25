# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

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
    
    @http.route('/bookstore/create_products', type='http', auth='user', website=True)
    def create_products(self, **kwargs):
        """Manually create products for books"""
        if not request.env.user.has_group('base.group_system'):
            return request.not_found()
        
        books = request.env['bookstore.book'].sudo().search([('product_id', '=', False)])
        created_count = 0
        
        for book in books:
            book._create_product()
            created_count += 1
        
        return request.render('bookstore.sync_result', {
            'message': f'Successfully created {created_count} products for books.',
            'created_count': created_count,
        })

    @http.route('/shop/books', type='http', auth='public', website=True)
    def shop_books(self, **kwargs):
        """Show all books in shop format"""
        books = request.env['bookstore.book'].sudo().search([
            ('is_published', '=', True),
            ('product_id', '!=', False)
        ])
        
        return request.render('bookstore.shop_books', {
            'books': books,
        })
