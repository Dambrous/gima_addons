from odoo import http, fields, _
from odoo.addons.portal.controllers import portal
from odoo.http import request, content_disposition
from odoo.addons.portal.controllers.portal import pager as portal_pager
import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import groupby as groupbyeleme
from operator import itemgetter
import base64
from odoo.osv.expression import OR, AND
from odoo.tools.translate import _


class GimaPortal(portal.CustomerPortal):
    def _get_certification_searchbar_sortings(self):
        return {
            "certificate_number": {
                "label": _("Certificate Number"),
                "certification": "certificate_number asc",
            },
            "partner_id": {"label": _("Employee"), "certification": "partner_id asc"},
            "type_certification_id": {"label": _("Type"), "certification": "type_certification_id asc"},
            "date_of_issue": {
                "label": _("Date of issue"),
                "certification": "date_of_issue asc",
            },
            "expiring_date": {
                "label": _("Expiring Date"),
                "certification": "expiration_date asc",
            },
            "State": {"label": _("State"), "certification": "state asc"},
        }, {
            "none": {"input": "none", "label": _("None")},
            "type_certification_id": {"input": "type", "label": _("Type")},
        }, {
            "employees": {"label": _("Employees"),
                          "domain": [('partner_id', 'in', request.env.user.partner_id.child_ids.ids)]},
            "company": {"label": _("Company"), "domain": [('partner_id', '=', request.env.user.partner_id.id)]},
            # "expiration_1_month: ": {
            #     "label": _("Expiration: 1 month"),
            #     "domain": [
            #         ("expiration_date", "!=", False),
            #         (
            #             "expiration_date",
            #             "<=",
            #             (datetime.datetime.now() + relativedelta(months=2)).date(),
            #         ),
            #     ],
            # },
        }, {
            "partner": {"input": "partner_id", "label": _("Search in Partner")},
            "certificate_number": {
                "input": "certificate_number",
                "label": _("Search in Certification"),
            },
        }

    def _prepare_certification_domain(self, partner):
        partner_ids = [partner.id] + [child.id for child in partner.child_ids]
        domain = [("partner_id", "in", partner_ids)]
        return domain

    def _prepare_certifications_portal_rendering_values(
            self,
            page=1,
            date_begin=None,
            date_end=None,
            sortby=None,
            groupby=None,
            filterby=None,
            search_in=None,
            search=None,
            **kwargs,
    ):
        model = "gima.certifications"
        GimaCertifications = request.env[model]
        partner = request.env.user.partner_id
        # domain = self._prepare_certification_domain(partner)
        domain = []
        if not sortby:
            sortby = "partner_id"
        # if not groupby:
        #     groupby = "type"
        if not filterby:
            if kwargs.get("type_certification") == "fgas":
                filterby = "employees"
            if kwargs.get("type_certification") == "iso_9001":
                filterby = "company"
        if not search_in:
            search_in = "partner_id"
        values = self._prepare_portal_layout_values()
        if kwargs.get("type_certification") == "fgas":
            certification_ids = request.env['gima.macro.certification'].search([('code', 'in', ('C-FGAS', 'E-FGAS'))])
            domain += [
                ("type_certification_id", "in", certification_ids.ids)
            ]
            values['page_name'] = "FGAS | GIMA Progetti"
        if kwargs.get("type_certification") == "iso_9001":
            certification_ids = request.env['gima.macro.certification'].search([('code', '=', 'C-9001')])
            domain += [("type_certification_id", "in", certification_ids.ids)]
            values['page_name'] = "ISO 9001 | GIMA Progetti"
        searchbar_sortings, searchbar_groupby, searchbar_filters, searchbar_inputs = self._get_certification_searchbar_sortings()

        if filterby:
            domain += searchbar_filters[filterby]["domain"]

        # type_group_by = searchbar_groupby.get(groupby, {})
        # if groupby in ("type"):
        #     type_group_by = type_group_by.get("input")
        # else:
        #     type_group_by = ""

        sort_order = searchbar_sortings[sortby]["certification"]

        # search
        if search and search_in:
            search_domain = []
            if search_in == "partner_id":
                partners = (
                    request.env["res.partner"]
                    .sudo()
                    .search([("name", "ilike", search)])
                )
                search_domain = OR(
                    [search_domain, [("partner_id", "in", partners.ids)]]
                )
            if search_in == "content":
                partners = (
                    request.env["res.partner"]
                    .sudo()
                    .search([("name", "ilike", search)])
                )
                search_domain = OR(
                    [
                        search_domain,
                        [
                            "|",
                            "|",
                            ("name", "ilike", search),
                            ("certificate_number", "ilike", search),
                            ("partner_id", "in", partners.ids),
                        ],
                    ]
                )
            if search_in == "certificate_number":
                search_domain = OR(
                    [search_domain, [("certificate_number", "ilike", search)]]
                )
            domain = AND([domain, search_domain])

        url = "/my/company_certification/" + str(kwargs.get("type_certification"))
        pager_values = portal_pager(
            url=url,
            total=GimaCertifications.search_count(domain),
            page=page,
            step=20,
            url_args={
                "sortby": sortby,
                "search_in": search_in,
                "search": search,
                "groupby": groupby,
                "filterby": filterby,
            },
        )

        gima_certifications = GimaCertifications.search(
            domain, order=sort_order, limit=20, offset=pager_values["offset"]
        )
        # if type_group_by:
        #     types_group_list = [
        #         {
        #             type_group_by: dict(g[0]._fields["type"].selection).get(g[0].type),
        #             str(type_group_by + "_key"): k,
        #             "certifications": GimaCertifications.concat(*g),
        #         }
        #         for k, g in groupbyeleme(gima_certifications, itemgetter(type_group_by))
        #     ]
        # else:
        #     types_group_list = [{"certifications": gima_certifications}]
        #
        # for type_group in types_group_list:
        #     type_group["priority"] = 10
        #     type_key = type_group.get("type_key")
        #     if type_key and "company" in type_key:
        #         type_group["priority"] = 1
        # types_group_list = sorted(types_group_list, key=lambda x: x["priority"])
        # for certification in types_group_list:
        #     if certification.get('type'):
        #         certification['type'] = _._get_translation(certification['type'])
        values.update(
            {
                "grouped_certifications": gima_certifications,
                "pager": pager_values,
                "default_url": url,
                "searchbar_sortings": searchbar_sortings,
                # "searchbar_groupby": searchbar_groupby,
                "searchbar_filters": searchbar_filters,
                "searchbar_inputs": searchbar_inputs,
                "sortby": sortby,
                # "groupby": groupby,
                "filterby": filterby,
                "search_in": search_in,
                "search": search,
                "type": 'certification'
            }
        )

        return values

    @http.route(
        ["/my/company_certifications"],
        type="http",
        auth="user",
        website=True,
    )
    def my_certifications(self, ):
        return request.render("gima_partner.portal_my_certifications")

    @http.route(
        ["/my/company_certification/<type_certification>",
         "/my/company_certifications/<type_certification>/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def my_certification_fgas(self, **kwargs):
        values = self._prepare_certifications_portal_rendering_values(**kwargs)
        return request.render("gima_partner.portal_view_certifications", values)

    def _get_headers(self, content, filename, content_type):
        return [
            ("Content-Type", content_type),
            ("X-Content-Type-Options", "nosniff"),
            ("Content-Length", len(content)),
            ("Content-Disposition", content_disposition(filename)),
        ]

    def _get_invoice_report_filename(self, extension="pdf"):
        """Get the filename of the generated invoice report with extension file."""
        self.ensure_one()
        return f"{self.name.replace('/', '_')}.{extension}"

    def get_name_attachment(self, model_name, object, extension):
        """
        Object gima.certification/gima.training
        Partner_id is required
        Certificate number is not required

        attachment_ids can be only one
        """
        filename = ""
        if object.partner_id.name:
            filename += object.partner_id.name + " - "
        if model_name == "gima.certifications":
            filename += (
                    object.certificate_number
                    + " - "
                    + dict(object._fields["type"].selection).get(object.type)
            )
        if model_name == "gima.training":
            if object.course_id.code:
                filename += object.course_id.code
        filename += extension

        return filename

    @http.route(
        ["/download/certificate/<model>/<int:certification_id>/<attachment_ids>"],
        type="http",
        auth="user",
        website=True,
    )
    def download_attachment(self, **kwargs):
        """
        Certification_id can be used in gima.certifications and gima.training models
        :param kwargs:
            model --> gima.certifications/gima.training
            attachment_ids --> ids attachments
            certification_id --> id of gima.certifications/gima.training
        """
        attachment_ids = eval(kwargs.get("attachment_ids"))
        model = kwargs.get("model")
        # CAN BE CERTIFICATION OR TRAINING --> gima_certification
        gima_certification = request.env[model].browse(kwargs["certification_id"])
        attachments = request.env["ir.attachment"].sudo().browse(attachment_ids)
        attachments.check_access_rights("read")
        attachments.check_access_rule("read")
        if len(attachment_ids) > 1:
            extension = ".zip"
            filename = self.get_name_attachment(model, gima_certification, extension)
            content = attachments._build_zip_from_attachments()
        else:
            attachment = attachments[0]
            extension = "." + attachment.mimetype.split("/")[1]
            content = base64.b64decode(attachment.datas)
            filename = self.get_name_attachment(model, gima_certification, extension)
        headers = self._get_headers(content, filename, extension.replace(".", " "))
        return request.make_response(content, headers)

    # -------------------------- COURSES-TRAINING

    def _get_training_employee_searchbar_sortings(self):
        return {
            "partner": {"input": "partner_id", "label": _("Search in Partner")},
            "course": {
                "input": "course_id",
                "label": _("Search in Courses"),
            },
        }

    def _prepare_training_domain(self, partner):
        return [("partner_id", "in", partner.child_ids.ids)]

    def _prepare_training_portal_rendering_values(
            self,
            page=1,
            date_begin=None,
            date_end=None,
            sortby=None,
            groupby=None,
            filterby=None,
            search_in=None,
            search=None,
            **kwargs,
    ):

        model = "gima.training"
        GimaTraining = request.env[model]
        if not search_in:
            search_in = "partner_id"
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        partner_ids = partner.child_ids.ids
        if kwargs.get('course_type'):
            macro_course_obj = request.env['gima.macro.course'].search([('code', '=', kwargs.get('course_type'))],
                                                                       limit=1)
            values['course_type'] = kwargs.get('course_type')

        values['type'] = 'training'
        values['partner_id'] = partner
        domain = self._prepare_training_domain(partner)
        if macro_course_obj:
            domain += [
                ("type_course_id", "=", macro_course_obj.id)
            ]
            values['page_name'] = macro_course_obj.name + " | GIMA Progetti"
            values['macro_course'] = macro_course_obj.name
        searchbar_inputs = self._get_training_employee_searchbar_sortings()

        # search
        if search and search_in:
            search_domain = []
            if search_in == "partner_id":
                partners = (
                    request.env["res.partner"]
                    .sudo()
                    .search([("name", "ilike", search)])
                )
                search_domain = OR(
                    [search_domain, [("partner_id", "in", partners.ids)]]
                )
            if search_in == "course_id":
                courses = (
                    request.env["gima.course"]
                    .sudo()
                    .search([("name", "ilike", search)])
                )
                search_domain = OR(
                    [
                        search_domain,
                        [
                            ("course_id", "in", courses.ids),
                        ],
                    ]
                )
            # if search_in == "certificate_number":
            #     search_domain = OR(
            #         [search_domain, [("certificate_number", "ilike", search)]]
            #     )
            domain = AND([domain, search_domain])

        url = "/my/company_training/" + str(kwargs.get("course_type"))
        pager_values = portal_pager(
            url=url,
            total=GimaTraining.search_count(domain),
            page=page,
            step=20,
            url_args={
                "search_in": search_in,
                "search": search,
            },
        )

        trainings = GimaTraining.search(
            domain, limit=20, offset=pager_values["offset"]
        )

        # for certification in types_group_list:
        #     if certification.get('type'):
        #         certification['type'] = _._get_translation(certification['type'])
        values.update(
            {
                "trainings": trainings,
                "pager": pager_values,
                "default_url": url,
                "searchbar_inputs": searchbar_inputs,
                "search_in": search_in,
                "search": search,
            }
        )

        return values

    @http.route(["/my/company_training"], type="http", auth="user", website=True)
    def my_training_home(self, **kwargs):
        values = self._prepare_portal_layout_values()
        # VISIBLITY OF BUTTONS IN PORTAL HOMEPAGE
        courses = {}
        for macro_course in request.env.user.partner_id.gima_macro_course_ids:
            courses[macro_course.code] = True
        values['courses'] = courses
        return request.render("gima_partner.portal_my_training", values)

    @http.route(
        ["/my/company_training/<string:course_type>"],
        type="http",
        auth="user",
        website=True,
    )
    def my_training_course(self, **kwargs):
        values = self._prepare_training_portal_rendering_values(**kwargs)
        return request.render("gima_partner.portal_my_courses", values)

    # -------------------------- DOCUMENTS

    @http.route(
        ["/my/company_documents"],
        type="http",
        auth="user",
        website=True,
    )
    def my_company_documents(self, **kwargs):
        return request.render("gima_partner.portal_my_documents")

    def _prepare_documents_portal_rendering_values(self, **kwargs):
        values = self._prepare_portal_layout_values()
        values['page_name'] = "Documents | GIMA Progetti"
        values['type'] = "documents"
        if kwargs.get('type_document') == 'pos':
            values['page_name'] = "POS | GIMA Progetti"
        if kwargs.get('type_document') == 'dvr':
            values['page_name'] = "DVR | GIMA Progetti"
        if kwargs.get('type_document') == 'medical_visits':
            values['page_name'] = (_("MEDICAL VISITS | GIMA Progetti"))
        return values

    @http.route(
        ["/my/company_document/<type_document>",
         "/my/company_document/<type_document>/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def my_company_documents_all(self, **kwargs):
        values = self._prepare_documents_portal_rendering_values(**kwargs)
        return request.render("gima_partner.portal_view_certifications", values)

    # -------------------------- PROMOTER - PORTAL

    def _get_training_searchbar_sortings(self):
        return {
            "course_id": {"label": _("Course"), "training": "course_id asc"},
        }, {
            "none": {"input": "none", "label": _("None")},
            "partner_id": {"input": "partner_id", "label": _("Employee")},
            "course_id": {"input": "course_id", "label": _("Course")}
        }, {
            "all": {"label": _("All"), "domain": []},
            "expiration_1_month: ": {
                "label": _("Expiration: 1 month"),
                "domain": [
                    ("expiration_date", "!=", False),
                    (
                        "expiration_date",
                        "<=",
                        (datetime.datetime.now() + relativedelta(months=1)).date(),
                    ),
                ],
            },
        }, {
            "partner": {"input": "partner_id", "label": _("Search in Partner")},
            # "certificate_number": {
            #     "input": "certificate_number",
            #     "label": _("Search in Certification"),
            # },
        }

    def _prepare_company_employees_training_portal_rendering_values(
            self,
            page=1,
            date_begin=None,
            date_end=None,
            sortby=None,
            groupby=None,
            filterby=None,
            search_in=None,
            search=None,
            **kwargs,
    ):
        model = "gima.training"
        GimaTraining = request.env[model]

        if not sortby:
            sortby = "course_id"
        if not groupby:
            groupby = "partner_id"
        if not filterby:
            filterby = "all"
        if not search_in:
            search_in = "partner_id"
        company = request.env['res.partner'].sudo().browse(kwargs.get("company_id"))
        values = self._prepare_portal_layout_values()
        domain = self._prepare_certification_domain(company)
        # company is a RES.PARTNER with is_company == True
        searchbar_sortings, searchbar_groupby, searchbar_filters, searchbar_inputs = self._get_training_searchbar_sortings()

        if filterby:
            domain += searchbar_filters[filterby]["domain"]

        type_group_by = searchbar_groupby.get(groupby, {})
        if groupby in ("partner_id", "course_id"):
            type_group_by = type_group_by.get("input")
        else:
            type_group_by = ""

        sort_order = searchbar_sortings[sortby]["training"]

        # search
        if search and search_in:
            search_domain = []
            if search_in == "partner_id":
                partners = (
                    request.env["res.partner"]
                    .sudo()
                    .search([("name", "ilike", search)])
                )
                search_domain = OR(
                    [search_domain, [("partner_id", "in", partners.ids)]]
                )
            if search_in == "content":
                partners = (
                    request.env["res.partner"]
                    .sudo()
                    .search([("name", "ilike", search)])
                )
                search_domain = OR(
                    [
                        search_domain,
                        [
                            "|",
                            "|",
                            ("name", "ilike", search),
                            ("certificate_number", "ilike", search),
                            ("partner_id", "in", partners.ids),
                        ],
                    ]
                )
            if search_in == "certificate_number":
                search_domain = OR(
                    [search_domain, [("certificate_number", "ilike", search)]]
                )
            domain = AND([domain, search_domain])

        url = "/my/company_management/" + str(kwargs.get("company_id"))
        pager_values = portal_pager(
            url=url,
            total=GimaTraining.sudo().search_count(domain),
            page=page,
            step=20,
            url_args={
                "sortby": sortby,
                "search_in": search_in,
                "search": search,
                "groupby": groupby,
                "filterby": filterby,
            },
        )

        gima_employee_training = GimaTraining.sudo().search(
            domain, order=sort_order, limit=20, offset=pager_values["offset"]
        )
        if type_group_by:
            types_group_list = [
                {
                    "group_by": k.name,
                    "trainings": GimaTraining.concat(*g),
                }
                for k, g in groupbyeleme(gima_employee_training, itemgetter(type_group_by))
            ]
        else:
            types_group_list = [{"trainings": gima_employee_training}]

        values.update(
            {
                "grouped_training": types_group_list,
                "pager": pager_values,
                "default_url": url,
                "searchbar_sortings": searchbar_sortings,
                "searchbar_groupby": searchbar_groupby,
                "searchbar_filters": searchbar_filters,
                "searchbar_inputs": searchbar_inputs,
                "sortby": sortby,
                "groupby": groupby,
                "filterby": filterby,
                "search_in": search_in,
                "search": search,
            }
        )

        return values

    @http.route(["/my/company_management"], type="http", auth="user", website=True)
    def my_company_management_home(self, **kwargs):
        values = self._prepare_portal_layout_values()
        companies_management = []
        user_partner = request.env.user.partner_id
        companies = request.env["res.partner"].sudo().search(
            [("promoter_id", "=", user_partner.id)]
        )
        # Calcolo delle commissioni per ciascuna azienda
        for company in companies:
            total_commission = 0.0
            # Ricerca dei corsi erogati all'azienda
            trainings = request.env["gima.training"].search(
                [("partner_id", "in", company.child_ids.ids)]
            )
            # Calcolo della commissione per ogni corso
            for training in trainings:
                total_commission += training.product_price * (user_partner.commission_percentage / 100.0)

            # Aggiunta delle informazioni all'oggetto di gestione
            companies_management.append({
                'id': company.id,
                'name': company.name,
                'total_commission': total_commission
            })

        values['companies'] = companies_management
        return request.render("gima_partner.portal_my_management_home", values)

    @http.route(
        ["/my/company_management/<int:company_id>"],
        type="http",
        auth="user",
        website=True,
    )
    def my_training(self, **kwargs):
        values = self._prepare_company_employees_training_portal_rendering_values(**kwargs)
        return request.render("gima_partner.portal_promoter_my_company", values)
