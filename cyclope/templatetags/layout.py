#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2010-2013 Código Sur Sociedad Civil.
# All rights reserved.
#
# This file is part of Cyclope.
#
# Cyclope is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Cyclope is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
templatetags.layout
-------------------

Template tags to mark regions in a template, which enable the configuration
of different Layouts.
"""
import json

from django import template
from django.contrib.contenttypes.models import ContentType

from cyclope.utils import layout_for_request, get_or_set_cache
from cyclope.core import frontend
from cyclope.models import SiteSettings
from cyclope.utils import layout_for_request, LazyJSONEncoder
from cyclope.themes import get_theme

register = template.Library()

@register.inclusion_tag('cyclope/region.html', takes_context=True)
def region(context, region_name):
    """Defines a region where views can be inserted in a template.

    The views that will actualy be inserted are defined in a Layout.

    Usage::

        {% region 'region_name' %}

    The region name must be one of the regions available to the template
    according to the theme configuration (as defined in the theme's __init__ file)

    """

    theme = get_theme(SiteSettings.objects.get().theme)

    region_ids = ""
    if hasattr(theme, "region_layout_ids"):
        # if region_ids are defined return them otherwise return empty
        region_ids = theme.region_layout_ids.get(region_name, "")
    
    region_classes = ""
    if hasattr(theme, "region_layout_classes"):
        # if content_classes are defined return them otherwise return empty
        region_classes = theme.region_layout_classes.get(region_name, "")
        
    # if we have a layout in the context use that one, otherwise guess it from the request
    layout = context.get('layout', layout_for_request(context['request']))
    region_vars = {'layout_name': layout.slug,
                   'region_name': region_name,
                   'region_layout_ids': region_ids,
                   'region_layout_classes': region_classes}

    regionviews = layout.regionview_set.filter(
        region=region_name).order_by('weight')
    views = []


    for regionview in regionviews:
        view_vars={}
        view = frontend.site.get_view(
            regionview.content_type.model_class(),
            regionview.content_view,
            )
        # instance views need instance data -> slug
        if view.is_instance_view:
            if regionview.content_object is None:
                raise template.TemplateSyntaxError
            slug = regionview.content_object.slug
            view_vars['output'] = view(context['request'], region_name=region_name,
                                       content_object=regionview.content_object,
                                       view_options=regionview.view_options)
            view_vars['slug'] = slug
        else:
            view_vars['output'] = view(context['request'], region_name=region_name,
                                       view_options=regionview.view_options)
        view_vars['name'] = regionview.content_view
        view_vars['model'] = regionview.content_type.model
        views.append(view_vars)

    region_vars['views'] = views

    return region_vars

@register.simple_tag
def layout_regions_data():
    """
    Builds a json object to embed on the admin's change_form of Layout. This
    object contains all the available views and regions for all templates.
    """
    theme_name = SiteSettings.objects.get().theme
    theme_settings = get_theme(theme_name)
    out_dict = {}
    layout_templates = {}
    for name, dic_ in theme_settings.layout_templates.iteritems():
        regions = dic_['regions']
        regions_data = [{'region_name': '', 'verbose_name': '------'}]
        items = sorted(regions.items(), key = lambda region: region[1]['weight'])    
        for region_name, data in items:
            if region_name != 'content':
                regions_data.extend([{'region_name': region_name,'verbose_name': data['name']}])
                            
        layout_templates[name] = regions_data
        
    out_dict["layout_templates"] = layout_templates

    views_for_models = {}
    models = frontend.site.get_all_registry_models()
    for model in models:
        views = [{'view_name': '', 'verbose_name': '------'}]
        views.extend([{'view_name': view.name,
                       'verbose_name': view.verbose_name}
                       for view in frontend.site.get_views(model)
                       if view.is_region_view])
        ctype = ContentType.objects.get_for_model(model)
        views_for_models[ctype.pk] = views
    out_dict["views_for_models"] = views_for_models
    json_data = json.dumps(out_dict, cls=LazyJSONEncoder)
    return json_data
    
@register.simple_tag
def bootstrap_skin_link():
    """
    Returns CSS link to the configured Bootswatch skin
    https://github.com/thomaspark/bootswatch
    """
    from cyclope import settings
    url = settings.CYCLOPE_THEME_MEDIA_URL
    path = "css/"
    skin = SiteSettings.objects.get().skin_setting
    if skin != 'bootstrap':
        path += 'skins/'
    link = '<link href="{}{}{}.min.css" rel="stylesheet">'.format(url, path, skin)
    return link
