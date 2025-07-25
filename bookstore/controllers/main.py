# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class BookstoreController(http.Controller):

    @http.route('/bookstore', type='http', auth='public', website=True)
    def bookstore_home(self, **kwargs):
        """Bookstore homepage"""
        try:
            # Search for all books, with safe fallbacks for missing fields
            domain = []
            
            # Only add is_published filter if the field exists
            try:
                if 'is_published' in request.env['bookstore.book']._fields:
                    domain.append(('is_published', '=', True))
            except:
                pass
            
            books = request.env['bookstore.book'].sudo().search(domain)
            categories = request.env['bookstore.category'].sudo().search([])
            
            return request.render('bookstore.bookstore_home', {
                'books': books,
                'categories': categories,
            })
        except Exception as e:
            # If anything fails, return a simple error page
            return request.render('website.404')

    @http.route('/bookstore/book/<int:book_id>', type='http', auth='public', website=True)
    def book_detail(self, book_id, **kwargs):
        """Book detail page"""
        try:
            book = request.env['bookstore.book'].sudo().browse(book_id)
            if not book.exists():
                return request.not_found()
            
            return request.render('bookstore.book_detail', {
                'book': book,
            })
        except Exception as e:
            return request.not_found()
