# A hard problem about a simple alphabet

MEPhI contest **Hod Mysli** 2026, correspondence round · [problem statement](https://hod.mephi.ru/tasks/2026/simple-alphabet)

The contest rules are a Post 2-tag system, conjugate to De Mol (2008), that computes the accelerated Collatz map \(T\). Whether every word \(\mathrm{B}^n\) halts is **open and equivalent to the Collatz conjecture**. Everything else in this repository is either proved in `paper/` or enumerated up to a stated bound. A test here does not replace a proof: it catches regressions in numbers and statements.

Paper (PDF): [`paper/solution.pdf`](paper/solution.pdf) · sources: [`paper/solution_ru.tpl.md`](paper/solution_ru.tpl.md)

| # | Claim | Status in the paper | Machine check |
|---|---|---|---|
| L1 | Letters in even positions from the end are never read | proved | `test_dead_letters_lemma` |
| L2 | Halt from length ≥2 only on `B` | proved | `test_halts_only_on_B` |
| T3 | \(\mathrm{B}^n \to \mathrm{B}^{T(n)}\) in \(n\) / \(n+1\) steps | proved | `test_collatz_macro_step` |
| F | \(S(n)=\sum(m + m \bmod 2)\); \(S(27)=40\,656\) | proved given the orbit reaches 1 | `test_halting_time_formula` |
| T4 | \((\mathrm{ACBACBBB})^k\mathrm{A}\) is a 4-cycle for every \(k\) | proved for all \(k\) | `test_infinite_cycle_family`; Lean \(k=1\) |
| N5 | Length ≤30 classes: 11 cycles, 0 unknown | enumeration: \(L\le 22\) two programs, 23..30 one | `rsrc`, `csrc/enum.c` → `results/enumeration.csv` |
| NF | After ≤ ⌈L/2⌉ steps the word is in the run language | proved + entry checked to length 20 | `src/tagsys/runs.py` |
| QR | Macro-step in the \((q,r)\) family; no halt if \(r\ge 2\) | proved | `test_qr_macro_law` |
| σ | Period of \(\sigma_k\) | conjecture; \(k\le 150\) enumerated | `scripts/sigma_law.py` |
| B1 | Block code: read 2, delete 4, any word | proved (full answer to question 3) | `test_block_binary_simulation` |
| B0 | Four suffixes on \(\{\mathrm{A},\mathrm{B}\}\), including BA; lockstep on \(\mathrm{B}^n\) | proved on the invariant class | `test_four_suffixes_ba_reachable_aa_unused`, `test_bin2_stepwise` |
| B2 | Cook cyclic tag system (6 phases) | proved, not a classical tag system | `test_cyclic_tag_simulation` |
| B3 | No small TS(2,2) with the dynamics of \(T\) | enumeration + De Mol 2010 | `csrc/search_ext.c` (48 231 288 systems) |
| I | Partial-delete convention → \(\mathrm{B}\leftrightarrow\mathrm{AC}\) ≙ Collatz \(1\leftrightarrow 2\) | proved | `test_partial_convention...` |

## Run
```bash
pip install -r requirements.txt
make -C csrc
./csrc/enum 2 22 > results/enumeration.csv 2> results/cycles_raw.txt
cargo run --release --manifest-path rsrc/Cargo.toml -- 2 30 > results/enumeration_rust.csv 2> results/enum_rust_log.txt
python tests/test_all.py        # or: pytest -q
python scripts/run_all.py       # tables and figures in results/ and figures/
```

## Layout
- `src/tagsys/`: core (`core.py`), Collatz link (`collatz.py`), cycles (`cycles.py`), binary analogues (`binary.py`)
- `csrc/`: fast exhaustive search (`enum.c`, Brent cycle detection) and binary-system search (`search_ext.c`; `search_binary.c` is the smaller first pass)
- `rsrc/`: independent Rust enumerator
- `tests/`: each paper claim as a test
- `docs/`: literature, oral-defence questions, AI disclosure
- `paper/`: solution text and PDF
- `lean/TagT4.lean`: Lean 4.34.1, `decide` for theorem 4 at \(k=1\) and traces \(\mathrm{B}^3\), \(\mathrm{B}^6\)

---

# «Сложная задача о простом алфавите»: исследование

Конкурс «Ход мысли», НИЯУ МИФИ, заочный тур 2026 · [условие](https://hod.mephi.ru/tasks/2026/simple-alphabet)

**Коротко.** Правила задачи — 2-tag система Поста, сопряжённая системе De Mol (2008), которая
считает ускоренный Коллатц. Остановка всех Б^n эквивалентна гипотезе Коллатца и открыта.
Остальное либо доказано в тексте `paper/`, либо проверено перебором до названной границы.
Тест в этом репозитории не заменяет доказательство: он ловит регресс чисел и формулировок.

| # | Утверждение | Статус в тексте | Машинная проверка |
|---|---|---|---|
| Л1 | Буквы на чётных местах с конца не читаются | доказано | `test_dead_letters_lemma` |
| Л2 | Остановка из длины ≥2 только на «Б» | доказано | `test_halts_only_on_B` |
| Т3 | Б^n → Б^T(n) за n / n+1 шагов | доказано | `test_collatz_macro_step` |
| Ф | S(n)=Σ(m + m mod 2); S(27)=40 656 | доказано при орбите до 1 | `test_halting_time_formula` |
| Т4 | (АВБАВБББ)^k А — цикл периода 4 | доказано для всех k | `test_infinite_cycle_family`; Lean k=1 |
| Н5 | Классы длины ≤30: 11 циклов, неизвестных 0 | перебор: L≤22 двумя программами, 23..30 одной | `rsrc`, `csrc/enum.c` → `results/enumeration.csv` |
| НФ | После ≤ ⌈L/2⌉ шагов — язык серий | доказано + вход до длины 20 | `src/tagsys/runs.py` |
| QR | Макрошаг в семействе (q, r); при r≥2 остановки нет | доказано | `test_qr_macro_law` |
| σ | Период σ_k | гипотеза; k≤150 перебор | `scripts/sigma_law.py` |
| Б1 | Блочный код: читаем 2, стираем 4, любое слово | доказано (полный ответ на вопрос 3) | `test_block_binary_simulation` |
| Б0 | Четыре суффикса {А,Б}, включая БА; на Б^n шаг в шаг | доказано на инвариантном классе | `test_four_suffixes_ba_reachable_aa_unused`, `test_bin2_stepwise` |
| Б2 | Циклическая tag-система Кука (6 фаз) | доказано, не классическая tag | `test_cyclic_tag_simulation` |
| Б3 | Нет малых TS(2,2) с динамикой T | перебор + аргумент De Mol 2010 | `csrc/search_ext.c` (48 231 288 систем) |
| И | «Стираем сколько есть» → Б↔АВ ≙ 1↔2 | доказано | `test_partial_convention...` |

## Запуск
```bash
pip install -r requirements.txt
make -C csrc
./csrc/enum 2 22 > results/enumeration.csv 2> results/cycles_raw.txt
cargo run --release --manifest-path rsrc/Cargo.toml -- 2 30 > results/enumeration_rust.csv 2> results/enum_rust_log.txt
python tests/test_all.py        # или: pytest -q
python scripts/run_all.py       # таблицы и рисунки в results/ и figures/
```

## Структура
- `src/tagsys/`: ядро (`core.py`), связь с Коллатцем (`collatz.py`), циклы (`cycles.py`), двоичные аналоги (`binary.py`)
- `csrc/`: быстрый полный перебор (`enum.c`, детекция циклов по Бренту) и поиск двоичных систем (`search_ext.c`; `search_binary.c` — меньший первый прогон)
- `rsrc/`: независимый перебор на Rust
- `tests/`: каждое утверждение работы в виде теста
- `docs/`: литература, вопросы для очного тура, раскрытие ИИ
- `paper/`: текст решения и PDF
- `lean/TagT4.lean`: Lean 4.34.1, `decide` для теоремы 4 при \(k=1\) и трасс Б^3, Б^6
