import os

from aspen.utils import Canonizer
from aspen.website import Website


website = Website([])
canonize = Canonizer(os.environ['CANONICAL_LOCATION'])
website.algorithm.insert_after('parse_environ_into_request', canonize)
