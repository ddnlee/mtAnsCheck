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
            PolyFactorCompare: 2
            PolyExpansionCompare: 3
            PolyFormCompare: 4
            NumCompare: 5
            NumPrimeFactorCompare: 6
            PairCompare: 7
            EqCompare: 8
            IneqCompare: 9
            SignCompare: 10
        '''

        if (len(_student_answer) > 0):
            try:
                correct_sympy, student_sympy = Ans2Sympy(_correct_answer,_student_answer, f=_check_function)
                if _check_function == 'PolyExpansionCompare':
                    _symbol = object[cnt]['symbol'] if 'symbol' in object[cnt].keys() else None
                    _order = object[cnt]['order'] if 'order' in object[cnt].keys() else None
                    
                    result = globals()[_check_function](correct_sympy, student_sympy, _symbol, _order)
                elif _check_function == 'NumCompare':
                    _Type = object[cnt]['Type'] if 'Type' in object[cnt].keys() else None
                    _order = object[cnt]['order'] if 'order' in object[cnt].keys() else None

                    result = globals()[_check_function](correct_sympy, student_sympy, _Type, _order)
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
        {"ID": "0", "check_function": "NumCompare", "correct_answer": "36", "student_answer": "36",
         "Type": None, "order": None, "symbol" : None, "leading_coeff" : None}]}
    context = 'test'
    output = sympy_eval_handler(event, context)
    print("====> output: " + output)


if __name__ == '__main__':
    test()