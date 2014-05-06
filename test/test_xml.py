from lxml import etree
from tools import GenericMoncovTest
from tools import tracing_import_code_submodule as tracing_import
from moncov.stats.simple import get_stats_xml
import re


class Test(GenericMoncovTest):

    def test_01_filename(self):
        with tracing_import('./code/if_true_else', db=self.db) as module:
            pass
        xml = get_stats_xml(db=self.db, whitelist=[re.compile('.*')], blacklist=[])
        tree = etree.XML(xml)

        for i in tree.xpath('//class'):
            filename = i.xpath("./@filename")[0]
        self.assertResultFileName(filename)