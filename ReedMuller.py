import itertools, math
__all__ = ['encode', 'decode', 'code_info']

# Возвращает длину сообщения $k = \sum_{i=0}^r C_m^i$, корректирующую способность $t = 2^{m - r - 1} - 1$ и длину кода $n = 2^m$
def code_info(r, m):
	'''
	>>> code_info(1, 2)
	{'k': 3, 't': 0, 'n': 4}
	>>> code_info(2, 4)
	{'k': 11, 't': 1, 'n': 16}
	'''
	return {'k': sum(math.comb(m, i) for i in range(0, r+1)),
	        't': 2**(m - r - 1) - 1, 'n': 2**m}

# Возвращает $\{ A ⊆ \{0, …, m-1\} : |A| = t \}$
def subsets(m, t):
	'''
	>>> [bin(i) for i in subsets(3, 1)]
	['0b1', '0b10', '0b100']
	>>> [bin(i) for i in subsets(3, 2)]
	['0b11', '0b101', '0b110']
	>>> [bin(i) for i in subsets(3, 3)]
	['0b111']
	'''
	for i in itertools.combinations(range(0, m), t):
	    # $i$ содержит выбранные биты, ровно $t$ штук.
	    yield sum(1 << j for j in i)

# Возвращает $\{ A ⊆ \{0, …, m-1\} : |A| ≤ r \}$
def all_subsets(r, m):
	'''
	>>> [bin(i) for i in all_subsets(3, 3)]
	['0b0', '0b1', '0b10', '0b100', '0b11', '0b101', '0b110', '0b111']
	'''
	return itertools.chain.from_iterable(
	    subsets(m, t) for t in range(0, r+1))

# Вычисляет $\Eval\left(\sum_{A ∈ \mathit{As}} u_A x_A\right)$
def evaluate(get_As, m, u):
	'''
	f(x₀,x₁,x₂) = x₀x₂ будет иметь вектор значений 00000101
	>>> bin(evaluate(lambda: [0b101], 3, {0b101: 1}))
	'0b101'

	f(x₀,x₁) = 1 + x₁ будет иметь вектор значений 1100
	>>> bin(evaluate(lambda: [0b00, 0b10], 2, {0:1, 2:1}))
	'0b1100'
	'''
	result = 0
	for z in range(2**m):
	    summ = 0
	    for A in get_As():
	        # Вычисляю $x_A = x_{A_1}x_{A_2}…x_{A_k}$, подставляя в качестве $x_i = z_i$
	        # Это равно единице тогда и только тогда, когда все биты из $A$ также стоят в $z$.
	        xProduct = 1 if (z & A) == A else 0
	        summ += u[A] * xProduct
	    result = (result << 1) | (summ % 2)
	return result

# Кодирует сообщение $u$ при помощи кода $\RM(r, m)$
def encode(r, m, msg):
	'''
	>>> bin(encode(2, 4, [1,1,1,0,0,1,1,0,1,0,0]))
	'0b1000111010001110'
	'''
	u = [None] * (2**m)
	for i, A in zip(msg, all_subsets(r, m), strict=True):
	    u[A] = i
	return evaluate(lambda: all_subsets(r, m), m, u)

# Возвращает все векторы из подпространства $V⊆𝔽_2$,
# если даны базисные векторы для $V$.
def _subspace(basis):
	for i in range(2**len(basis)):
	    result = 0
	    for mask in basis:
	        if (i & 1) == 1:
	            result |= mask
	        i >>= 1
	    yield result

# Возвращает все векторы из подпространства $V_A ⊆ 𝔽₂^m$
def subspaceV_A(_m, A):
	'''
	>>> [bin(i) for i in subspaceV_A(3, 0b10)]
	['0b0', '0b10']
	>>> [bin(i) for i in subspaceV_A(3, 0b101)]
	['0b0', '0b1', '0b100', '0b101']
	'''
	basis = []
	mask = 1
	while mask <= A:
	    if (A & mask) != 0:
	        basis.append(mask)
	    mask <<= 1
	return _subspace(basis)

# Возвращает все векторы из подпространства $V_{\overbar{A}}$
def subspaceV_minusA(m, A):
	'''
	>>> [bin(i) for i in subspaceV_minusA(3, 0b10)]
	['0b0', '0b1', '0b100', '0b101']
	>>> [bin(i) for i in subspaceV_minusA(3, 0b101)]
	['0b0', '0b10']
	'''
	basis = []
	for i in range(m):
	    mask = 1 << i
	    if (A & mask) == 0:
	        basis.append(mask)
	return _subspace(basis)

# Алгоритм Рида по псевдокоду, который был в статье
def decode(r, m, y):
	'''
	Попробуйте изменить здесь бит и запустить тесты снова!
	>>> decode(2, 4, 0b1000111010001110)
	('0b1000111010001110', [1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0])
	'''
	u = [None] * (2**m)
	t = r
	while t >= 0:
	    for A in subsets(m, t):
	        num1 = 0
	        for b in subspaceV_minusA(m, A):
	            coset = (v + b for v in subspaceV_A(m, A))

	            # s = $\sum_{z ∈ (V_A + b)} y_z$
	            s = sum((y >> z) & 1 for z in coset)
	            if (s % 2) == 1:
	                num1 += 1
	        u[A] = int(num1 >= 2**(m - t - 1))
	    y = y ^ evaluate(lambda: subsets(m, t), m, u)
	    t = t - 1
	c = evaluate(lambda: all_subsets(r, m), m, u)
	msg = [u[A] for A in all_subsets(r, m)]
	return bin(c), msg

# «Тесты»:
import doctest; doctest.testmod()
# Try: `python -i ReedMuller.py`