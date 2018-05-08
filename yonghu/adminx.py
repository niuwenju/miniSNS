# _*_ coding: utf-8 _*_
import xadmin
from xadmin import views

class GlobalSettings(object):
    site_title = "社交后台管理"
    site_footer = "社交"
    menu_style = "accordion"


xadmin.site.register(views.CommAdminView,GlobalSettings)