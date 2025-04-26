import sys
import os
import pytest 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.calculations import add, Bankaccount, Insufficient_Funds


@pytest.mark.parametrize("num1, num2, expected",[
    (1,2,3),
    (4,5,9),
    (10,21,31)                                                 
                                                 ])
def test_add(num1, num2, expected):
    assert add(num1,num2) == expected 


@pytest.fixture
def bank_account():
    return Bankaccount(1000)

def test_bank_amount(bank_account):   #Adding in a ficture
    assert bank_account.balance == 1000

def test_exception(bank_account):   #Adding in a ficture
    #with pytest.raises(Exception):
    with pytest.raises(Exception):
        assert bank_account.withdraw(1001) == 1000

#def test_add(num1, num2, expected):
#    print("testing add funton")
#    sum = add(1,2)
#    assert sum == 3 


#test_add()