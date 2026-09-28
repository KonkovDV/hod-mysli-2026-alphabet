/* Полный перебор 2-tag систем на {A,B,V}: читаем последнюю, стираем 2,
 * продукция зависит только от буквы. Ищем те, у которых X^n впервые
 * возвращается к X^{T(n)} для всех n=2..nmax.
 * T(n)=n/2 или (3n+sg)/2, sg=+1 (Коллатц) или sg=-1 (3n-1).
 * Запуск: search_unique_3letter [plus|minus|small]
 *   plus  (по умолчанию): sg=+1, продукции длины 0..3, n<=40
 *   minus: sg=-1, продукции длины 0..4, n<=40
 *   small: sg=+1, продукции длины 0..2, n<=20  (для CI)
 */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define NBUF 100000
static unsigned char buf[2 * NBUF];
static unsigned char P[3][8];
static int Lp[3];

static int Tsgn(int n, int sg) {
    if ((n & 1) == 0) return n / 2;
    return (3 * n + sg) / 2;
}

static int one_n(int X, int sg, int n) {
    int s = NBUF, e = NBUF, steps = 0, target = Tsgn(n, sg);
    for (int k = 0; k < n; k++) buf[e++] = (unsigned char)X;
    for (;;) {
        if (e - s < 2) return 0;
        int c = buf[e - 1];
        e -= 2;
        int L = Lp[c];
        s -= L;
        if (L) memcpy(buf + s, P[c], (size_t)L);
        if (++steps > 20000 || e - s > 3000) return 0;
        if (s < 5000) {
            int len = e - s;
            memmove(buf + NBUF, buf + s, (size_t)len);
            s = NBUF;
            e = NBUF + len;
        }
        int all = 1;
        for (int i = s; i < e; i++) if (buf[i] != (unsigned char)X) { all = 0; break; }
        if (all && e > s) return (e - s == target);
    }
}

static int test_all(int X, int sg, int nmax) {
    for (int n = 2; n <= nmax; n++) if (!one_n(X, sg, n)) return 0;
    return 1;
}

static int nprod(int maxlen) {
    int t = 0;
    for (int L = 0; L <= maxlen; L++) {
        int c = 1;
        for (int i = 0; i < L; i++) c *= 3;
        t += c;
    }
    return t;
}

/* m-я продукция в лексикографическом перечислении длин 0..maxlen, буквы — цифры base 3. */
static void setprod(int m, int maxlen, unsigned char *dst, int *len) {
    int base = 0;
    for (int L = 0; L <= maxlen; L++) {
        int cnt = 1;
        for (int i = 0; i < L; i++) cnt *= 3;
        if (m < base + cnt) {
            int x = m - base;
            *len = L;
            for (int i = 0; i < L; i++) { dst[i] = (unsigned char)(x % 3); x /= 3; }
            return;
        }
        base += cnt;
    }
    *len = 0;
}

int main(int argc, char **argv) {
    const char *mode = argc > 1 ? argv[1] : "plus";
    int sg = 1, maxlen = 3, nmax = 40;
    if (strcmp(mode, "minus") == 0) { sg = -1; maxlen = 4; }
    else if (strcmp(mode, "small") == 0) { sg = 1; maxlen = 2; nmax = 20; }
    else if (strcmp(mode, "plus") != 0) {
        fprintf(stderr, "usage: search_unique_3letter [plus|minus|small]\n");
        return 2;
    }
    int np = nprod(maxlen);
    long systems = (long)np * np * np;
    long found = 0;
    const char *nm = "ABV";
    printf("MODE %s sg=%d prod_len=0..%d n=2..%d systems=%ld\n", mode, sg, maxlen, nmax, systems);
    for (int a = 0; a < np; a++)
        for (int b = 0; b < np; b++)
            for (int c = 0; c < np; c++) {
                int id[3] = {a, b, c};
                for (int k = 0; k < 3; k++) setprod(id[k], maxlen, P[k], &Lp[k]);
                for (int X = 0; X < 3; X++) if (test_all(X, sg, nmax)) {
                    found++;
                    printf("HIT sg=%d X=%c ", sg, nm[X]);
                    for (int k = 0; k < 3; k++) {
                        printf("%c->", nm[k]);
                        for (int i = 0; i < Lp[k]; i++) putchar(nm[P[k][i]]);
                        if (k < 2) printf(" ");
                    }
                    printf("\n");
                }
            }
    printf("FOUND %ld\n", found);
    return 0;
}
