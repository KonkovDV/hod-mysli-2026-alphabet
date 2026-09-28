//! Параллельный перебор классов 2-tag системы.
//!
//! Внутренний шаг не трогает общую память: атомик один, и он только раздаёт
//! номера классов (`fetch_add`). Так сделан динамический планировщик OpenMP и
//! обходы Коллатца у Barina: работа разная по длительности, воровать её нужно
//! пачками, а не ставить атомарный счётчик на каждый шаг. Шаг с атомиком
//! гонял бы одну кэш-линию между ядрами и был бы медленнее однопоточного кода.
//!
//! Сравнение слов — AVX2, если диапазон лежит в кольцевом буфере сплошняком
//! (это почти всегда: буфер 2 МиБ, слово короче). AVX-512 на i5-13600KF нет.
//! Детекция цикла — алгоритм Брента, тот же, что в `csrc/enum.c`, чтобы
//! периоды и канонические слова совпали с уже посчитанным каталогом.

use std::arch::x86_64::{
    _mm256_cmpeq_epi8, _mm256_loadu_si256, _mm256_movemask_epi8, __m256i,
};
use std::collections::HashMap;
use std::io::{self, Write};
use std::ptr;
use std::sync::atomic::{AtomicU64, Ordering};
use std::thread;
use std::time::Instant;

const CAP: usize = 1 << 21;
const MASK: u32 = (CAP as u32) - 1;
const MAXLEN: u32 = 1_000_000;
const MAXSTEPS: u64 = 200_000_000;
const CHUNK: u64 = 32;

#[repr(C, align(64))]
struct Cursor {
    next: AtomicU64,
}

struct Ring {
    data: Box<[u8]>,
    h: u32,
    t: u32,
}

impl Ring {
    fn new() -> Self {
        Self {
            data: vec![0u8; CAP].into_boxed_slice(),
            h: 0,
            t: 0,
        }
    }

    #[inline(always)]
    fn len(&self) -> u32 {
        self.t.wrapping_sub(self.h)
    }

    #[inline(always)]
    fn idx(&self, i: u32) -> usize {
(self.h.wrapping_add(i) & MASK) as usize
    }

    #[inline(always)]
    unsafe fn contig(&self, n: usize) -> Option<*const u8> {
        let start = (self.h & MASK) as usize;
        if start + n <= CAP {
            Some(self.data.as_ptr().add(start))
        } else {
            None
        }
    }

    fn load_class(&mut self, l: usize, code: u64) {
        self.h = 0;
        self.t = l as u32;
        unsafe {
            let p = self.data.as_mut_ptr();
            for i in 0..l {
                *p.add(i) = 1;
            }
            let mut x = code;
            let nr = (l + 1) / 2;
            for k in 0..nr {
                *p.add(2 * k) = (x % 3) as u8;
                x /= 3;
            }
        }
    }

    fn copy_from(&mut self, src: &Ring) {
        let n = src.len();
        self.h = 0;
        self.t = n;
        let n = n as usize;
        unsafe {
            if let Some(p) = src.contig(n) {
                ptr::copy_nonoverlapping(p, self.data.as_mut_ptr(), n);
            } else {
                for i in 0..n {
                    *self.data.get_unchecked_mut(i) = *src.data.get_unchecked(src.idx(i as u32));
                }
            }
        }
    }

    /// Читаем первый байт перевёрнутого слова, стираем два, дописываем
    /// перевёрнутую продукцию: A→111, B→20 (это «CA»), C→1.
    #[inline(always)]
    fn step(&mut self) -> bool {
        if self.len() < 2 {
            return false;
        }
        unsafe {
            let x = *self.data.get_unchecked((self.h & MASK) as usize);
            self.h = self.h.wrapping_add(2);
            let t0 = self.t;
            let base = self.data.as_mut_ptr();
            match x {
                0 => {
                    *base.add((t0 & MASK) as usize) = 1;
                    *base.add((t0.wrapping_add(1) & MASK) as usize) = 1;
                    *base.add((t0.wrapping_add(2) & MASK) as usize) = 1;
                    self.t = t0.wrapping_add(3);
                }
                1 => {
                    *base.add((t0 & MASK) as usize) = 2;
                    *base.add((t0.wrapping_add(1) & MASK) as usize) = 0;
                    self.t = t0.wrapping_add(2);
                }
                _ => {
                    *base.add((t0 & MASK) as usize) = 1;
                    self.t = t0.wrapping_add(1);
                }
            }
        }
        true
    }
}

#[inline(always)]
unsafe fn eq_words(a: *const u8, b: *const u8, n: usize) -> bool {
    let mut i = 0;
    while i + 8 <= n {
        let xa = (a.add(i) as *const u64).read_unaligned();
        let xb = (b.add(i) as *const u64).read_unaligned();
        if xa != xb {
            return false;
        }
        i += 8;
    }
    while i < n {
        if *a.add(i) != *b.add(i) {
            return false;
        }
        i += 1;
    }
    true
}

#[target_feature(enable = "avx2")]
#[inline]
unsafe fn eq_avx2(a: *const u8, b: *const u8, n: usize) -> bool {
    let mut i = 0;
    while i + 32 <= n {
        let va = _mm256_loadu_si256(a.add(i) as *const __m256i);
        let vb = _mm256_loadu_si256(b.add(i) as *const __m256i);
        let cmp = _mm256_cmpeq_epi8(va, vb);
        if _mm256_movemask_epi8(cmp) != -1 {
            return false;
        }
        i += 32;
    }
    eq_words(a.add(i), b.add(i), n - i)
}

#[inline(always)]
fn rings_eq(a: &Ring, b: &Ring) -> bool {
    let n = a.len();
    if n != b.len() {
        return false;
    }
    if n == 0 {
        return true;
    }
    let n = n as usize;
    unsafe {
        let a0 = *a.data.get_unchecked(a.idx(0));
        let b0 = *b.data.get_unchecked(b.idx(0));
        if a0 != b0 {
            return false;
        }
        if n > 1 {
            let ae = *a.data.get_unchecked(a.idx((n as u32) - 1));
            let be = *b.data.get_unchecked(b.idx((n as u32) - 1));
            if ae != be {
                return false;
            }
        }
        match (a.contig(n), b.contig(n)) {
            (Some(pa), Some(pb)) => {
                if cfg!(target_feature = "avx2") && n >= 32 {
                    eq_avx2(pa, pb, n)
                } else {
                    eq_words(pa, pb, n)
                }
            }
            _ => {
                for i in 0..n as u32 {
                    if *a.data.get_unchecked(a.idx(i)) != *b.data.get_unchecked(b.idx(i)) {
                        return false;
                    }
                }
                true
            }
        }
    }
}

fn to_original(q: &Ring) -> String {
    let n = q.len();
    let mut out = vec![0u8; n as usize];
    for i in 0..n {
        let b = unsafe { *q.data.get_unchecked(q.idx(n - 1 - i)) };
        out[i as usize] = b"ABC"[b as usize];
    }
    String::from_utf8(out).unwrap_or_default()
}

fn word_from_code(l: usize, code: u64) -> String {
    let mut o = vec![b'B'; l];
    let mut x = code;
    let nr = (l + 1) / 2;
    for k in 0..nr {
        let digit = (x % 3) as usize;
        o[l - 1 - 2 * k] = b"ABC"[digit];
        x /= 3;
    }
    String::from_utf8(o).unwrap_or_default()
}

struct CycleRec {
    period: u64,
    min_len: i32,
    max_len: i32,
}

struct Acc {
    halt: u64,
    cycle: u64,
    unknown: u64,
    best_steps: i64,
    best_code: u64,
    cycles: HashMap<String, CycleRec>,
}

impl Acc {
    fn new() -> Self {
        Self {
            halt: 0,
            cycle: 0,
            unknown: 0,
            best_steps: -1,
            best_code: 0,
            cycles: HashMap::new(),
        }
    }

    fn note_halt(&mut self, steps: i64, code: u64) {
        self.halt += 1;
        if steps > self.best_steps || (steps == self.best_steps && code < self.best_code) {
            self.best_steps = steps;
            self.best_code = code;
        }
    }

    fn merge(&mut self, part: Acc) {
        self.halt += part.halt;
        self.cycle += part.cycle;
        self.unknown += part.unknown;
        if part.best_steps > self.best_steps
            || (part.best_steps >= 0
                && part.best_steps == self.best_steps
                && part.best_code < self.best_code)
        {
            self.best_steps = part.best_steps;
            self.best_code = part.best_code;
        }
        for (k, v) in part.cycles {
            self.cycles.entry(k).or_insert(v);
        }
    }
}

#[inline(never)]
fn canonical(src: &Ring, lam: u64, tmp: &mut Ring) -> (String, i32, i32) {
    tmp.copy_from(src);
    let mut best = to_original(tmp);
    let mut min_l = tmp.len() as i32;
    let mut max_l = min_l;
    for _ in 1..lam {
        if !tmp.step() {
            break;
        }
        let n = tmp.len() as i32;
        if n < min_l {
            min_l = n;
        }
        if n > max_l {
            max_l = n;
        }
        let cur = to_original(tmp);
        if cur < best {
            best = cur;
        }
    }
    (best, min_l, max_l)
}

#[cold]
#[inline(never)]
fn note_unknown(acc: &mut Acc) {
    acc.unknown += 1;
}

#[cold]
#[inline(never)]
fn note_cycle(hare: &Ring, lam: u64, tmp: &mut Ring, acc: &mut Acc) {
    let (word, min_l, max_l) = canonical(hare, lam, tmp);
    acc.cycles.entry(word).or_insert(CycleRec {
        period: lam,
        min_len: min_l,
        max_len: max_l,
    });
    acc.cycle += 1;
}

fn run_class(l: usize, code: u64, tortoise: &mut Ring, hare: &mut Ring, tmp: &mut Ring, acc: &mut Acc) {
    hare.load_class(l, code);
    tortoise.copy_from(hare);
    let mut power: u64 = 1;
    let mut lam: u64 = 1;
    let mut total: u64 = 0;
    loop {
        if !hare.step() {
            // Снимок Брента — не начальное слово. Длину остановки считаем заново от кода класса.
            tmp.load_class(l, code);
            let mut k = 0u64;
            while tmp.step() {
                k += 1;
            }
            acc.note_halt(k as i64, code);
            return;
        }
        total += 1;
        if hare.len() > MAXLEN || total > MAXSTEPS {
            note_unknown(acc);
            return;
        }
        if rings_eq(tortoise, hare) {
            note_cycle(hare, lam, tmp, acc);
            return;
        }
        if power == lam {
            tortoise.copy_from(hare);
            power = power.saturating_mul(2);
            lam = 0;
        }
        lam += 1;
    }
}

fn worker(l: usize, cls: u64, cursor: &Cursor) -> Acc {
    let mut tortoise = Ring::new();
    let mut hare = Ring::new();
    let mut tmp = Ring::new();
    let mut acc = Acc::new();
    loop {
        let start = cursor.next.fetch_add(CHUNK, Ordering::Relaxed);
        if start >= cls {
            break;
        }
        let end = (start + CHUNK).min(cls);
        for code in start..end {
            run_class(l, code, &mut tortoise, &mut hare, &mut tmp, &mut acc);
        }
    }
    acc
}

fn enumerate_length(l: usize, threads: usize) -> Acc {
    let nr = (l + 1) / 2;
    let mut cls = 1u64;
    for _ in 0..nr {
        cls = cls.saturating_mul(3);
    }
    let cursor = Cursor {
        next: AtomicU64::new(0),
    };
    let started = Instant::now();
    let mut total = Acc::new();
    thread::scope(|scope| {
        let mut handles = Vec::with_capacity(threads);
        for _ in 0..threads {
            handles.push(scope.spawn(|| worker(l, cls, &cursor)));
        }
        for h in handles {
            total.merge(h.join().expect("поток перебора"));
        }
    });
    let secs = started.elapsed().as_secs_f64();
    let word = if total.best_steps < 0 {
        String::new()
    } else {
        word_from_code(l, total.best_code)
    };
    let stdout = io::stdout();
    let mut out = stdout.lock();
    let _ = writeln!(
        out,
        "{l},{cls},{},{},{},{},{word}",
        total.halt, total.cycle, total.unknown, total.best_steps
    );
    let _ = out.flush();
    let mut cycles: Vec<_> = total.cycles.iter().collect();
    cycles.sort_by(|a, b| a.0.cmp(b.0));
    let stderr = io::stderr();
    let mut err = stderr.lock();
    for (w, rec) in &cycles {
        let _ = writeln!(
            err,
            "CYCLE,{l},{},{},{},{w}",
            rec.period, rec.min_len, rec.max_len
        );
    }
    let _ = writeln!(
        err,
        "L={l} classes={cls} threads={threads} {:.2}s {:.0} cls/s",
        secs,
        cls as f64 / secs.max(1e-9)
    );
    total
}

fn main() {
    let mut args = std::env::args().skip(1);
    let lmin: usize = args.next().and_then(|s| s.parse().ok()).unwrap_or(2);
    let lmax: usize = args.next().and_then(|s| s.parse().ok()).unwrap_or(20);
    let threads: usize = args.next().and_then(|s| s.parse().ok()).unwrap_or_else(|| {
        thread::available_parallelism().map(|n| n.get()).unwrap_or(1)
    });
    if lmin < 2 || lmax < lmin || lmax > 40 {
        eprintln!("usage: enum_rs Lmin Lmax [threads]   (2 ≤ Lmin ≤ Lmax ≤ 40)");
        std::process::exit(2);
    }
    eprintln!(
        "enum_rs threads={threads} avx2={} chunk={CHUNK}",
        cfg!(target_feature = "avx2")
    );
    println!("L,classes,halt,cycle,unknown,max_steps_to_halt,argmax_word");
    for l in lmin..=lmax {
        enumerate_length(l, threads);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn code_zero_length_two_is_ba() {
        assert_eq!(word_from_code(2, 0), "BA");
        assert_eq!(word_from_code(2, 1), "BB");
        assert_eq!(word_from_code(2, 2), "BC");
    }

    #[test]
    fn one_step_of_bbb() {
        let mut r = Ring::new();
        r.load_class(3, 0); // читаемая буква A? L=3, nr=2, code 0 → обе живые A
        // не важно: все B это код, у которого цифры равны 1
        r.load_class(3, 1 + 3); // цифры 1,1 → слово BBB, reversed тоже BBB
        assert!(r.step());
        assert_eq!(to_original(&r), "ACB");
    }
}
