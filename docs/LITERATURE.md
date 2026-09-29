# Литература, на которую опирается текст (сентябрь 2026)

В основной текст не входят Busy Beaver, Cappallo 2026, Chang 2026 и ежегодные непроверенные «доказательства» Коллатца.

## Tag-системы
- E. Post (1943). *Formal reductions of the combinatorial decision problem.* Amer. J. Math. 65, 197–215.
- M. Minsky (1961). *Recursive unsolvability of Post's problem of "Tag".* Ann. Math. 74(3), 437–455.
- J. Cocke, M. Minsky (1964). *Universality of tag systems with P=2.* JACM 11(1), 15–20.
- L. De Mol (2007). *Study of limits of solvability in tag systems.* LNCS 4664, 170–181. Это границы разрешимости, не полное доказательство TS(2,2).
- L. De Mol (2010). *Solvability of the halting and reachability problem for binary 2-tag systems.* Fundamenta Informaticae 99(4), 435–471. Полное доказательство. Пост утверждение не опубликовал.
- L. De Mol (2008). *Tag systems and Collatz-like functions.* Theor. Comput. Sci. 390(1), 92–101. Теорема 2.1 — наша система после разворота. Теорема 2.3 — условие унарной редукции в её конструкции. doi:10.1016/j.tcs.2007.10.020.
- L. De Mol (2011). *On the complex behavior of simple tag systems: an experimental approach.* Theor. Comput. Sci. 412. Система Поста $0\to 00$, $1\to 1101$.
- L. De Mol (2009). Обзор границ разрешимости. EPTCS 1, 56–66. arXiv:0906.3329.
- M. Cook (2004). *Universality in elementary cellular automata.* Complex Systems 15(1), 1–40, §2.2. Шесть фаз — стандартный подсчёт 2μ при μ=3.
- T. Neary (2015). *Undecidability in binary tag systems…* STACS, LIPIcs 30, 649–661. Универсальность двухсимвольных систем при большом β, зависящем от программы. Это не TS(2,2).
- S. Wolfram (2021). arXiv:2103.06931. Другая система: Пост 0→00, 1→1101, выборка 10^25.
- N. Kurilenko (2022). Complex Systems 31(3). Опубликован неограниченный рост в системе Поста 0→00, 1→1101. Мы не перепроверяли; полная классификация той системы открыта.
- The bbchallenge Collaboration (2024). Coq-доказательство BB(5) = 47 176 870. Ориентир дисциплины перебора («проверено до N» отдельно от «доказано»), не содержание этой работы.
- OEIS A351849. Та же система: 1→23, 2→1, 3→111.

## Коллатц
- J. C. Lagarias (1985). *The 3x+1 problem and its generalizations.* Amer. Math. Monthly 92, 3–23.
- D. Bařina (2025). J. Supercomputing 81, art. 810. Проверка n < 2^71. Не доказательство.
- T. Tao (2022). Forum Math. Pi 10, e12. Почти все орбиты в смысле логарифмической плотности достигают почти ограниченных значений. Не «почти все доходят до 1».
- S. Eliahou (1993). Discrete Math. 118, 45–56. Историческая оценка, устарела.
- C. Hercher (2023). J. Integer Sequences 26, 23.3.5. Нет m-циклов при m≤91. Здесь m — число локальных минимумов, не длина цикла.
- K. Knight (2026). Discrete Math. 349(3), 114812. Нет high cycles. Не решение гипотезы.
- J. Conway (1972). *Unpredictable iterations*, Boulder, 49–52. Неразрешимость обобщённого Коллатца. FRACTRAN — отдельно, 1987.
- S. Kurtz, J. Simon (2007). LNCS 4484, 542–553. Π⁰₂-полнота обобщённой задачи. К нашей фиксированной системе напрямую не относится.
- E. Yolcu, S. Aaronson, M. Heule (2021). CADE-28. Коллатц как завершаемость строковой системы переписывания.
- J. Lagarias, A. Weiss (1992). Ann. Appl. Probab. 2(1). Ключевая константа экстремального поведения γ₀ ≈ 41.677647. Коэффициент 2/ln(4/3) ≈ 6.952 — отдельная эвристика среднего числа макрошагов ускоренного T, не их константа.
