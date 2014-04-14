from tools import GenericMoncovTest
from tools import tracing
from tools import code_submodule_whitelist as whitelist
from tools import tracing_import_code_submodule as tracing_import
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

    def test_06_true_fucntion_value_if_value_else(self):
        with tracing_import('function_value_if_value_else', db=self.db) as module: 
            module.function(True)
        self.assertResultBranchRate(Rate(1, 2))

    def test_06_false_fucntion_value_if_value_else(self):
        with tracing_import('function_value_if_value_else', db=self.db) as module: 
            module.function(False)
        self.assertResultBranchRate(Rate(1, 2))

    def test_07_true_false__function_value_if_value_else(self):
        with tracing_import('function_value_if_value_else', db=self.db) as module: 
            module.function(True); module.function(False)
        self.assertResultBranchRate(Rate(2, 2))

    def test_08_if_true_if_true_else(self):
        with tracing_import('if_true_if_true_else', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(2, 3))

    def test_09_while_false(self):
        with tracing_import('while_false', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(0, 1))

    def test_10_while_some(self):
        with tracing_import('while_some', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(1, 1))

    def test_11_for_empty(self):
        with tracing_import('for_empty', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(0, 1))

    def test_12_for_few(self):
        with tracing_import('for_few', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(1, 1))

    def test_13_true_true_true_false__function_a_b_if_a_if_b_else(self):
        with tracing_import('function_a_b_if_a_if_b_else', db=self.db) as module:
            module.function(True, True); module.function(True, False)
        self.assertResultBranchRate(Rate(3, 3))
        
    def test_14_for_in_for(self):
        with tracing_import('for_in_for', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(2, 2))
        
    def test_15_while_false_if_true_else(self):
        with tracing_import('while_false_if_true_else', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(0, 3))
        
    def test_16_if_false_while_some(self):
        with tracing_import('if_false_while_some', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(0, 2))
        
    def test_17_while_false_for_some(self):
        with tracing_import('while_false_for_some', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(0, 3))
