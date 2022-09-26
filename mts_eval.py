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

        _symbol = object[cnt]['symbol'] if 'symbol' in object[cnt].keys() else None
        _order = object[cnt]['order'] if 'order' in object[cnt].keys() else None
        _form = object[cnt]['form'] if 'form' in object[cnt].keys() else None
        _leading_coeff = object[cnt]['leading_coeff'] if 'leading_coeff' in object[cnt].keys() else None
        _de = object[cnt]['de'] if 'de' in object[cnt].keys() else None
        _sol = object[cnt]['sol'] if 'sol' in object[cnt].keys() else None
        _poly = object[cnt]['poly'] if 'poly' in object[cnt].keys() else None

        '''
            StrCompare: 0
            PolyCompare: 1
              - order == 'Fix' # 리스트일 때 순서 고정
              - form == 'Fix' # 숫자 형태 관련
            PolyFactorCompare: 2
            PolyExpansionCompare: 3
              - order == 'Acc' / 'Dec' # 오름차순 / 내림차순
              - symbol == 'x' / 'y' 등의 문자

            PolyFormCompare: 4
            NumCompare: 5
              - order == 'Fix' # 리스트일 때 순서 고정
              - form == 'Fix' # 소수 != 분수, 약분 전!=후, 거듭제곱 전!=후, 통분 전!= 후
              - de = 'Rtn' # 유리화 전!=후 (form = 'Fix'로 유리화 한 후 덧셈식으로 나타내면 False 나와서 param 추가)

            NumPrimeFactorCompare: 6 (사용X)
            PairCompare: 7
              - order == 'Fix' # 리스트일 때 순서 고정

            EqCompare: 8
              - leading_coeff == 'Fix' # 최고차항 계수 고정
              - form == 'Fix' # 숫자 형태 관련

            IneqCompare: 9
              - form == 'Fix' # 숫자 형태 관련
              - poly == 'Fix' # 한 쪽 변의 다항식이 정답과 일치(동류항 계산 여부는 정답을 따름)
              
            SignCompare: 10
              - order == 'Fix' # 리스트일 때 순서 고정

            NoSignCompare: 11
        '''

        if (len(_student_answer) > 0):
            try:
                tmp = Ans2Sympy(_correct_answer, _student_answer, f=_check_function)
                if tmp == True: result = True
                elif tmp == False: print("1* *1 /1 생략X"); result = False
                else:
                    correct_sympy, student_sympy = tmp
                    if _check_function == 'PolyExpansionCompare':
                        result = globals()[_check_function](correct_sympy, student_sympy, _symbol, _order)
                    elif _check_function in ['NumCompare']:
                        result = globals()[_check_function](correct_sympy, student_sympy, _form, _order, _de)
                    elif _check_function in ['PolyCompare']:
                        result = globals()[_check_function](correct_sympy, student_sympy, _form, _order)
                    elif _check_function in ['PairCompare', 'SignCompare']:
                        result = globals()[_check_function](correct_sympy, student_sympy, _order)
                    elif _check_function == 'EqCompare':
                        result = globals()[_check_function](correct_sympy, student_sympy, _form, _leading_coeff)
                    elif _check_function == 'IneqCompare':
                        result = globals()[_check_function](correct_sympy, student_sympy, _form, _poly)
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

    print('3.result: ' + output)

    return output


def test():
    event = {"answer": [
        {"ID": "1", "check_function": "IneqCompare", "correct_answer": "-5< 5x <5", "student_answer": "-1<x<1", "poly": "Fix"}]}

    ''' TestCase-True '''
    evt_True = {"answer": [
        # ** NumCompare **
        # ** form **
        {"ID": "1", "check_function": "NumCompare", "correct_answer": "0.5", "student_answer": "(1)/(2)"},
        # ** order **
        {"ID": "2", "check_function": "NumCompare", "correct_answer": "1,\,2", "student_answer": "1,2",
         "order": 'Fix'},
        # ** de **
        {"ID": "3", "check_function": "NumCompare", "correct_answer": r"\frac{\sqrt{6}+\sqrt{3}}{3}'", "student_answer": "sqrt(6)/3+sqrt(3)/3",
         "de": 'Rtn'},

        # ** PolyCompare **
        # ** order **
        {"ID": "4", "check_function": "PolyCompare", "correct_answer": "x^2,x,1", "student_answer": "1,x**2,x"},

        # ** PolyExpansionCompare **
        {"ID": "5", "check_function": "PolyExpansionCompare", "correct_answer": "x^2+x", "student_answer": "x^2+x"},
        # ** order **
        {"ID": "6", "check_function": "PolyExpansionCompare", "correct_answer": "x^2+x", "student_answer": "x**2+x",
         "order": 'Dec', "symbol": 'x'},

        # ** NoSignCompare **
        {"ID": "7", "check_function": "NoSignCompare", "correct_answer": "xy", "student_answer": "x*y"},

        # ** EqCompare **
        {"ID": "8", "check_function": "EqCompare", "correct_answer": "y=300x", "student_answer": "y=300*x"},

        # ** IneqCompare **
        {"ID": "9", "check_function": "IneqCompare", "correct_answer": "x\ge1", "student_answer": "x>=1"},

        # ** PolyFormCompare **
        {"ID": "10", "check_function": "PolyFormCompare", "correct_answer": "-x-\\dfrac{1}{2}x", "student_answer": "-x-1/2*x"}
    ]}

    ''' TestCase-False '''
    evt_False = {"answer": [
        # ** NumCompare **
        # ** form **
        {"ID": "1", "check_function": "NumCompare", "correct_answer": "0.5", "student_answer": "(1)/(2)",
         "form": 'Fix'},
        # ** order **
        {"ID": "2", "check_function": "NumCompare", "correct_answer": "1,\,2", "student_answer": "2,1",
         "order": 'Fix'},
        # ** de **
        {"ID": "3", "check_function": "NumCompare", "correct_answer": r"\frac{\sqrt{6}+\sqrt{3}}{3}'",
         "student_answer": "sqrt(2)/sqrt(3)+1/sqrt(3)",
         "de": 'Rtn'},

        # ** PolyCompare **
        # ** order **
        {"ID": "4", "check_function": "PolyCompare", "correct_answer": "x^2,x,1", "student_answer": "1,x**2,x",
         "order": 'Fix'},
        # ** form **
        {"ID": "5", "check_function": "PolyCompare", "correct_answer": "4000-0.5x", "student_answer": "4000-1/2*x",
         "form": 'Fix'},

        # ** PolyExpansionCompare **
        {"ID": "6", "check_function": "PolyExpansionCompare", "correct_answer": "x^2+x", "student_answer": "x*(x+1)"},
        # ** order **
        {"ID": "7", "check_function": "PolyExpansionCompare", "correct_answer": "x+x^2", "student_answer": "x**2+x",
         "order": 'Acc', "symbol": 'x'},

        # ** NoSignCompare **
        {"ID": "8", "check_function": "NoSignCompare", "correct_answer": "xy", "student_answer": "x×y"},
        {"ID": "9", "check_function": "NoSignCompare", "correct_answer": "0.1a", "student_answer": "0.a"},

        # ** EqCompare **
        {"ID": "10", "check_function": "EqCompare", "correct_answer": "y=300x", "student_answer": "2*y=2*300*x",
         "leading_coeff": "Fix"},

        # ** IneqCompare **
        {"ID": "11", "check_function": "IneqCompare", "correct_answer": "x\ge1", "student_answer": "x>1"},
        {"ID": "12", "check_function": "IneqCompare", "correct_answer": "x\gt-30", "student_answer": "-x<30", "poly": "Fix"},
        {"ID": "13", "check_function": "IneqCompare", "correct_answer": "x>6-3", "student_answer": "x+3>6", "poly": "Fix"},

        # ** PolyFormCompare **
        {"ID": "14", "check_function": "PolyFormCompare", "correct_answer": "2(x-3)^2", "student_answer": "2*(3-x)**2"}
    ]}

    context = 'test'
    # output = sympy_eval_handler(event, context)
    output = sympy_eval_handler(evt_True, context)
    output = sympy_eval_handler(evt_False, context)
    print("====> output: " + output)


if __name__ == '__main__':
    test()

'''
    공통 false: 계수 1 생략 안 한 답(1*x, -1*2, 3/1), 동류항 정리 안 한 답은 정답의 동류항 저일 여부에 따름 (x+x, 1+1)
'''