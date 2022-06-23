from sympy import *
from re import *
from answer_conversion import *

# 단순값 비교
def IsEqual(correct_sympy, student_sympy): #정답 order 관계X
    return student_sympy.equals(correct_sympy)

# simplify와 args len, equals 비교 (기호 포함하는 순환소수, 절댓값 compare 제외)
def IsArgsEqual(sympy):
    exp_args = sorted(DelMulOne(map(lambda x: x,sympy.args)),key=lambda x: x.sort_key())
    cp_args = sorted(parse_expr(str(sympy),evaluate=True).args,key=lambda x: x.sort_key())
    # print(sympy,parse_expr(str(sympy),evaluate=True),exp_args,cp_args,'여기')
    # print( exp_args, cp_args)
    if len(exp_args) != len(cp_args): print('IsArgsEqual',1);return False
    if all(IsEqual(exp_args[i],cp_args[i]) for i in range(len(exp_args))) == 0:
        print('IsArgsEqual',2);return False
    return True
# print(IsArgsEqual(Parse2Sympy('Abs(+5)')),Parse2Sympy('Abs(+5)').args)
# print(IsArgsEqual(Parse2Sympy('0.[3]')),Parse2Sympy('0.[3]'))

# 동류항 정리 확인(Add일 때)
def IsSimilarTerm(student_sympy):
    s_args = tuple([student_sympy])
    while s_args != ():
        s_tmp = ()
        #print(s_args)
        for p in s_args:
            if type(p) in [Pow,Mul]: s_tmp += p.args; continue
            if IsArgsEqual(p) == 0: print('IsSimilarTerm',1);return False
            s_tmp += p.args
        s_args = s_tmp
    return True
# print(IsSimilarTerm(Parse2Sympy('xy+3x+5y+10+5')))

# 다항식 1개 비교
def single_poly(correct_sympy, student_sympy): #정답 order 관계X
    if IsEqual(correct_sympy, student_sympy) == 0: print('single_poly',1);return False
    if abs(denom(correct_sympy)).equals(abs(denom(student_sympy))) == 0: print('single_poly',2);return False
    if IsSimilarTerm(student_sympy) == 0: print('single_poly',3);return False
    return True
# correct_sympy, student_sympy = Ans2Sympy(r'500-150\times a','500-150 × a')
# correct_sympy, student_sympy = Ans2Sympy(r'a','1a')
# print(correct_sympy,student_sympy)
# correct_sympy, student_sympy = correct_sympy[0], student_sympy[0]
# print(single_poly(correct_sympy, student_sympy))

# 다항식 단순 비교(동류항 정리 조건만 만족, 정답과 차수 일치)
def PolyCompare(correct_sympy, student_sympy, order=None): #정답 order 관계X
    if order == None:
        correct_sympy = sorted(correct_sympy, key=lambda x: x.sort_key())
        student_sympy = sorted(student_sympy, key=lambda x: x.sort_key())
    if len(correct_sympy) != len(student_sympy): return False
    if all(single_poly(correct_sympy[i], student_sympy[i]) for i in range(len(correct_sympy))) == 0: print('PolyCompare',1);return False
    return True
# correct_sympy, student_sympy = Ans2Sympy('3yz+2xyz','(15xyz+10x**2yz)/(5x)')
# # correct_sympy, student_sympy = Ans2Sympy(r'3xy, -5xy','-5xy,3xy')
# correct_sympy, student_sympy = Ans2Sympy(r'x-4','x-4')
# print(PolyCompare(correct_sympy, student_sympy))

def NoSignCompare(correct_sympy, student_sympy):
    c_sympy, s_sympy = Latex2Sympy(correct_sympy), Parse2Sympy(student_sympy)
    if IsEqual(c_sympy, s_sympy) == 0: print(0,'정답과 값이 다름');return False

    # 곱셈, 나눗셈 기호, 계수 1 생략했는지 확인
    ptn = ['×|÷','(?<![0-9.])([1][a-zA-Z]{1})|([a-zA-Z][1])(?![0-9])']
    for p in ptn:
        if len(findall(p, student_sympy)) > 0: print(0,'기호, 계수 생략X');return False

    # 학생 답안 항으로 쪼개기
    if type(s_sympy) == Add: terms = s_sympy.args
    else: terms = tuple([s_sympy])

    while terms != ():
        print(terms)
        tmp = ()
        for s in terms:
            if type(s) != Add:
                tmp_s = sub('\(.+\)','',str(s))
                print(tmp_s)
                print(finditer('(?<!\/|\*\*)[1-9\-]+(\/[1-9]+)*',tmp_s))
                # 수가 문자 앞에 있는지 확인 (마이너스 포함)
                try:

                    for i in finditer('(?<!\/|\*\*)[1-9\-]+(\/[1-9]+)*',tmp_s):
                        print(여기)
                        if i.start() != 0: print(1,'숫자가 문자 뒤에');return False
                except:
                    pass

                # 알파벳 순서인지 확인, (거듭제곱도 확인 가능) ** 대소문자 같이 나올 때 고려X **
                ASCIIcode = list(filter(lambda x: 65<x<90 or 97<x<122,map(lambda x: ord(x),tmp_s)))
                for i in range(len(ASCIIcode)-1):
                    if ASCIIcode[i] >= ASCIIcode[i+1]: print(2,'알파벳 순서X');return False

                for args in map(lambda x: Parse2Sympy(x).args,findall('\(.+\)', str(s))): tmp += args
        terms = tmp
    return True


# correct_sympy, student_sympy = Ans2Sympy(r'-\dfrac{1}{3}ah', '1/3*(-a)*h',f='NoSignCompare')
# correct_sympy, student_sympy = Ans2Sympy(r'-\dfrac{1}{3}x-3y', '-1/3x-y3',f='NoSignCompare')
# correct_sympy, student_sympy = Ans2Sympy(r'-10(3*a+3*b)', '-10*(3*a+b*3)',f='NoSignCompare')
# correct_sympy, student_sympy = Ans2Sympy(r'\dfrac{a^2}{b}', '(a**2)/(b)',f='NoSignCompare')
# correct_sympy, student_sympy = Ans2Sympy(r'x^2+3x', 'x**2+3*x',f='NoSignCompare')
# print(NoSignCompare(correct_sympy, student_sympy))


# 인수분해
def PolyFactorCompare(correct_sympy, student_sympy): #정답 order 관계X
    c_sympy, s_sympy = correct_sympy[0], student_sympy[0]
    if IsEqual(c_sympy, s_sympy) == 0: print(1);return False
    if IsSimilarTerm(s_sympy) == 0: print(2);return False
    s_args = tuple([s_sympy])
    while s_args != ():
        s_tmp = ()
        # print(s_args)
        for p in s_args:
            if type(p) in [Mul,Pow]: print(11);s_tmp += p.args
            elif len(factor_list(p)[1]) == 0 or len(factor_list(p)[1]) == abs(factor_list(p)[0]) == factor_list(p)[1][0][1] == 1:
                continue
            else: print(3);return False
        s_args = s_tmp
    return True
# correct_sympy, student_sympy = Ans2Sympy('\dfrac{1}{2}(x-2)^2','1/2*(x-2)**2')
# # correct_sympy, student_sympy = Ans2Sympy('(a+b)(2-x-2y)','2(a+b)-(x+2y)(a+b)')
# print(PolyFactorCompare(correct_sympy, student_sympy))

# 전개, 순서 비교(오름차순/내림차순)
def PolyExpansionCompare(correct_sympy, student_sympy,order=None,symbol=None): #정답 order 관계X
    c_sympy, s_sympy = correct_sympy[0], student_sympy[0]
    # print(correct_sympy.args, student_sympy.args)
    if type(s_sympy) != Add: return False
    if IsEqual(c_sympy, s_sympy) == 0: return False
    if IsSimilarTerm(s_sympy) == 0: return False
    if len(c_sympy.args) != len(s_sympy.args): return False
    if order == None:
        cr_args = sorted(DelMulOne(c_sympy.args), key=lambda x: x.sort_key())
        st_args = sorted(DelMulOne(s_sympy.args), key=lambda x: x.sort_key())
        return all(IsEqual(cr_args[i], st_args[i]) for i in range(len(cr_args)))
    else:
        degree_list = list(map(lambda t: degree(t, gen=Symbol(symbol)), s_sympy.args))
        # print(degree_list,symbol)
        if order == 'Acc':
            return all(degree_list[i] <= degree_list[i + 1] for i in range(len(c_sympy.args) - 1))
        else:
            return all(degree_list[i] >= degree_list[i + 1] for i in range(len(c_sympy.args) - 1))
# correct_sympy, student_sympy = Ans2Sympy('3yz+2xyz','2xyz+3yz')
# print(PolyExpansionCompare(correct_sympy, student_sympy,order='Dec',symbol='y'))

# 다항식 정확히 비교
# BQ+R 꼴, a(x-p)**2+q 꼴 등
def PolyFormCompare(correct_sympy,student_sympy): # 다항식 A, B 교환 허용X, 동류항 반드시 정리해야 함
    correct_sympy, student_sympy = correct_sympy[0], student_sympy[0]
    print(correct_sympy,student_sympy)
    if single_poly(correct_sympy, student_sympy) == 0: print('0');return False
    c_args = sorted(tuple(map(lambda x: x*2/2,(correct_sympy*2/2).args)),key=lambda x: x.sort_key())
    s_args = sorted(tuple(map(lambda x: x*2/2,(student_sympy*2/2).args)),key=lambda x: x.sort_key())
    while c_args != ():
        print(c_args, s_args)
        c_tmp = ()
        s_tmp = ()
        if len(c_args) != len(s_args): print('1'); return False
        for i in range(len(c_args)):
            if type(c_args[i]) in [Mul,Pow]:
                c_tmp += c_args[i].args
                s_tmp += s_args[i].args
            else:
                if single_poly(c_args[i], s_args[i]) == 0:
                    print('2');return False
        c_args = c_tmp
        s_args = s_tmp
    return True

# correct_sympy, student_sympy = Ans2Sympy(r'-\dfrac{1}{2}(x-3)^2','-1/2(x-3)**2')
# print(PolyFormCompare(correct_sympy, student_sympy))

