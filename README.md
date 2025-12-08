# Projekt: Bankovní operace s VIP prioritizací

**Autor:** David Pivoňka  
**Datum:** 25. 11. 2025


## Co projekt dělá
Program simuluje provoz banky z pohledu manažera, který sleduje a hodnotí transakce klientů. Pět zákazníků má své účty uložené v souboru, provádí vklady, výběry, dotazy na zůstatek a převody mezi účty, přičemž VIP požadavky mají při zpracování vyšší prioritu. Částky, denní limity a kompletní historie transakcí se ukládají, takže zůstatky i výpisy z účtů zůstávají zachovány i po dalším spuštění programu.


## Instalace a spuštění
- Vyžaduje **Python 3.10+**  
- Všechny použité knihovny jsou součástí standardní instalace Pythonu.  
- Všechny níže uvedené soubory musí být ve stejné složce:
main.py, account.py, ticket.py, worker.py, persistence.py.
- Spusť v terminálu příkaz:  
python UsingBankomat.py


## Základní funkce
- Paralelní (souběžné) odbavení více požadavků na bankomaty.
- VIP požadavky jsou obslouženy vždy přednostně.
- Každý požadavek může být: **výběr**, **vklad**, nebo **zůstatek** na účtu.
- Výsledky operací jsou jasně a přehledně vypsány do konzole.

## Struktura projektu
- account.py – třída Account (zůstatek, denní limit, historie transakcí).
- ticket.py – třída Ticket (ID požadavku, VIP příznak, typ akce, částka, ID účtů).
- worker.py – funkce pro zpracování požadavků v procesech a tisk manažerského výpisu.
- persistence.py – načtení a uložení účtů do souboru accounts.json.
- main.py – hlavní soubor, který připraví účty, vygeneruje ukázkové tikety a spustí paralelní zpracování.


## Příklad výstupu
VIP Požadavek 7 | účet 2 | Akce: TRANSFER
------------------------------------------------------
 > Převod 6000 Kč z účtu 2 na účet 5. Nový zůstatek 6000 Kč.
======================================================

Požadavek 5 | účet 1 | Akce: DEPOSIT
------------------------------------------------------
 > Vklad 2000 Kč, nový zůstatek 7000 Kč
======================================================

Všechny akce u banky byly zpracovány.

########################################
VÝPISY Z ÚČTŮ (pohled manažera)
########################################
ÚČET 1 – zůstatek 7000 Kč, denní limit 4000 Kč
2025-12-09 00:15:30 | DEPOSIT    |   2000 Kč | Vklad 2000 Kč, nový zůstatek 7000 Kč
...
=