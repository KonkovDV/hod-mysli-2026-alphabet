/* N4. Алфавит {A,B}. Правило зависит только от последней буквы.
 * Стираем d[x] букв, d[A],d[B] in 1..4. Продукция длины 0..5.
 * Коды X^n, X^n Y, Y X^n для обоих выборов основной буквы (6 видов).
 * Приём: первое возвращение к тому же виду даёт показатель T(n), n=2..40.
 */
#include <stdio.h>
#include <string.h>

#define NBUF 200000
static char buf[2 * NBUF];
static char P[2][8];
static int Lp[2];
static int Del[2];

static int T(int n) { return (n & 1) ? (3 * n + 1) / 2 : n / 2; }

static void code(int t, int n, int *s, int *e) {
    int i = NBUF;
    *s = NBUF;
    if (t == 3) buf[i++] = 'B';
    if (t == 5) buf[i++] = 'A';
    for (int k = 0; k < n; k++) buf[i++] = (t == 1 || t == 4 || t == 5) ? 'B' : 'A';
    if (t == 2) buf[i++] = 'B';
    if (t == 4) buf[i++] = 'A';
    *e = i;
}

static int iscode(int t, int s, int e, int *n) {
    if (e - s < 1) return 0;
    char X = (t == 1 || t == 4 || t == 5) ? 'B' : 'A';
    char Y = (X == 'A') ? 'B' : 'A';
    int a = s, b = e;
    if (t == 2 || t == 4) { if (buf[e - 1] != Y) return 0; b--; }
    if (t == 3 || t == 5) { if (buf[s] != Y) return 0; a++; }
    for (int i = a; i < b; i++) if (buf[i] != X) return 0;
    *n = b - a;
    return *n >= 1;
}

static int test(int t) {
    for (int n = 2; n <= 40; n++) {
        int s, e, steps = 0, m;
        code(t, n, &s, &e);
        for (;;) {
            if (e - s < 2) return 0;
            int x = buf[e - 1] == 'B';
            int d = Del[x];
            if (e - s < d) return 0;
            int len = Lp[x];
            e -= d;
            if (s - len < 0) return 0;
            s -= len;
            if (len) memcpy(buf + s, P[x], (size_t)len);
            if (++steps > 20000 || e - s > 5000) return 0;
            if (s < 1000) {
                int L = e - s;
                memmove(buf + NBUF, buf + s, (size_t)L);
                s = NBUF;
                e = NBUF + L;
            }
            if (iscode(t, s, e, &m)) {
                if (m != T(n)) return 0;
                break;
            }
        }
    }
    return 1;
}

int main(void) {
    /* 0..5: 1+2+4+8+16+32 = 63 продукции */
    int opts[64][2], no = 0;
    long found = 0, tested = 0, systems = 0;
    for (int l = 0; l <= 5; l++)
        for (int m = 0; m < (1 << l); m++) { opts[no][0] = l; opts[no][1] = m; no++; }
    printf("VARDELETE d=1..4 prod_len=0..5 nprods=%d codes=6 n=2..40\n", no);
    for (int d0 = 1; d0 <= 4; d0++)
        for (int d1 = 1; d1 <= 4; d1++)
            for (int i0 = 0; i0 < no; i0++)
                for (int i1 = 0; i1 < no; i1++) {
                    systems++;
                    Del[0] = d0;
                    Del[1] = d1;
                    Lp[0] = opts[i0][0];
                    Lp[1] = opts[i1][0];
                    for (int i = 0; i < Lp[0]; i++) P[0][i] = (opts[i0][1] >> i & 1) ? 'B' : 'A';
                    for (int i = 0; i < Lp[1]; i++) P[1][i] = (opts[i1][1] >> i & 1) ? 'B' : 'A';
                    for (int t = 0; t < 6; t++) {
                        tested++;
                        if (test(t)) {
                            found++;
                            if (found <= 20)
                                printf("HIT dA=%d dB=%d A:%.*s B:%.*s code %d\n",
                                       d0, d1, Lp[0], P[0], Lp[1], P[1], t);
                        }
                    }
                }
    printf("SYSTEMS %ld\nTESTED %ld\nFOUND %ld\n", systems, tested, found);
    return 0;
}
