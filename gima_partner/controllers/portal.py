import datetime
import werkzeug
from collections import OrderedDict
from markupsafe import Markup
from dateutil.relativedelta import relativedelta
from math import ceil
from werkzeug.urls import url_encode
from odoo.exceptions import UserError
from odoo import http, fields, _
from odoo.exceptions import AccessError, MissingError
from odoo.addons.portal.controllers import portal
from odoo.http import request, content_disposition
from odoo.addons.portal.controllers.portal import pager as portal_pager
import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import groupby as groupbyeleme
from operator import itemgetter
from werkzeug.wrappers import Response
import base64
from odoo.osv.expression import OR, AND
import mimetypes


class GimaPortal(portal.CustomerPortal):

    def _get_certification_searchbar_sortings(self):
        return {
            'certificate_number': {'label': _('Certification Number'), 'certification': 'certificate_number asc'},
            'partner_id': {'label': _('Partner'), 'certification': 'partner_id asc'},
            'type': {'label': _('Type'), 'certification': 'type asc'},
            'date_of_issue': {'label': _('Date of issue'), 'certification': 'date_of_issue asc'},
            'expiring_date': {'label': _('Expiring Date'), 'certification': 'expiration_date asc'},
            'State': {'label': _('State'), 'certification': 'state asc'},
        }

    def _prepare_certification_domain(self, partner):
        partner_ids = [partner.id] + [child.id for child in partner.child_ids]
        domain = [('partner_id', 'in', partner_ids)]
        return domain

    def _prepare_certifications_portal_rendering_values(
            self, page=1, date_begin=None, date_end=None, sortby=None, groupby=None, filterby=None, search_in=None,
            search=None, **kwargs
    ):
        GimaCertifications = request.env['gima.certifications']

        if not sortby:
            sortby = 'partner_id'
        if not groupby:
            groupby = 'type'
        if not filterby:
            filterby = 'all'
        if not search_in:
            search_in = 'partner_id'
        partner = request.env.user.partner_id
        values = self._prepare_portal_layout_values()
        domain = self._prepare_certification_domain(partner)
        searchbar_sortings = self._get_certification_searchbar_sortings()

        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'type': {'input': 'type', 'label': _('Type')},
        }
        # Definizione del filtro 'Expiration_1_month'
        # VEDRÒ TUTTE LE SCADENZE DI MASSIMO 2 MESI
        expiration_1_month_domain = [
            ('expiration_date', '!=', False),
            ('expiration_date', '<=', (datetime.datetime.now() + relativedelta(months=2)).date()),
        ]
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'expiration_1_month: ': {'label': _('Expiration: 1 month'), 'domain': expiration_1_month_domain},
        }

        searchbar_inputs = {
            'partner': {'input': 'partner_id', 'label': _('Search in Partner')},
            'certificate_number': {'input': 'certificate_number', 'label': _('Search in Certification')},
        }
        if filterby:
            domain += searchbar_filters[filterby]['domain']

        type_group_by = searchbar_groupby.get(groupby, {})
        if groupby in ('type'):
            type_group_by = type_group_by.get("input")
        else:
            type_group_by = ''

        sort_order = searchbar_sortings[sortby]['certification']

        # search
        if search and search_in:
            search_domain = []
            if search_in == 'partner_id':
                partners = request.env['res.partner'].sudo().search([('name', 'ilike', search)])
                search_domain = OR([search_domain, [('partner_id', 'in', partners.ids)]])
            if search_in == 'content':
                partners = request.env['res.partner'].sudo().search([('name', 'ilike', search)])
                search_domain = OR([search_domain,
                                    ['|', '|', ('name', 'ilike', search), ('certificate_number', 'ilike', search),
                                     ('partner_id', 'in', partners.ids)]])
            if search_in == 'certificate_number':
                search_domain = OR([search_domain, [('certificate_number', 'ilike', search)]])
            domain = AND([domain, search_domain])

        url = "/my/company_certifications"
        pager_values = portal_pager(
            url=url,
            total=GimaCertifications.search_count(domain),
            page=page,
            step=5,
            url_args={'sortby': sortby, 'search_in': search_in, 'search': search, 'groupby': groupby,
                      'filterby': filterby},
        )

        gima_certifications = GimaCertifications.search(domain, order=sort_order, limit=5,
                                                        offset=pager_values['offset'])
        if type_group_by:
            types_group_list = [
                {type_group_by: dict(g[0]._fields['type'].selection).get(g[0].type), str(type_group_by + '_key'): k,
                 'certifications': GimaCertifications.concat(*g)} for k, g in
                groupbyeleme(gima_certifications, itemgetter(type_group_by))]
        else:
            types_group_list = [{'certifications': gima_certifications}]

        for type_group in types_group_list:
            type_group['priority'] = 10
            type_key = type_group.get('type_key')
            if type_key and 'company' in type_key:
                type_group['priority'] = 1
        types_group_list = sorted(types_group_list, key=lambda x: x['priority'])
        values.update({
            'grouped_certifications': types_group_list,
            'pager': pager_values,
            'default_url': url,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_filters': searchbar_filters,
            'searchbar_inputs': searchbar_inputs,
            'sortby': sortby,
            'groupby': groupby,
            'filterby': filterby,
            'search_in': search_in,
            'search': search,
        })

        return values

    @http.route(['/my/company_certifications', '/my/company_certifications/page/<int:page>'], type='http', auth="user",
                website=True)
    def my_certifications(self, **kwargs):
        values = self._prepare_certifications_portal_rendering_values(**kwargs)
        return request.render("gima_partner.portal_my_certifications", values)

    def _get_headers(self, content, filename, content_type):
        return [
            ('Content-Type', content_type),
            ('X-Content-Type-Options', 'nosniff'),
            ('Content-Length', len(content)),
            ('Content-Disposition', content_disposition(filename)),
        ]

    def _get_invoice_report_filename(self, extension='pdf'):
        """ Get the filename of the generated invoice report with extension file. """
        self.ensure_one()
        return f"{self.name.replace('/', '_')}.{extension}"

    def get_name_attachment(self, model_name, object, attachment_ids, extension):
        """
        Object gima.certification/gima.training
        Partner_id is required
        Certificate number is not required

        attachment_ids can be only one
        """
        filename = ""
        if object.partner_id.name:
            filename += object.partner_id.name + " - "
        if model_name == 'gima.certifications':
            filename += object.certificate_number + " - " + dict(object._fields['type'].selection).get(object.type)
        if model_name == 'gima.training':
            if object.course_id.code:
                filename += object.course_id.code
        filename += extension

        return filename

    @http.route(['/download/certificate/<model>/<int:certification_id>/<attachment_ids>'], type='http',
                auth="user", website=True)
    def download_attachment(self, **kwargs):
        """
        Certification_id can be used in gima.certifications and gima.training models
        :param kwargs:
            model --> gima.certifications/gima.training
            attachment_ids --> ids attachments
            certification_id --> id of gima.certifications/gima.training
        """
        attachment_ids = eval(kwargs.get('attachment_ids'))
        model = kwargs.get('model')
        # CAN BE CERTIFICATION OR TRAINING --> gima_certification
        gima_certification = request.env[model].browse(kwargs['certification_id'])
        attachments = request.env['ir.attachment'].sudo().browse(attachment_ids)
        attachments.check_access_rights('read')
        attachments.check_access_rule('read')
        if len(attachment_ids) > 1:
            extension = '.zip'
            filename = self.get_name_attachment(model, gima_certification, attachment_ids, extension)
            content = attachments._build_zip_from_attachments()
        else:
            attachment = attachments[0]
            extension = "." + attachment.mimetype.split('/')[1]
            content = base64.b64decode(attachment.datas)
            filename = self.get_name_attachment(model, gima_certification, attachments, extension)
        headers = self._get_headers(content, filename, extension.replace(".", " "))
        return request.make_response(content, headers)

    # -------------------------- COURSES-TRAINING

    @http.route(['/my/company_training'], type='http', auth="user", website=True)
    def my_training_home(self, **kw):
        values = self._prepare_portal_layout_values()
        return request.render("gima_partner.portal_my_training", values)

    @http.route(['/my/company_training/<string:course_type>'], type='http', auth="user", website=True)
    def my_training(self, **kw):
        values = self._prepare_portal_layout_values()
        return request.render("gima_partner.portal_my_courses", values)
