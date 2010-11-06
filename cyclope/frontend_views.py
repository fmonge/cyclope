#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2010 Código Sur - Nuestra América Asoc. Civil / Fundación Pacificar.
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
cyclope.frontend_views
----------------------
"""

from django.utils.translation import ugettext_lazy as _
from django.template import loader, RequestContext, Template, Context
from django.contrib.sites.models import Site

from cyclope import settings as cyc_settings
from cyclope.core import frontend
from cyclope.core.collections.models import Collection, Category
from cyclope.models import Menu, MenuItem
from cyclope.utils import template_for_request
import cyclope.settings as cyc_settings


class MenuRootItemsList(frontend.FrontendView):
    """A list view of the root MenuItems for a given Menu.
    """
    name='root_items_list'
    verbose_name=_('list of root items for the selected Menu')
    is_default = True
    is_region_view = True

#BORRAR \/
    is_content_view = True

    def get_response(self, request, host_template, content_object):
        menu_items = MenuItem.tree.filter(menu=content_object,
                                          level=0, active=True)
        current_url = request.path_info[1:].split('/')[0]
        c = RequestContext(request, {'menu_items': menu_items,
                                     'current_url': current_url})
        t = loader.get_template("cyclope/menu_flat_items_list.html")
        c['host_template'] = host_template
        return t.render(c)

frontend.site.register_view(Menu, MenuRootItemsList)


class MenuFlatItemsList(frontend.FrontendView):
    """A flat list view of all the MenuItems for a given Menu.
    """
    name='flat_items_list'
    verbose_name=_('flat list of all items for the selected Menu')
    is_region_view = True

#BORRAR \/
    is_content_view = True

    def get_response(self, request, host_template, content_object):
        menu_items = MenuItem.tree.filter(menu=content_object, active=True)
        current_url = request.path_info[1:].split('/')[0]
        c = RequestContext(request, {'menu_items': menu_items,
                                     'current_url': current_url})
        t = loader.get_template("cyclope/menu_flat_items_list.html")
        c['host_template'] = host_template
        return t.render(c)

frontend.site.register_view(Menu, MenuFlatItemsList)


# TODO(nicoechaniz): refactor this view and CollectionCategoriesHierarchy which share most of their code.
class MenuMenuItemsHierarchy(frontend.FrontendView):
    """A hierarchical list view of the menu items in a menu.
    """
    name='menuitems_hierarchy'
    verbose_name=_('hierarchical list of the items in the selected menu')
    is_region_view = True

#BORRAR \/
    is_content_view = True

    def get_response(self, request, host_template, content_object):
        menu = content_object
        menu_items = MenuItem.tree.filter(menu=menu, level=0)
        menu_items_list = []
        for item in menu_items:
            menu_items_list.extend(self._get_menuitems_nested_list(item))
        c = RequestContext(request, {'menu_items': menu_items_list,
                                     'menu_slug': menu.slug})
        t = loader.get_template("cyclope/menu_menuitems_hierarchy.html")
        c['host_template'] = host_template
        return t.render(c)

    def _get_menuitems_nested_list(self, base_item, name_field='name'):
        """Creates a nested list to be used with unordered_list template tag
        """
        #TODO(nicoechaniz): see if there's a more efficient way to build this recursive template data.
        from django.template import Template, Context
        link_template = Template(
             '{% if menu_item.custom_url %}'
             '   <a href="{{menu_item.url}}">'
             '{% else %}'
             '   <a href="/{{CYCLOPE_PREFIX}}{{menu_item.url}}">'
             '{% endif %}'
             '<span>{{ menu_item.name }}</span>'
             '</a>'
            )
        nested_list = []
        for child in base_item.get_children():
            if child.get_descendant_count()>0:
                nested_list.extend(self._get_menuitems_nested_list(
                    child, name_field=name_field))
            else:
                name = getattr(child, name_field)
                nested_list.append(link_template.render(
                    Context({'menu_item': child})))

        name = getattr(base_item, name_field)
        include = link_template.render(
            Context({'menu_item': base_item}))
        if nested_list:
            return [include, nested_list]
        else:
            return [include]

frontend.site.register_view(Menu, MenuMenuItemsHierarchy)


class MenuItemChildrenOfCurrentItem(frontend.FrontendView):
    """List view of all the sub-items for the currently selected MenuItem
    """
    name='children_list'
    verbose_name=_('list view of children of the current menu item')
    is_default = True
    is_instance_view = False
    is_region_view = True

    def get_response(self, request, host_template):
        base_url = request.path_info[1:].split('/')[0]
        if base_url == '':
            current_item = MenuItem.tree.filter(site_home=True)
        else:
            current_item = MenuItem.tree.filter(url=base_url)

        if current_item:
            children = current_item[0].get_children()

            c = RequestContext(request, {'menu_items': children })
            t = loader.get_template("cyclope/menu_flat_items_list.html")
            c['host_template'] = host_template
            return t.render(c)
        else:
            return ''

frontend.site.register_view(MenuItem, MenuItemChildrenOfCurrentItem)

class SiteMap(frontend.FrontendView):
    """Show an expanded hierarchical list of all collection and menus
    """
    name='map'
    verbose_name=_('expanded hierarchical list of all collection and menus')
    is_default = True
    is_instance_view = False
    is_content_view = True

    def get_response(self, request, host_template):

        collections_list = []
        for collection in Collection.objects.filter(visible=True):
            category_list = []
            for category in Category.tree.filter(collection=collection, level=0):
                # TODO(diegoM): Change this line when the refactorization is done
                category_list.extend(self._get_categories_nested_list(category))
            t = Template('{{ category }} <a href="{% url category_feed category.slug %}">'
                         '<img src="{{ media_url }}images/css/rss_logo.png"/></a>')
            include = t.render(Context({'category':category,
                                        'media_url':cyc_settings.CYCLOPE_THEME_MEDIA_URL}))
            collections_list.extend([include,category_list])

        menus_list = []
        for menu in Menu.objects.all():
            menu_items_list = []
            for item in MenuItem.tree.filter(menu=menu, level=0):
                # TODO(diegoM): Change this line when the refactorization is done
                menu_items_list.extend(MenuMenuItemsHierarchy()._get_menuitems_nested_list(item))
            menus_list.extend([menu.name, menu_items_list])

        c = RequestContext(request, {'collections':collections_list,
                                     'menus':menus_list})
        t = loader.get_template("cyclope/site_map.html")
        c['host_template'] = host_template
        return t.render(c)

    def _get_categories_nested_list(self, base_category, name_field='name'):

        """Creates a nested list to be used with unordered_list template tag
        """
        #TODO(nicoechaniz): see if there's a more efficient way to build this recursive template data.
        link_template = Template(
            '{% if has_children %}'
              '<span class="expand_collapse">+</span>\n'
            '{% endif %}'
            '{% if has_content %}'
              '<a href="{% url category-teaser_list slug %}">'
                 '<span>{{ name }}</span></a>'
            '{% else %} {{ name }}'
            '{% endif %}'
            ' <a href="{% url category_feed slug %}">'
            '<img src="{{ media_url }}images/css/rss_logo.png"/></a>'
            )
        nested_list = []
        for child in base_category.get_children():
            if child.get_descendant_count()>0:
                nested_list.extend(self._get_categories_nested_list(
                    child, name_field=name_field))
            else:
                name = getattr(child, name_field)
                has_content = child.categorizations.exists()
                nested_list.append(link_template.render(
                    Context({'name': name,
                             'slug': child.slug,
                             'has_content': has_content,
                             'media_url':cyc_settings.CYCLOPE_THEME_MEDIA_URL,})))

        name = getattr(base_category, name_field)
        has_content = base_category.categorizations.exists()
        include = link_template.render(
            Context({'name': name,
                     'slug': base_category.slug,
                     'has_content': has_content,
                     'has_children': base_category.get_descendant_count(),
                     'media_url':cyc_settings.CYCLOPE_THEME_MEDIA_URL,}))
        if nested_list:
            return [include, nested_list]
        else:
            return [include]
frontend.site.register_view(Site, SiteMap)


