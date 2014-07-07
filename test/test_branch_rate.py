__test__ = False # FIXME

from tools import GenericMoncovTest
from tools import tracing
from tools import code_submodule_whitelist as whitelist
from tools import tracing_import_code_submodule as tracing_import
from moncov.stats.rate import Rate

class Test(GenericMoncovTest):

    def test_01_no_branch(self):
        with tracing_import('no_branch', db=self.db) as module:
            pass
        self.assertResultBranchRate(None)

    def test_01_no_branch(self):
        with tracing_import('no_branch', db=self.db) as module:
            pass
        self.assertResultLineRate(Rate(3, 3))
    
    def test_02_empty_file(self):
        with tracing_import('empty_file', db=self.db) as module:
            pass
        self.assertResultBranchRate(None)        

    def test_03_if_true(self):
        with tracing(self.db, whitelist('if_true'), []):
            import code.if_true
        self.assertResultBranchRate(Rate(1, 1))

    def test_04_if_false(self):
        with tracing(self.db, whitelist('if_false'), []):
            import code.if_false
        self.assertResultBranchRate(Rate(0))

    def test_05_if_true_else(self):
        with tracing(self.db, whitelist('if_true_else'), []):
            import code.if_true_else
        self.assertResultBranchRate(Rate(1, 2))

    def test_06_if_false_else(self):
        with tracing_import('if_false_else', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(1, 2))

    def test_07_if_true_if_true(self):
        with tracing(self.db, whitelist('if_true_if_true'), []):
            import code.if_true_if_true
        self.assertResultBranchRate(Rate(2, 2))        
        
    def test_08_if_true_if_false(self):
        with tracing_import('if_true_if_false', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(1, 4))        
        
    def test_09_if_false_if_true_else(self):
        with tracing_import('if_false_if_true_else', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(0, 3))

    def test_10_if_true_if_true_else(self):
        with tracing_import('if_true_if_true_else', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(2, 3))  
        
    def test_11_if_false_for_some(self):
        with tracing_import('if_false_for_some', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(0, 3))
        
    def test_12_if_true_for_some_ifelse(self):
        with tracing_import('if_true_for_some_ifelse', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(2, 3))

    def test_13_if_true_for_some_ifelse_for_some(self):
        with tracing_import('if_true_for_some_ifelse_for_some', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(2, 4))

    def test_14_if_false_for_some_ifelse_for_some(self):
        with tracing_import('if_false_for_some_ifelse_for_some', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(2, 4))
        
    def test_15_if_false_while_some(self):
        with tracing_import('if_false_while_some', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(0, 2))     
        
    def test_16_if_true_while_some_ifelse(self):
        with tracing_import('if_true_while_some_ifelse', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(2, 3))
        
    def test_17_if_true_while_false_ifelse(self):
        with tracing_import('if_true_while_false_ifelse', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(1, 3))    
   
    def test_18_if_false_while_false_if_true_while_false(self):
        with tracing_import('if_false_while_false_if_true_while_false', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(1, 4)) 
        
    def test_19_while_some(self):
        with tracing_import('while_some', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(1, 1))        

    def test_20_while_false(self):
        with tracing_import('while_false', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(0, 1))          

    def test_21_while_some_if_true(self):
        with tracing_import('while_some_if_true', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(2, 2))
        
    def test_22_while_some_if_false(self):
        with tracing_import('while_some_if_false', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(1, 2))     
        
    def test_23_while_false_if_true_else(self):
        with tracing_import('while_false_if_true_else', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(0, 3))
        
    def test_24_while_some_for_some(self):
        with tracing_import('while_some_for_some', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(2, 2))
        
    def test_25_while_false_for_some(self):
        with tracing_import('while_false_for_some', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(0, 3))
        
    def test_26_while_false_while_some(self):
        with tracing_import('while_false_while_some', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(0, 2))
        
    def test_27_while_false_while_false(self):
        with tracing_import('while_false_while_false', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(0, 2))
        
    def test_28_while_some_while_some(self):
        with tracing_import('while_some_while_some', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(2, 2))
        
    def test_29_while_some_while_false(self):
        with tracing_import('while_some_while_false', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(1, 2))

    def test_30_while_false_if_false_ifelse(self):
        with tracing_import('while_false_if_false_ifelse', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(0, 3))     

    def test_31_for_empty(self):
        with tracing_import('for_empty', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(0, 1))

    def test_32_for_some(self):
        with tracing_import('for_some', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(1, 1))

    def test_33_for_some_for_some(self):
        with tracing_import('for_some_for_some', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(2, 2))
        
    def test_34_for_some_if_true_ifelse(self):
        with tracing_import('for_some_if_true_ifelse', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(2, 3))
        
    def test_35_for_some_if_false_ifelse(self):
        with tracing_import('for_some_if_false_ifelse', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(2, 3))
        
    def test_36_for_some_while_some(self):
        with tracing_import('for_some_while_some', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(2, 2))
        
    def test_37_for_some_while_false(self):
        with tracing_import('for_some_while_false', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(1, 2))
    
    def test_38_for_some_break_else(self):
        with tracing_import('for_some_break_else', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(1, 2))

    def test_39_for_empty_pass_else(self):
        with tracing_import('for_empty_pass_else', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(1, 2))

    def test_40_for_empty_break_else(self):
        with tracing_import('for_empty_break_else', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(1, 2))
        
    def test_41_for_empty_if_true_if_false_not_nested(self):
        with tracing_import('for_empty_if_true_if_false_not_nested', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(1, 3))

    def test_42_true_true_true_false__function_a_b_if_a_if_b_else(self):
        with tracing_import('function_a_b_if_a_if_b_else', db=self.db) as module:
            module.function(True, True); module.function(True, False)
        self.assertResultBranchRate(Rate(3, 3))

    def test_43_true_fucntion_value_if_value_else(self):
        with tracing_import('function_value_if_value_else', db=self.db) as module: 
            module.function(True)
        self.assertResultBranchRate(Rate(1, 2))

    def test_44_false_fucntion_value_if_value_else(self):
        with tracing_import('function_value_if_value_else', db=self.db) as module: 
            module.function(False)
        self.assertResultBranchRate(Rate(1, 2))

    def test_45_true_false__function_value_if_value_else(self):
        with tracing_import('function_value_if_value_else', db=self.db) as module: 
            module.function(True); module.function(False)
        self.assertResultBranchRate(Rate(2, 2))

    def test_46_if_true_def_if_true_else(self):
        with tracing_import('if_true_def_if_true_false', db=self.db) as module:
            pass
        self.assertResultBranchRate(Rate(2, 3))
