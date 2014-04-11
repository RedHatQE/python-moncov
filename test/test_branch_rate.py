from tools import GenericMoncovTest
from tools import tracing
from tools import code_submodule_whitelist as whitelist
from moncov.stats.rate import Rate

class Test(GenericMoncovTest):
    def test_01_if_true(self):
        with tracing(self.db, whitelist('if_true'), []):
            import code.if_true
        self.assertResultBranchRate(Rate(1, 1))

    def test_02_if_false(self):
        with tracing(self.db, whitelist('if_false'), []):
            import code.if_false
        self.assertResultBranchRate(Rate(0))

    def test_03_if_true_else(self):
        with tracing(self.db, whitelist('if_true_else'), []):
            import code.if_true_else
        self.assertResultBranchRate(Rate(1, 2))

    def test_04_if_false_else(self):
        with tracing(self.db, whitelist('if_false_else'), []):
            import code.if_false_else
        self.assertResultBranchRate(Rate(1, 2))

    def test_05_if_true_if_true(self):
        with tracing(self.db, whitelist('if_true_if_true'), []):
            import code.if_true_if_true
        self.assertResultBranchRate(Rate(2, 2))
        
