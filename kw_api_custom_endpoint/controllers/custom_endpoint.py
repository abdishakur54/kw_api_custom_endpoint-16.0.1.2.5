import logging

from odoo import http
from odoo.addons.kw_api.controllers.controller_base import kw_api_route, KwApi
from odoo.http import request

_logger = logging.getLogger(__name__)


# pylint: disable=too-many-return-statements
class CustomEndpointController(http.Controller):

    @kw_api_route(
        methods=['GET', 'POST', 'DELETE'],
        route=['/kw_api/custom/<string:api_name>',
               '/kw_api/custom/<string:api_name>/<int:obj_id>'])
    def kw_api_custom_response(self, api_name, obj_id=False, **kw):
        endpoint = request.env['kw.api.custom.endpoint'].sudo().search([
            ('api_name', '=', api_name)], limit=1)

        if not endpoint:
            return KwApi().response(
                code=404, error='404: Not Found', data={'error': {
                    'code': '404', 'message': '404: Not Found'}}, )

        kw_api = KwApi(**endpoint.kwapi_params())

        if endpoint.is_api_key_required:
            api_key_p = request.env['kw.api.key'].sudo().get_api_key()
            if not api_key_p['allowed_api_key_ip']:
                return KwApi().response(
                    code=403, error='403: Wrong API key', data={'error': {
                        'code': '403', 'message': '403: Wrong API key'}}, )

        if request.httprequest.method == 'POST':
            if obj_id and not endpoint.is_update_enabled:
                return KwApi().response(
                    code=403, error='403: Update forbidden', data={'error': {
                        'code': '403', 'message': '403: Update forbidden'}}, )
            if not obj_id and not endpoint.is_create_enabled:
                return KwApi().response(
                    code=403, error='403: Create forbidden', data={'error': {
                        'code': '403', 'message': '403: Create forbidden'}}, )
            return endpoint.change(kw_api=kw_api, obj_id=obj_id, **kw)

        if request.httprequest.method == 'DELETE':
            if obj_id and not endpoint.is_delete_enabled:
                return KwApi().response(
                    code=403, error='403: Delete forbidden', data={'error': {
                        'code': '403', 'message': '403: Delete forbidden'}}, )
            return endpoint.delete(kw_api=kw_api, obj_id=obj_id, **kw)

        if obj_id and not endpoint.is_get_enabled:
            return KwApi().response(
                code=403, error='403: Get forbidden', data={'error': {
                    'code': '403', 'message': '403: Get forbidden'}}, )
        if not obj_id and not endpoint.is_list_enabled:
            return KwApi().response(
                code=403, error='403: List forbidden', data={'error': {
                    'code': '403', 'message': '403: List forbidden'}}, )

        page_index = request.httprequest.args.get('pageIndex')
        try:
            kw_api.page_index = int(page_index)
        except Exception as e:
            _logger.debug(e)
        page_size = request.httprequest.args.get('pageSize')
        try:
            kw_api.page_size = int(page_size)
        except Exception as e:
            _logger.debug(e)
        kw['update_date'] = request.httprequest.args.get('update_date')

        return endpoint.response(kw_api=kw_api, obj_id=obj_id, **kw)
