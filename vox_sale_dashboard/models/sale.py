# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from collections import defaultdict, Counter
import datetime
from datetime import datetime
from lxml import etree
import simplejson  # If not installed, you have to install it by executing pip install simplejson


class SaleReport(models.Model):
    _inherit = "sale.report"


    def _select_sale(self, fields=None):
        if not fields:
            fields = {}
        select_ = """
            min(l.id) as id,
            l.product_id as product_id,
            l.name as product_name,
            t.uom_id as product_uom,
            CASE WHEN l.name IS NOT NULL THEN sum(l.product_uom_qty / u.factor * u2.factor) ELSE 0 END as product_uom_qty,
            CASE WHEN l.name IS NOT NULL THEN sum(l.qty_delivered / u.factor * u2.factor) ELSE 0 END as qty_delivered,
            CASE WHEN l.name IS NOT NULL THEN SUM((l.product_uom_qty - l.qty_delivered) / u.factor * u2.factor) ELSE 0 END as qty_to_deliver,
            CASE WHEN l.name IS NOT NULL THEN sum(l.qty_invoiced / u.factor * u2.factor) ELSE 0 END as qty_invoiced,
            CASE WHEN l.name IS NOT NULL THEN sum(l.qty_to_invoice / u.factor * u2.factor) ELSE 0 END as qty_to_invoice,
            CASE WHEN l.name IS NOT NULL THEN sum(l.price_total_val / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) ELSE 0 END as price_total,
            CASE WHEN l.name IS NOT NULL THEN sum(l.price_included / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) ELSE 0 END as price_subtotal,
            CASE WHEN l.name IS NOT NULL THEN sum(l.untaxed_amount_to_invoice / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) ELSE 0 END as untaxed_amount_to_invoice,
            CASE WHEN l.name IS NOT NULL THEN sum(l.untaxed_amount_invoiced / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) ELSE 0 END as untaxed_amount_invoiced,
            count(*) as nbr,
            s.name as name,
            s.date_order as date,
            s.state as state,
            s.partner_id as partner_id,
            s.user_id as user_id,
            s.company_id as company_id,
            s.campaign_id as campaign_id,
            s.medium_id as medium_id,
            s.source_id as source_id,
            extract(epoch from avg(date_trunc('day',s.date_order)-date_trunc('day',s.create_date)))/(24*60*60)::decimal(16,2) as delay,
            t.categ_id as categ_id,
            s.pricelist_id as pricelist_id,
            s.analytic_account_id as analytic_account_id,
            s.team_id as team_id,
            p.product_tmpl_id,
            partner.country_id as country_id,
            partner.industry_id as industry_id,
            partner.commercial_partner_id as commercial_partner_id,
            CASE WHEN l.name IS NOT NULL THEN sum(p.weight * l.product_uom_qty / u.factor * u2.factor) ELSE 0 END as weight,
            CASE WHEN l.name IS NOT NULL THEN sum(p.volume * l.product_uom_qty / u.factor * u2.factor) ELSE 0 END as volume,
            l.discount as discount,
            CASE WHEN l.name IS NOT NULL THEN sum((l.price_unit * l.product_uom_qty * l.discount / 100.0 / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END))ELSE 0 END as discount_amount,
            s.id as order_id
        """

        for field in fields.values():
            select_ += field
        return select_



    def _group_by_sale(self, groupby=''):
        res = super()._group_by_sale(groupby)
        res += """,l.name"""
        return res