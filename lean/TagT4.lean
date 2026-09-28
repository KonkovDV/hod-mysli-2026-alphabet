/- Lean 4.34.1, без Mathlib и без sorry.
   Собрано командой `lean TagT4.lean` (код выхода 0).
   Кодировка: w — список букв слева направо; читаем ПОСЛЕДНЮЮ, стираем две последние, пишем в НАЧАЛО.
   Это проверка частных случаев, не индукция для всех k и всех n. -/
inductive Ltr | A | B | C
  deriving DecidableEq, Repr
open Ltr

def prod : Ltr → List Ltr
  | A => [B, B, B]
  | B => [A, C]
  | C => [B]

def step (w : List Ltr) : Option (List Ltr) :=
  match w.reverse with
  | x :: _ :: rest => some (prod x ++ rest.reverse)
  | _ => none

def X : List Ltr := [A, C, B, A, C, B, B, B]   -- АВБАВБББ

-- Т4 при k = 1: слово X·А возвращается в себя ровно за 4 шага.
-- Период делит 4; шаги 1 и 2 исключают делители 1 и 2, остаётся ровно 4.
example : (step (X ++ [A]) >>= step >>= step >>= step) = some (X ++ [A]) := by decide
example : step (X ++ [A]) ≠ some (X ++ [A]) := by decide
example : (step (X ++ [A]) >>= step) ≠ some (X ++ [A]) := by decide

-- Т3 на двух трассах. Общая индукция для всех n здесь не утверждается.
def iter : Nat → List Ltr → Option (List Ltr)
  | 0, w => some w
  | n+1, w => step w >>= iter n
example : iter 4 (List.replicate 3 B) = some (List.replicate 5 B) := by decide  -- Б^3 → Б^5 за 4 шага
example : iter 6 (List.replicate 6 B) = some (List.replicate 3 B) := by decide  -- Б^6 → Б^3 за 6 шагов
