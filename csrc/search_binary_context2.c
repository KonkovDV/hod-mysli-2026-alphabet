/* Системы на {A,B}: правило зависит от двух последних букв, стираем фиксированное D,
 * продукция длины 0..3. Коды: A^n, B^n, A^n B, B A^n, B^n A, A B^n.
 * Первое возвращение к тому же виду кода обязано дать показатель T(n), n=2..40.
 * Это перепись search из аудита 28.09.2026; печать found — фактический счёт.
 */
#include <stdio.h>
#include <string.h>

#define NBUF 200000
static char buf[2 * NBUF];
static char P[4][8];
static int Lp[4];
static int D;

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
            if (e - s < 2 || e - s < D) return 0;
            int ctx = (buf[e - 2] == 'B') * 2 + (buf[e - 1] == 'B');
            int len = Lp[ctx];
            e -= D;
            if (s - len < 0) return 0;
            s -= len;
            if (len) memcpy(buf + s, P[ctx], (size_t)len);
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
    int opts[64][2], no = 0;
    const int ML = 3;
    long found = 0, tested = 0;
    for (int l = 0; l <= ML; l++)
        for (int m = 0; m < (1 << l); m++) { opts[no][0] = l; opts[no][1] = m; no++; }
    printf("CONTEXT2 prod_len=0..%d D=1..3 codes=6 n=2..40 productions=%d\n", ML, no);
    for (D = 1; D <= 3; D++)
        for (int i0 = 0; i0 < no; i0++)
            for (int i1 = 0; i1 < no; i1++)
                for (int i2 = 0; i2 < no; i2++)
                    for (int i3 = 0; i3 < no; i3++) {
                        int idx[4] = {i0, i1, i2, i3};
                        for (int c = 0; c < 4; c++) {
                            Lp[c] = opts[idx[c]][0];
                            for (int i = 0; i < Lp[c]; i++)
                                P[c][i] = (opts[idx[c]][1] >> i & 1) ? 'B' : 'A';
                        }
                        for (int t = 0; t < 6; t++) {
                            tested++;
                            if (test(t)) {
                                found++;
                                if (found <= 40)
                                    printf("HIT D=%d AA:%.*s AB:%.*s BA:%.*s BB:%.*s code %d\n",
                                           D, Lp[0], P[0], Lp[1], P[1], Lp[2], P[2], Lp[3], P[3], t);
                            }
                        }
                    }
    printf("TESTED %ld\nFOUND %ld\n", tested, found);
    return 0;
}
