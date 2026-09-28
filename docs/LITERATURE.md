# Литература и состояние науки (на сентябрь 2026)

## Tag-системы
- E. Post (1921, опубл. 1943). *Formal reductions of the combinatorial decision problem.* Amer. J. Math. 65, 197–215. Tag-системы; нерешённая система 0→00, 1→1101.
- M. Minsky (1961); J. Cocke, M. Minsky (1964). *Universality of tag systems with P=2.* JACM 11, 15–20.
- H. Wang (1963). *Tag systems and lag systems.* Math. Ann. 152, 65–74.
- **L. De Mol (2008). *Tag systems and Collatz-like functions.* Theor. Comput. Sci. 390, 92–101.** Система a→bc, b→a, c→aaa, изоморфная нашей. https://www.clps.ugent.be/sites/default/files/publications/6812232.pdf
- L. De Mol (2009/2011). *On the boundaries of solvability and unsolvability in tag systems*; *On the complex behavior of simple tag systems* (разрешимость TS(2,2), метод таблиц). arXiv:0906.3329
- M. Cook (2004). *Universality in elementary cellular automata.* Complex Systems 15. Циклические tag-системы.
- T. Neary (2015). *Undecidability in binary tag systems and the Post correspondence problem for five pairs of words.* STACS; arXiv:1312.6700. Двоичные tag-системы универсальны.
- S. Wolfram (2021). *After 100 years, can we finally crack Post's problem of tag?* arXiv:2103.06931. Все 10^25 малых начальных условий останавливаются, длины ведут себя как случайное блуждание.
- T. Cappallo (сент. 2026). *Tag-system computation using only powers and principal logarithms.* arXiv:2609.10592. Свежий результат, годится как «SOTA-штрих».

## Коллатц: состояние на 2026
- D. Barina (2025). *Improved verification limit…* J. Supercomput. 81, 810. Проверено до 2^71 ≈ 2.36·10^21 (проект продолжается, ≈2^71.02).
- T. Tao (2022). *Almost all orbits of the Collatz map attain almost bounded values.* Forum Math. Pi 10, e12.
- R. Terras (1976); I. Korec (1994); Krasikov–Lagarias (2003). Результаты «почти все».
- S. Eliahou (1993); C. Hercher (2023): нет m-циклов при m ≤ 91; **K. Knight (2026). *Collatz high cycles do not exist.* Discrete Math. 349(3), 114812.**
- J. Conway (1972) *Unpredictable iterations*; Kurtz–Simon (2007): обобщённая задача неразрешима (Π⁰₂-полна).
- E. Yolcu, S. Aaronson, M. Heule (2021). *An automated approach to the Collatz conjecture.* CADE-28; arXiv:2105.14697. Коллатц как завершаемость системы переписывания строк, SAT-доказательства ослабленных версий. **Прямо родственно нашей постановке.**
- J. Lagarias, A. Weiss (1992). Стохастические модели (время остановки ≈ 6.95 ln n).
- J. Lagarias (ред., 2010). *The Ultimate Challenge: The 3x+1 Problem.* AMS.
- Busy Beaver: BB(5) определён (2024), машина «Antihydra» связывает BB(6) с задачей типа Коллатца.
- E. Y. Chang (2026). *Exploring Collatz dynamics with human–LLM collaboration.* arXiv:2603.11066. Пример прозрачного описания работы с ИИ, **включая ложную лемму от LLM**. Хорошая ссылка для раздела о раскрытии ИИ.
- Проект ccchallenge.org: формализация литературы о Коллатце в Lean.

## Предостережение
Каждый год на arXiv появляются «доказательства» гипотезы Коллатца. Ни одно не выдержало проверки. Не цитировать такие работы как результаты.
