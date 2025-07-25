# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class BookstoreController(http.Controller):

    @http.route('/bookstore', type='http', auth='public', website=True)
    def bookstore_home(self, **kwargs):
        """Bookstore homepage"""
        try:
            # Try to search with is_published field
            books = request.env['bookstore.book'].sudo().search([('is_published', '=', True)])
        except Exception:
            # Fallback if is_published field doesn't exist yet
            books = request.env['bookstore.book'].sudo().search([])
        
        categories = request.env['bookstore.category'].sudo().search([])
        
        return request.render('bookstore.bookstore_home', {
            'books': books,
            'categories': categories,
        })

    @http.route('/bookstore/book/<int:book_id>', type='http', auth='public', website=True)
    def book_detail(self, book_id, **kwargs):
        """Book detail page"""
        book = request.env['bookstore.book'].sudo().browse(book_id)
        if not book.exists():
            return request.not_found()
        
        # Check if is_published field exists and is False
        try:
            if hasattr(book, 'is_published') and not book.is_published:
                return request.not_found()
        except Exception:
            # Field doesn't exist yet, allow access
            pass
        
        return request.render('bookstore.book_detail', {
            'book': book,
        })
