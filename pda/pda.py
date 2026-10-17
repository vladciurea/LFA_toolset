import sys
from collections import deque


def este_lambda(simbol):
    return simbol in ("lambda", "λ", "_")


def citeste_definitie(cale_fisier):
    # citim toate liniile din fisierul de intrare
    with open(cale_fisier, "r") as f:
        linii = [linie.rstrip("\n") for linie in f]

    pozitie = 0

    stari = set(linii[pozitie].split())
    pozitie += 1

    alfabet = set(linii[pozitie].split())
    pozitie += 1

    nr_tranzitii = int(linii[pozitie].strip())
    pozitie += 1

    tranzitii = []
    for _ in range(nr_tranzitii):
        campuri = linii[pozitie].split()
        stare_curenta, simbol_citit, simbol_varf, stare_urmatoare, sir_pus = campuri
        tranzitii.append((stare_curenta, simbol_citit, simbol_varf, stare_urmatoare, sir_pus))
        pozitie += 1

    stare_initiala = linii[pozitie].strip()
    pozitie += 1

    simbol_initial = linii[pozitie].strip()
    pozitie += 1

    stari_finale = set(linii[pozitie].split())
    pozitie += 1

    mod_acceptare = linii[pozitie].strip()
    pozitie += 1

    cuvant = linii[pozitie].strip() if pozitie < len(linii) else ""

    # un cuvant marcat ca vid devine sir gol
    if este_lambda(cuvant):
        cuvant = ""

    return {
        "stari": stari,
        "alfabet": alfabet,
        "tranzitii": tranzitii,
        "stare_initiala": stare_initiala,
        "simbol_initial": simbol_initial,
        "stari_finale": stari_finale,
        "mod_acceptare": mod_acceptare,
        "cuvant": cuvant,
    }


def este_acceptata(stare, stiva, mod, stari_finale):
    # acceptare prin stare finala
    if mod == "stare_finala":
        return stare in stari_finale

    # acceptare prin stiva goala
    if mod == "stiva_goala":
        return len(stiva) == 0

    # acceptare prin stare finala si stiva goala
    if mod == "ambele":
        return stare in stari_finale and len(stiva) == 0

    return False


def simuleaza(pda):
    cuvant = pda["cuvant"]
    tranzitii = pda["tranzitii"]
    mod = pda["mod_acceptare"]
    stari_finale = pda["stari_finale"]

    # construim configuratia initiala: stare initiala, pozitie 0, stiva cu simbolul initial
    stiva_initiala = (pda["simbol_initial"],)
    config_initiala = (pda["stare_initiala"], 0, stiva_initiala)

    # pregatim coada pentru BFS si multimea configuratiilor vizitate
    coada = deque([config_initiala])
    vizitate = {config_initiala}

    while coada:
        # extragem pe rand cate o configuratie din coada
        stare, index, stiva = coada.popleft()

        # acceptam imediat daca am consumat tot inputul si conditia de acceptare e indeplinita
        if index == len(cuvant) and este_acceptata(stare, stiva, mod, stari_finale):
            return True

        # generam toate configuratiile urmatoare posibile
        for stare_curenta, simbol_citit, simbol_varf, stare_urmatoare, sir_pus in tranzitii:
            # tranzitia trebuie sa porneasca din starea curenta
            if stare_curenta != stare:
                continue

            # avem nevoie de un varf de stiva cu care sa comparam
            if not stiva:
                continue

            # varful stivei trebuie sa coincida cu simbolul cerut de tranzitie
            if stiva[-1] != simbol_varf:
                continue

            # calculam noua pozitie in input in functie de simbolul citit
            if este_lambda(simbol_citit):
                index_nou = index
            else:
                if index >= len(cuvant) or cuvant[index] != simbol_citit:
                    continue
                index_nou = index + 1

            # facem pop pentru simbolul din varful stivei
            stiva_noua = stiva[:-1]

            # adaugam pe stiva sirul nou in ordine inversa daca nu este vid
            if not este_lambda(sir_pus):
                stiva_noua = stiva_noua + tuple(reversed(sir_pus))

            # construim configuratia urmatoare
            config_noua = (stare_urmatoare, index_nou, stiva_noua)

            # adaugam configuratia in coada doar daca nu a mai fost vizitata
            if config_noua not in vizitate:
                vizitate.add(config_noua)
                coada.append(config_noua)

    # nicio configuratie de acceptare gasita, deci cuvantul este respins
    return False


def main():
    # preluam caile fisierelor de intrare si de iesire
    cale_intrare = sys.argv[1] if len(sys.argv) > 1 else "input"
    cale_iesire = sys.argv[2] if len(sys.argv) > 2 else "output"

    pda = citeste_definitie(cale_intrare)

    acceptat = simuleaza(pda)

    rezultat = "Acceptat" if acceptat else "Respins"

    # scriem rezultatul in fisierul de iesire
    with open(cale_iesire, "w") as f:
        f.write(rezultat + "\n")




if __name__ == "__main__":
    main()