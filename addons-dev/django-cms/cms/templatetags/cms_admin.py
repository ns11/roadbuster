# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from classytags.core import Tag
from classytags.helpers import InclusionTag

from django import template
from django.conf import settings
from django.contrib.admin.views.main import ERROR_FLAG
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils.translation import get_language, ugettext_lazy as _

from cms.utils import i18n
from cms.utils.urlutils import admin_reverse


register = template.Library()

CMS_ADMIN_ICON_BASE = "%sadmin/img/" % settings.STATIC_URL


@register.simple_tag(takes_context=False)
def get_admin_url_for_language(page, language):
    if language not in page.get_languages():
        admin_url = admin_reverse('cms_pagecontent_add')
        admin_url += '?cms_page={}&language={}'.format(page.pk, language)
        return admin_url

    page_content = page.get_title_obj(language, fallback=False)
    return admin_reverse('cms_pagecontent_change', args=[page_content.pk])


@register.simple_tag(takes_context=True)
def show_admin_menu_for_pages(context, descendants, depth=1):
    admin = context['admin']
    request = context['request']

    if 'tree' in context:
        filtered = context['tree']['is_filtered']
    else:
        filtered = False

    rows = admin.get_tree_rows(
        request,
        pages=descendants,
        language=context['preview_language'],
        depth=depth,
        follow_descendants=not bool(filtered),
    )
    return mark_safe(''.join(rows))


@register.simple_tag(takes_context=False)
def get_page_display_name(cms_page):
    from cms.models import EmptyPageContent
    language = get_language()

    if not cms_page.title_cache:
        cms_page.set_translations_cache()

    if not cms_page.title_cache.get(language):
        fallback_langs = i18n.get_fallback_languages(language)
        found = False
        for lang in fallback_langs:
            if cms_page.title_cache.get(lang):
                found = True
                language = lang
        if not found:
            language = None
            for lang, item in cms_page.title_cache.items():
                if not isinstance(item, EmptyPageContent):
                    language = lang
    if not language:
        return _("Empty")
    title = cms_page.title_cache[language]
    if title.title:
        return title.title
    if title.page_title:
        return title.page_title
    if title.menu_title:
        return title.menu_title
    return cms_page.get_slug(language)


@register.simple_tag(takes_context=True)
def tree_publish_row(context, page, language):
    cls = "cms-pagetree-node-state cms-pagetree-node-state-empty empty"
    text = _("no content")

    if page.title_cache.get(language):
        cls = "cms-pagetree-node-state cms-pagetree-node-state-published published"
        text = _("has contents")

    return mark_safe(
        '<span class="cms-hover-tooltip cms-hover-tooltip-left cms-hover-tooltip-delay %s" '
        'data-cms-tooltip="%s"></span>' % (cls, force_text(text)))


@register.inclusion_tag('admin/cms/page/tree/filter.html')
def render_filter_field(request, field):
    params = request.GET.copy()

    if ERROR_FLAG in params:
        del params['ERROR_FLAG']

    lookup_value = params.pop(field.html_name, [''])[-1]

    def choices():
        for value, label in field.field.choices:
            queries = params.copy()

            if value:
                queries[field.html_name] = value
            yield {
                'query_string': '?%s' % queries.urlencode(),
                'selected': lookup_value == value,
                'display': label,
            }
    return {'field': field, 'choices': choices()}


@register.filter
def boolean_icon(value):
    BOOLEAN_MAPPING = {True: 'yes', False: 'no', None: 'unknown'}
    return mark_safe(
        '<img src="%sicon-%s.gif" alt="%s" />' % (CMS_ADMIN_ICON_BASE, BOOLEAN_MAPPING.get(value, 'unknown'), value))


class PageSubmitRow(InclusionTag):
    name = 'page_submit_row'
    template = 'admin/cms/page/submit_row.html'

    def get_context(self, context):
        opts = context['opts']
        change = context['change']
        is_popup = context['is_popup']
        save_as = context['save_as']
        language = context.get('language', '')
        filled_languages = context.get('filled_languages', [])
        context = {
            'show_delete_link': False,
            'show_save_as_new': not is_popup and change and save_as,
            'show_save_and_add_another': False,
            'show_save_and_continue': not is_popup and context['has_change_permission'],
            'is_popup': is_popup,
            'show_save': True,
            'language': language,
            'language_is_filled': language in filled_languages,
            'object_id': context.get('object_id', None),
            'opts': opts,
        }
        return context


register.tag(PageSubmitRow)


def in_filtered(seq1, seq2):
    return [x for x in seq1 if x in seq2]


in_filtered = register.filter('in_filtered', in_filtered)


@register.simple_tag
def admin_static_url():
    """
    If set, returns the string contained in the setting ADMIN_MEDIA_PREFIX, otherwise returns STATIC_URL + 'admin/'.
    """
    return getattr(settings, 'ADMIN_MEDIA_PREFIX', None) or ''.join([settings.STATIC_URL, 'admin/'])


class CMSAdminIconBase(Tag):
    name = 'cms_admin_icon_base'

    def render_tag(self, context):
        return CMS_ADMIN_ICON_BASE


register.tag(CMSAdminIconBase)


@register.inclusion_tag('admin/cms/page/plugin/submit_line.html', takes_context=True)
def submit_row_plugin(context):
    """
    Displays the row of buttons for delete and save.
    """
    opts = context['opts']
    change = context['change']
    is_popup = context['is_popup']
    save_as = context['save_as']
    ctx = {
        'opts': opts,
        'show_delete_link': context.get('has_delete_permission', False) and change and context.get('show_delete', True),
        'show_save_as_new': not is_popup and change and save_as,
        'show_save_and_add_another': context['has_add_permission'] and not is_popup and (not save_as or context['add']),
        'show_save_and_continue': not is_popup and context['has_change_permission'],
        'is_popup': is_popup,
        'show_save': True,
        'preserved_filters': context.get('preserved_filters'),
    }
    if context.get('original') is not None:
        ctx['original'] = context['original']
    return ctx
