/* Расширенный поиск чистых 2-tag систем на алфавите {A,B}={0,1},
 * классическая ориентация (читаем первую букву, стираем d, дописываем в конец).
 *
 * Код числа n — слово X^n S, где суффикс S фиксирован (пустой S — это код X^n;
 * непустой покрывает схемы X^n Y и X^n YZ как один суффикс).
 * Система принимается, если для каждого тестового n ПЕРВОЕ возвращение слова
 * к виду X^m S имеет m = T(n) = n/2 | (3n+1)/2.
 *
 * Границы перебора печатаются в stdout и продублированы в results скриптом трека R5.
 * Параллелизм: один поток (tcc/gcc без OpenMP). Циклы по продукции независимы.
 */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#define CAP 8192
static char buf[CAP];
static char P0[32], P1[32], X[8], S[8];
static int PL0, PL1, XL, SL, d;
static unsigned long long nsys, nhit_n2;

int T(int n) { return (n % 2 == 0) ? n / 2 : (3 * n + 1) / 2; }

/* Первое m≥0, для которого слово равно X^m S; -1, если вид другой. */
static int parse_m(const char *b, int len) {
    if (len < SL) return -1;
    if (SL && memcmp(b + len - SL, S, SL) != 0) return -1;
    int body = len - SL;
    if (body % XL) return -1;
    for (int i = 0; i < body; i++) if (b[i] != X[i % XL]) return -1;
    return body / XL;
}

/* 1, если первое возвращение к коду есть именно T(n). */
static int evolves(int n) {
    int j = 0;
    for (int k = 0; k < n; k++) for (int t = 0; t < XL; t++) buf[j++] = X[t];
    for (int t = 0; t < SL; t++) buf[j++] = S[t];
    int i = 0;
    int target = T(n);
    for (int st = 0; st < 2500; st++) {
        int len = j - i;
        if (len < d) return 0;
        int x = buf[i];
        i += d;
        int pl = x ? PL1 : PL0;
        const char *p = x ? P1 : P0;
        if (j + pl >= CAP) {
            memmove(buf, buf + i, j - i);
            j -= i; i = 0;
        }
        memcpy(buf + j, p, pl);
        j += pl;
        len = j - i;
        if (len > 1500) return 0;
        int m = parse_m(buf + i, len);
        if (m >= 0) return m == target;
    }
    return 0;
}

static void dump_found(void) {
    printf("FOUND d=%d X=", d);
    for (int t = 0; t < XL; t++) putchar('A' + X[t]);
    printf(" S=");
    for (int t = 0; t < SL; t++) putchar('A' + S[t]);
    if (!SL) printf("-");
    printf(" A->");
    for (int t = 0; t < PL0; t++) putchar('A' + P0[t]);
    printf(" B->");
    for (int t = 0; t < PL1; t++) putchar('A' + P1[t]);
    printf("\n");
    fflush(stdout);
}

int main(void) {
    /* Границы. Менять только вместе с отчётом R5. */
    const int DMIN = 2, DMAX = 8;
    const int XLMIN = 1, XLMAX = 3;
    const int SLMAX = 4;
    const int PLMAX = 6;
    int tests[] = {2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 15, 16, 27};
    int nt = (int)(sizeof(tests) / sizeof(tests[0]));
    printf("BOUNDS d=%d..%d |X|=%d..%d |S|=0..%d |P|=1..%d tests=%d orientation=classic\n",
           DMIN, DMAX, XLMIN, XLMAX, SLMAX, PLMAX, nt);
    fflush(stdout);
    nsys = 0; nhit_n2 = 0;
    for (d = DMIN; d <= DMAX; d++) {
        for (XL = XLMIN; XL <= XLMAX; XL++) {
            for (int xm = 0; xm < (1 << XL); xm++) {
                for (int t = 0; t < XL; t++) X[t] = (xm >> t) & 1;
                for (SL = 0; SL <= SLMAX; SL++) {
                    int smax = SL ? (1 << SL) : 1;
                    for (int sm = 0; sm < smax; sm++) {
                        for (int t = 0; t < SL; t++) S[t] = (sm >> t) & 1;
                        for (PL0 = 1; PL0 <= PLMAX; PL0++) {
                            for (int m0 = 0; m0 < (1 << PL0); m0++) {
                                for (int t = 0; t < PL0; t++) P0[t] = (m0 >> t) & 1;
                                for (PL1 = 1; PL1 <= PLMAX; PL1++) {
                                    for (int m1 = 0; m1 < (1 << PL1); m1++) {
                                        nsys++;
                                        for (int t = 0; t < PL1; t++) P1[t] = (m1 >> t) & 1;
                                        if ((nsys & 0x1ffff) == 0) {
                                            fprintf(stderr, "progress systems=%llu d=%d\n", nsys, d);
                                            fflush(stderr);
                                        }
                                        if (!evolves(2)) continue;
                                        nhit_n2++;
                                        int ok = 1;
                                        for (int k = 1; k < nt; k++) {
                                            if (!evolves(tests[k])) { ok = 0; break; }
                                        }
                                        if (ok) dump_found();
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        fprintf(stderr, "d=%d done, systems=%llu passed_n2=%llu\n", d, nsys, nhit_n2);
    }
    printf("SYSTEMS %llu\nPASSED_N2 %llu\nDONE\n", nsys, nhit_n2);
    return 0;
}
