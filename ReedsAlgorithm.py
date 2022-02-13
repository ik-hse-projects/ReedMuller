import itertools, math

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
def all_subsets(m, r):
    '''
    >>> [bin(i) for i in all_subsets(3, 3)]
    ['0b1', '0b10', '0b100', '0b11', '0b101', '0b110', '0b111']
    '''
    return itertools.chain.from_iterable(
        subsets(m, t) for t in range(1, r+1)
    )

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

# Возвращает все смежные классы вида $(V_A + b)$
def cosets(m, A):
    for b in subspaceV_minusA(m, A):
        yield (v + b for v in subspaceV_A(m, A))

# Вычисляет $\Eval\left(\sum_{A ∈ \mathit{As}} u_A x_A\right)$
def evaluate(As, m, u):
    '''
    f(x₀,x₁,x₂) = x₀x₂ будет иметь вектор значений 00000101
    >>> bin(evaluate([0b101], 3, {0b101: 1}))
    '0b101'

    f(x₀,x₁) = 1 будет иметь вектор значений 1111
    >>> bin(evaluate([0], 2, {0: 1}))
    '0b1111'
    '''
    result = 0
    for z in range(2**m):
        val = 0
        for A in As:
            # Вычисляю $x_A = x_{A_1}x_{A_2}…x_{A_k}$, подставляя в качестве $x_i = z_i$
            # Это равно единице тогда и только тогда, когда все биты из $A$ также стоят в $z$.
            xProduct = 1 if (z & A) == A else 0

            val += u[A] * xProduct
        val %= 2
        result = (result << 1) | val
    return result

# Алгоритм Рида по псевдокоду, который был ранее
def Reed(r, m, y):
    # $k = \sum_{i=0}^r C_m^r$. TODO: хранить в int, а не массиве
    u = [None] * sum(math.comb(m,i) for i in range(r+1))
    t = r
    while t >= 0:
        for A in subsets(m, t):
            num1 = 0
            for coset in cosets(m, A):
                # s = $\sum_{z ∈ \mathit{coset}} y_z$
                s = sum((y >> z) & 1 for z in coset)
                if (s % 2) == 1:
                    num1 += 1
            u[A] = int(num1 >= 2**(m - t - 1))
        y = y ^ evaluate(subsets(m, t), m, u)
        t = t - 1
    c = evaluate(all_subsets(m, r), m, u)
    return (c, u)

# «Тесты»:
import doctest; doctest.testmod()
# Try: `python -i ReedsAlgorithm.py`
