from itertools import combinations


def parse_symbols(prod, neterm, term):
    sorted_nt = sorted(neterm, key=len, reverse=True)
    result = []
    i = 0
    while i < len(prod):
        matched = False
        for nt in sorted_nt:
            if nt and prod[i:i + len(nt)] == nt:
                result.append(nt)
                i += len(nt)
                matched = True
                break
        if not matched:
            result.append(prod[i])
            i += 1
    return result


def print_gram(gram):
    for nt, prods in gram.items():
        print(f"  {nt} -> {' | '.join(prods)}")


def to_chomsky(gr, m_neterm, m_term, simb_start):
    gram = {k: list(v) for k, v in gr.items()}
    neterm = list(m_neterm)
    term = [t for t in m_term if t != 'l']  # 'l' (lambda) nu e terminal real

    # PASUL 1: Simbol de start nou S0 -> S

    new_start = "S0"
    while new_start in neterm:
        new_start += "0"
    neterm.append(new_start)
    gram[new_start] = [simb_start]
    simb_start = new_start

    # PASUL 2: Eliminare productii lambda

    nullable = set()
    changed = True
    while changed:
        changed = False
        for nt, prods in gram.items():
            if nt in nullable:
                continue
            for prod in prods:
                if prod == 'l':
                    if nt not in nullable:
                        nullable.add(nt); changed = True
                    continue
                syms = parse_symbols(prod, neterm, term)
                if all(s in nullable for s in syms): # daca, cumva un neterminal se gaseste prin lista parsata a productiei, acea productie implicit nu este nullable
                    if nt not in nullable:
                        nullable.add(nt); changed = True

    new_gram = {}
    for nt, prods in gram.items():
        new_prods = set()
        for prod in prods:
            if prod == 'l':
                continue
            syms = parse_symbols(prod, neterm, term)
            null_pos = [i for i, s in enumerate(syms) if s in nullable] #gasim pozitiile simbolurilelor nullable din productie; pentru: [S -> BCB] cu B nullable => null_pos = [0,2]
            for r in range(len(null_pos) + 1):
                for omit in combinations(null_pos, r):
                    res = [s for i, s in enumerate(syms) if i not in omit]
                    if res: # conditie pentru a nu adauga 'lambda' inapoi daca toate simbolurile din productie sunt nullable si suntem in pasul in care le omitem pe toate
                        new_gram.setdefault(nt, set())
                        new_prods.add(''.join(res))
        if new_prods:
            new_gram[nt] = new_prods
    gram = {k: list(v) for k, v in new_gram.items()}

    # daca simbolul de start poate genera cuvantul vid, pastram S0 -> l
    if simb_start in nullable:
        gram.setdefault(simb_start, [])
        if 'l' not in gram[simb_start]:
            gram[simb_start].append('l')

    # PASUL 3: Eliminare reguli unitare (A -> B)

    changed = True
    while changed:
        changed = False
        for nt in list(gram.keys()):
            for prod in list(gram[nt]):
                if prod in neterm:  # productie unitara
                    gram[nt].remove(prod)
                    changed = True
                    for p in gram.get(prod, []):
                        if p not in gram[nt]:
                            gram[nt].append(p)

    # PASUL 4: Eliminare simboluri inutile

    # 4a) generative
    generative = set(term)
    changed = True
    while changed:
        changed = False
        for nt, prods in gram.items():
            if nt in generative:
                continue
            for prod in prods:
                if prod == 'l':
                    generative.add(nt); changed = True; break
                syms = parse_symbols(prod, neterm, term)
                if all(s in generative for s in syms):
                    generative.add(nt); changed = True; break

    # 4b) accesibile din start
    accesibile = {simb_start}
    changed = True
    while changed:
        changed = False
        for nt in list(accesibile):
            for prod in gram.get(nt, []):
                if prod == 'l':
                    continue
                for s in parse_symbols(prod, neterm, term):
                    if s not in accesibile:
                        accesibile.add(s); changed = True

    utile = generative & accesibile
    new_gram = {}
    for nt, prods in gram.items():
        if nt not in utile:
            continue
        kept = []
        for p in prods:
            if p == 'l':
                kept.append(p); continue
            if all(s in utile for s in parse_symbols(p, neterm, term)):
                kept.append(p)
        if kept:
            new_gram[nt] = kept
    gram = new_gram
    neterm = [n for n in neterm if n in utile]

    # PASUL 5: Inlocuire terminale in regulile lungi

    terminal_map = {}
    tcount = [0]

    def term_nt(t):
        if t not in terminal_map:
            name = f"X{t}{tcount[0]}"
            tcount[0] += 1
            while name in neterm:
                name = f"X{t}{tcount[0]}"; tcount[0] += 1
            terminal_map[t] = name
            neterm.append(name)
        return terminal_map[t]

    new_gram = {}
    for nt, prods in gram.items():
        new_prods = []
        for prod in prods:
            if prod == 'l':
                new_prods.append('l'); continue
            syms = parse_symbols(prod, neterm, term)
            if len(syms) == 1:
                new_prods.append(prod); continue  # A -> a ramane
            new_syms = [term_nt(s) if s in term else s for s in syms]
            new_prods.append(''.join(new_syms))
        new_gram[nt] = new_prods
    for t, name in terminal_map.items():
        new_gram[name] = [t]
    gram = new_gram

    # PASUL 6: Spargere reguli lungi (RECURSIV)

    ycount = [0]
    split_cache = {} # stocam neterminalele deja mapate pentru a evita duplicate
    helper_rules = {} # noile productii intermediare

    def new_y():
        name = f"Y{ycount[0]}"
        ycount[0] += 1
        while name in neterm:
            name = f"Y{ycount[0]}"; ycount[0] += 1
        neterm.append(name)
        return name

    def binarize(syms):
        # returneaza o prod. cu cel mult 2 simboluri, inregistrand neterminale ajutatoare
        if len(syms) <= 2:
            return ''.join(syms)
        rest = tuple(syms[1:])
        if rest in split_cache:
            z = split_cache[rest]
        else:
            z = new_y()
            split_cache[rest] = z
            helper_rules[z] = [binarize(list(rest))]
        return syms[0] + z

    new_gram = {}
    for nt, prods in gram.items():
        new_prods = []
        for prod in prods:
            if prod == 'l':
                new_prods.append('l'); continue
            syms = parse_symbols(prod, neterm, term)
            new_prods.append(binarize(syms))
        new_gram[nt] = new_prods
    new_gram.update(helper_rules)
    gram = new_gram

    print("\n FORMA NORMALA CHOMSKY")
    print_gram(gram)

    return gram, neterm, term, simb_start


def scrie_output(path, gram, neterm, term, simb_start):
    # neterminale efectiv folosite (chei + cele din productii)
    used_nt = set(gram.keys())
    # ordonam: start primul, apoi restul stabil
    nt_order = [simb_start] + sorted(n for n in used_nt if n != simb_start)

    productii = []
    for nt in nt_order:
        for prod in gram.get(nt, []):
            productii.append((nt, prod))

    # terminalele includ 'l' (lambda) ca in input
    term_out = list(term) + ['l']

    with open(path, "w") as f:
        f.write(' '.join(nt_order) + '\n')
        f.write(' '.join(term_out) + '\n')
        f.write(str(len(productii)) + '\n')
        for nt, prod in productii:
            f.write(f"{nt} {prod}\n")
        f.write(simb_start + '\n')


f = open("input")
mult_neterm = f.readline().strip().split()
term        = f.readline().strip().split()
nr_prod     = int(f.readline().strip())

gram = {}
for _ in range(nr_prod):
    parts = f.readline().strip().split()
    nt, rhs = parts[0], parts[1]
    gram.setdefault(nt, []).append(rhs)

s_start  = f.readline().strip()
f.close()

print("GRAMATICA INITIALA")
print_gram(gram)
print(f"Start: {s_start}")

g, nt, tm, start = to_chomsky(gram, mult_neterm, term, s_start)
scrie_output("output", g, nt, tm, start)
