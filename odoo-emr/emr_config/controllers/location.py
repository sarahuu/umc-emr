from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.home import Home
from odoo.addons.web.controllers.session import Session


class Login(Home):
    @http.route('/web/login', type='http', auth="public")
    def web_login(self, redirect=None, **kw):
        if request.httprequest.method == 'POST':
            location = kw.get("emr_location")
            response = super().web_login(redirect=redirect, **kw)
            if request.session.uid and location:
                request.session['active_location'] = int(location)
                user = request.env['res.users'].browse(request.session.uid).sudo()
                # user.default_location_id = int(location)
            elif not request.session.uid:
                qcontext = request.params.copy()
                qcontext['locations'] = request.env['emr.locations'].sudo().search([])
                qcontext['error'] = "Wrong login/password"  # You can keep Odoo's own error if preferred
                return request.render("web.login", qcontext)
            return response
        qcontext = request.params.copy()
        qcontext['locations'] = request.env['emr.locations'].sudo().search([])
        return request.render("web.login", qcontext)



class Session(Session):
    @http.route('/web/session/get_session_info', type='json', auth="user")
    def get_session_info(self):
        session_info = super().get_session_info()
        location = request.session.get('active_location')
        if location:
            session_info['user_context']['active_location'] = location
            session_info['active_location'] = location
        return session_info
