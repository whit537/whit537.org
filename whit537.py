import datetime
import os
import re

import tree
from aspen.utils import Canonizer
from aspen.website import Website


website = Website([])
website.renderer_default = 'unspecified'  # require explicit renderer, to avoid escaping bugs
website.default_renderers_by_media_type['text/html'] = 'jinja2'
website.default_renderers_by_media_type['text/plain'] = 'jinja2'


canonize = Canonizer(os.environ['CANONICAL_LOCATION'])


def render_published(published):
    if re.match('^.*-\d\d:\d\d$', published) is not None:
        published = published[:-6]
    out = datetime.datetime.strptime(published, '%Y-%m-%dT%H:%M:%S.%f')
    out = out.strftime('%B %d, %Y')
    out = out.replace(' 0', ' ')
    return out


def add_stuff(request):
    request.context['render_published'] = render_published


tree.startup(website)

website.algorithm.insert_after('parse_environ_into_request', canonize)
website.algorithm.insert_after('canonize', add_stuff)
