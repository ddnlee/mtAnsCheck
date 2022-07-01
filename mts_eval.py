import json
from mts.answer_conversion import *
from mts.number_compare import *
from mts.poly_compare import *
from mts.pair_compare import *
from mts.eqn_compare import *
from mts.ineq_compare import *


def sympy_eval_handler(event, context):
    if context is None or event is None:
        return 'N/A'

    object = json.loads(json.dumps(event)).get('answer')
    _idx = len(object)

    print('1. answer: ', json.dumps(object))
    print('2._idx: ', _idx)

    output = '';
    for cnt in range(0, _idx):
        _id = object[cnt]['ID']
        _check_function = object[cnt]['check_function']
        _correct_answer = object[cnt]['correct_answer']
        _student_answer = object[cnt]['student_answer']

        '''
            StrCompare: 0
            PolyCompare: 1
              - order == 'Fix' # 리스트일 때 순서 고정
              
            PolyFactorCompare: 2
            PolyExpansionCompare: 3
              - order == 'Acc' / 'Dec' # 오름차순 / 내림차순
              - symbol == 'x' / 'y' 등의 문자
              
            PolyFormCompare: 4
            NumCompare: 5
              - order == 'Fix' # 리스트일 때 순서 고정
              - form == 'Fix' # 소수 != 분수, 약분 전!=후, 유리화 전!=후, 거듭제곱 전!=후, 통분 전!= 후
              
            NumPrimeFactorCompare: 6 (사용X)
            PairCompare: 7
              - order == 'Fix' # 리스트일 때 순서 고정
              
            EqCompare: 8
              - leading_coeff == 'Fix' # 최고차항 계수 고정
              
            IneqCompare: 9
            SignCompare: 10
              - order == 'Fix' # 리스트일 때 순서 고정
              
            NoSignCompare: 11
        '''

        if (len(_student_answer) > 0):
            try:
                correct_sympy, student_sympy = Ans2Sympy(_correct_answer,_student_answer, f=_check_function)
                if _check_function == 'PolyExpansionCompare':
                    _symbol = object[cnt]['symbol'] if 'symbol' in object[cnt].keys() else None
                    _order = object[cnt]['order'] if 'order' in object[cnt].keys() else None
                    result = globals()[_check_function](correct_sympy, student_sympy, _symbol, _order)
                elif _check_function == 'NumCompare':
                    _form = object[cnt]['form'] if 'form' in object[cnt].keys() else None
                    _order = object[cnt]['order'] if 'order' in object[cnt].keys() else None
                    result = globals()[_check_function](correct_sympy, student_sympy, _form, _order)
                elif _check_function in ['PolyCompare','PairCompare', 'SignCompare']:
                    _order = object[cnt]['order'] if 'order' in object[cnt].keys() else None
                    result = globals()[_check_function](correct_sympy, student_sympy, _order)
                elif _check_function == 'EqCompare':
                    _leading_coeff = object[cnt]['leading_coeff'] if 'leading_coeff' in object[cnt].keys() else None
                    result = globals()[_check_function](correct_sympy, student_sympy, _leading_coeff)
                else:
                    result = globals()[_check_function](correct_sympy, student_sympy)
            except Exception as expt:
                print(expt)
                result = 'N/A'
                pass
        else:
            result = "False"

        output += _id + ':' + str(result)
        if (cnt < _idx - 1):
            output += ','

    print('3.result: '+ output)

    return output


def test():
    event = {"answer": [
        {"ID": "0", "check_function": "NumCompare", "correct_answer": "1,\,2", "student_answer": "1,2",
         "form": None, "order": 'Fix', "symbol": None, "leading_coeff": None}]}
    context = 'test'
    output = sympy_eval_handler(event, context)
    print("====> output: " + output)

if __name__ == '__main__':
    test()

'''
    공통 false: 동류항 정리 안 한 답(x+x, 1+1), 계수 1 생략 안 한 답(1*x, -1*2, 3/1) 
    ** NumCompare **
        ** form **
    true:   {"ID": "0", "check_function": "NumCompare", "correct_answer": "0.5", "student_answer": "(1)/(2)",
            "form": None, "order": None, "symbol" : None, "leading_coeff" : None}

    false:  {"ID": "0", "check_function": "NumCompare", "correct_answer": "0.5", "student_answer": "(1)/(2)",
                "form": 'Fix', "order": None, "symbol" : None, "leading_coeff" : None}
        ** order **
    true:   {"ID": "0", "check_function": "NumCompare", "correct_answer": "1,2", "student_answer": "2,1",
            "form": None, "order": 'None', "symbol" : None, "leading_coeff" : None}

    false:  {"ID": "0", "check_function": "NumCompare", "correct_answer": "1,2", "student_answer": "2,1",
                "form": None, "order": 'Fix', "symbol" : None, "leading_coeff" : None}
                
    ** PolyCompare **
        ** order **
    true:   {"ID": "0", "check_function": "PolyCompare", "correct_answer": "x^2,x,1", "student_answer": "1,x**2,x",
            "form": None, "order": None, "symbol" : None, "leading_coeff" : None}

    false:  {"ID": "0", "check_function": "PolyCompare", "correct_answer": "x^2,x,1", "student_answer": "1,x**2,x",
                "form": None, "order": 'Fix', "symbol" : None, "leading_coeff" : None}
                
    ** PolyExpansionCompare **
    true:   {"ID": "0", "check_function": "PolyExpansionCompare", "correct_answer": "x^2+x", "student_answer": "x^2+x",
            "form": None, "order": None, "symbol" : None, "leading_coeff" : None}

    false:  {"ID": "0", "check_function": "PolyExpansionCompare", "correct_answer": "x^2+x", "student_answer": "x*(x+1)",
                "form": None, "order": None, "symbol" : None, "leading_coeff" : None}            
        ** order **
    true:   {"ID": "0", "check_function": "PolyExpansionCompare", "correct_answer": "x^2+x", "student_answer": "x**2+x",
            "form": None, "order": 'Dec', "symbol" : 'x', "leading_coeff" : None}
            
    false:   {"ID": "0", "check_function": "PolyExpansionCompare", "correct_answer": "x+x^2", "student_answer": "x**2+x",
            "form": None, "order": 'Acc', "symbol" : 'x', "leading_coeff" : None}
            
    ** NoSignCompare **
    true:   {"ID": "0", "check_function": "NoSignCompare", "correct_answer": "xy", "student_answer": "xy",
            "form": None, "order": None, "symbol" : None, "leading_coeff" : None}
    
    false:  {"ID": "0", "check_function": "NoSignCompare", "correct_answer": "xy", "student_answer": "x×y",
                "form": None, "order": None, "symbol" : None, "leading_coeff" : None}
                
    false:  {"ID": "0", "check_function": "NoSignCompare", "correct_answer": "0.1a", "student_answer": "0.a",
                "form": None, "order": None, "symbol" : None, "leading_coeff" : None}
'''
