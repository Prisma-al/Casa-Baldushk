# -*- coding: utf-8 -*-
# from odoo import http


# class PosFrontSort(http.Controller):
#     @http.route('/pos_front_sort/pos_front_sort', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_front_sort/pos_front_sort/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_front_sort.listing', {
#             'root': '/pos_front_sort/pos_front_sort',
#             'objects': http.request.env['pos_front_sort.pos_front_sort'].search([]),
#         })

#     @http.route('/pos_front_sort/pos_front_sort/objects/<model("pos_front_sort.pos_front_sort"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_front_sort.object', {
#             'object': obj
#         })

