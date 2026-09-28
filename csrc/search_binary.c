/* Поиск ДВОИЧНЫХ tag-систем (алфавит {A,B}), которые на кодах X^n реализуют T(n)=n/2 | (3n+1)/2.
 * Перебор: удаление d=2..6, |X|<=3, длины продукций <=8. Результат (2026-09-28): НИ ОДНОЙ.
 * Классическая ориентация (читаем первую букву, стираем d, дописываем в конец) — эквивалентна
 * зеркальной. Проверка на n из tests[]. Время ~1 мин. */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#define CAP 4096
static char buf[CAP*4];
int T(int n){return n%2==0? n/2 : (3*n+1)/2;}
char P[2][16]; int PL[2]; char X[8]; int XL; int d;
int ispow(int i,int j){ int L=j-i; if(L%XL) return 0; for(int k=0;k<L;k++) if(buf[i+k]!=X[k%XL]) return 0; return L/XL; }
int nextpure(int n){
  int i=0,j=0; for(int k=0;k<n;k++) for(int t=0;t<XL;t++) buf[j++]=X[t];
  for(int st=0;st<3000;st++){
    if(j-i<d) return -1;
    int x=buf[i]; i+=d;
    if(j+PL[x]>=CAP*4){ memmove(buf,buf+i,j-i); j-=i; i=0; }
    memcpy(buf+j,P[x],PL[x]); j+=PL[x];
    if(j-i>1500) return -1;
    int m=ispow(i,j); if(m>0) return m;
  }
  return -1;
}
int main(int argc,char**argv){
  int tests[]={2,3,4,5,6,7,9,11,12,13,15,16,17,18,19,20,21,27,31};
  int nt=sizeof(tests)/sizeof(int);
  for(d=2; d<=6; d++)
  for(int xl=1;xl<=3;xl++) for(int xm=0;xm<(1<<xl);xm++){
    XL=xl; for(int t=0;t<xl;t++) X[t]=(xm>>t)&1;
    for(int l0=1;l0<=8;l0++) for(int m0=0;m0<(1<<l0);m0++)
    for(int l1=1;l1<=8;l1++) for(int m1=0;m1<(1<<l1);m1++){
      PL[0]=l0; PL[1]=l1;
      for(int t=0;t<l0;t++) P[0][t]=(m0>>t)&1;
      for(int t=0;t<l1;t++) P[1][t]=(m1>>t)&1;
      int ok=1;
      for(int k=0;k<nt;k++){ if(nextpure(tests[k])!=T(tests[k])){ok=0;break;} }
      if(ok){ printf("d=%d X=",d); for(int t=0;t<xl;t++)putchar('A'+X[t]);
        printf(" A->"); for(int t=0;t<l0;t++)putchar('A'+P[0][t]);
        printf(" B->"); for(int t=0;t<l1;t++)putchar('A'+P[1][t]); printf("\n"); fflush(stdout);}
    }
  }
  printf("DONE\n"); return 0;
}
