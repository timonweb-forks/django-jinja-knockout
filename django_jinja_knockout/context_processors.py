from pyquestpc import sdv
from django.conf import settings
from django.utils.html import format_html, force_text, escape
from django.core.urlresolvers import reverse
from django.templatetags.static import static
from django.forms.utils import flatatt
from django.middleware.csrf import get_token
from .models import get_verbose_name, ContentTypeLinker
from .tpl import add_css_classes, reverseq


LAYOUT_CLASSES = {'label': 'col-md-3', 'field': 'col-md-7'}

def raise_helper(msg):
    raise Exception(msg)


class TemplateContextProcessor():

    CLIENT_ROUTES = ()

    def __init__(self, HttpRequest=None):
        self.user_id = 0
        self.HttpRequest = HttpRequest

    def skip_request(self):
        """
        Will be called for application response() views.
        Currently is used only with jinja2 templates to do not interfere with django.admin.
        """
        return self.HttpRequest is None or not hasattr(self.HttpRequest, 'client_data')

    def get_user_id(self):
        return self.HttpRequest.user.pk \
            if self.HttpRequest.user.is_authenticated() and self.HttpRequest.user.is_active \
            else 0

    def get_context_data(self):
        if self.skip_request():
            return {}
        self.user_id = self.get_user_id()
        client_conf = {
            'csrfToken': get_token(self.HttpRequest),
            'staticPath': static(''),
            'userId': self.user_id,
        }
        client_conf['url'] = {}
        for url, is_anon in self.__class__.CLIENT_ROUTES:
            if is_anon or self.user_id != 0:
                client_conf['url'][url] = reverse(url)
        return {
            'add_css_classes': add_css_classes,
            'client_data': self.HttpRequest.client_data,
            'client_conf': client_conf,
            'ContentTypeLinker': ContentTypeLinker,
            'escape': escape,
            'getattr': getattr,
            'get_verbose_name': get_verbose_name,
            'flatatt': flatatt,
            'format_html': format_html,
            'force_text': force_text,
            'isinstance': isinstance,
            'layout_classes': getattr(settings, 'LAYOUT_CLASSES', LAYOUT_CLASSES),
            'request': self.HttpRequest,
            'raise': raise_helper,
            # Use url() provided by django-jinja for reverse without query args.
            'reverseq': reverseq,
            'sdv_dbg': sdv.dbg,
            'str': str,
        }


# Inherit and extend TemplateContextProcessor class if you want to pass more data to Jinja2 templates.
def template_context_processor(HttpRequest=None):
    return TemplateContextProcessor(HttpRequest).get_context_data()
