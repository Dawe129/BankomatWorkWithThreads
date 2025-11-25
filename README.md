# Projekt: Bankovní operace s VIP prioritizací

**Autor:** David Pivoňka  
**Datum:** 25. 11. 2025


## Co projekt dělá
Program simuluje reálný provoz u bankomatů: uživatelé zadávají požadavky na výběr, vklad nebo kontrolu zůstatku ke svým bankovním účtům. Tyto požadavky jsou odbavovány souběžně pomocí více bankomatů (vláken), přičemž požadavky VIP klientů mají při obsluze vždy přednost.


## Instalace a spuštění
- Vyžaduje **Python 3.10+**  
- Všechny použité knihovny jsou součástí standardní instalace Pythonu.  
- Spusť v terminálu příkaz:  
python UsingBankomat.py


## Základní funkce
- Paralelní (souběžné) odbavení více požadavků na bankomaty.
- VIP požadavky jsou obslouženy vždy přednostně.
- Každý požadavek může být: **výběr**, **vklad**, nebo **zůstatek** na účtu.
- Výsledky operací jsou jasně a přehledně vypsány do konzole.


## Příklad výstupu
Požadavek 1: WITHDRAW 1500
Zadán do fronty.
================================================
VIP Požadavek 2 | účet 2 | Akce: DEPOSIT
Vklad: 3000 Kč
Nový zůstatek: 15000 Kč
===============================================