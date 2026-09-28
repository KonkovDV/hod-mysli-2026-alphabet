/* Exhaustive enumeration of the 2-tag system  A->BBB, B->AC, C->B  (read LAST letter,
 * erase last two, prepend production).  Letters: 0=A(А) 1=B(Б) 2=C(В).
 * By the dead-letter lemma only letters at odd positions from the end matter, so for
 * length L we enumerate 3^ceil(L/2) classes (unread positions filled with B).
 * Internally we store the REVERSED word (read first letter, delete 2, append) in a
 * ring buffer.  Cycle detection: Brent's algorithm.  Output CSV to stdout:
 *   L,halt,cycle,unknown,max_steps_to_halt,argmax_word
 * and cycles (canonical = lexicographically minimal rotation of orbit) to stderr:
 *   CYCLE,L_first_seen,period,minlen,maxlen,word
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CAP (1<<21)
#define MASK (CAP-1)
#define MAXLEN 1000000
#define MAXSTEPS 200000000L
/* reversed storage => append REVERSED productions: rev(AC)=CA */
static const char *PROD[3]={"\1\1\1","\2\0","\1"}; static const int PL[3]={3,2,1};
typedef struct { unsigned char b[CAP]; unsigned h,t; } Q;   /* word = b[h..t) */
static inline unsigned qlen(const Q*q){return q->t-q->h;}
static int step(Q*q){ if(qlen(q)<2) return 0; int x=q->b[q->h&MASK]; q->h+=2;
  for(int i=0;i<PL[x];i++) q->b[(q->t++)&MASK]=PROD[x][i]; return 1; }
static int qeq(const Q*a,const Q*b){ unsigned n=qlen(a); if(n!=qlen(b)) return 0;
  for(unsigned i=0;i<n;i++) if(a->b[(a->h+i)&MASK]!=b->b[(b->h+i)&MASK]) return 0; return 1; }
static void qcopy(Q*d,const Q*s){ unsigned n=qlen(s); d->h=0; d->t=n; for(unsigned i=0;i<n;i++) d->b[i]=s->b[(s->h+i)&MASK]; }
static void qstr(const Q*q,char*out){ /* print in ORIGINAL orientation (reverse back) */
  unsigned n=qlen(q); const char *L="ABC"; for(unsigned i=0;i<n;i++) out[i]=L[q->b[(q->h+n-1-i)&MASK]]; out[n]=0; }
#define MAXCYC 4096
static char *cyc_key[MAXCYC]; static int ncyc=0;
static int seen_cycle(const char*k){ for(int i=0;i<ncyc;i++) if(!strcmp(cyc_key[i],k)) return 1; return 0; }
/* returns 0 halt,1 cycle,2 unknown; *steps = steps to halt or mu+lambda */
static Q A,Bq,tmp;
static int run(Q*start,long*steps,int L){
  qcopy(&A,start); qcopy(&Bq,start); long power=1,lam=1; long total=0;
  /* Brent: tortoise=A saved, hare=Bq */
  for(;;){
    if(!step(&Bq)){ *steps=total+1-1+0; /* recompute exactly below */ break; }
    total++;
    if(qlen(&Bq)>MAXLEN||total>MAXSTEPS){ *steps=total; return 2; }
    if(qeq(&A,&Bq)){ /* cycle of length lam; extract canonical rep */
      static Q c; qcopy(&c,&Bq); static char best[MAXLEN+1], cur[MAXLEN+1]; qstr(&c,best);
      int minl=qlen(&c),maxl=qlen(&c);
      for(long i=1;i<lam;i++){ step(&c); qstr(&c,cur); if(strcmp(cur,best)<0) strcpy(best,cur);
        if((int)qlen(&c)<minl)minl=qlen(&c); if((int)qlen(&c)>maxl)maxl=qlen(&c);} 
      if(!seen_cycle(best)&&ncyc<MAXCYC){ cyc_key[ncyc++]=strdup(best);
        fprintf(stderr,"CYCLE,%d,%ld,%d,%d,%s\n",L,lam,minl,maxl,best); }
      *steps=total; return 1; }
    if(power==lam){ qcopy(&A,&Bq); power*=2; lam=0; }
    lam++;
  }
  /* halted: count exact steps */
  qcopy(&tmp,start); long k=0; while(step(&tmp)) k++; *steps=k; return 0;
}
int main(int argc,char**argv){
  int Lmin=argc>1?atoi(argv[1]):2, Lmax=argc>2?atoi(argv[2]):20;
  printf("L,classes,halt,cycle,unknown,max_steps_to_halt,argmax_word\n");
  static Q w; static char buf[MAXLEN+1];
  for(int L=Lmin;L<=Lmax;L++){
    int nr=(L+1)/2; long cls=1; for(int i=0;i<nr;i++) cls*=3;
    long h=0,c=0,u=0,best=-1; char bw[64]="";
    for(long code=0;code<cls;code++){
      /* original word o[0..L-1]; read positions from end: L-1, L-3, ... ; others = B */
      unsigned char o[256]; for(int i=0;i<L;i++) o[i]=1; long x=code;
      for(int i=0;i<nr;i++){ o[L-1-2*i]=x%3; x/=3; }
      w.h=0; w.t=L; for(int i=0;i<L;i++) w.b[i]=o[L-1-i];   /* reversed */
      long st; int r=run(&w,&st,L);
      if(r==0){h++; if(st>best){best=st; qstr(&w,buf); strncpy(bw,buf,63);} } else if(r==1)c++; else u++;
    }
    printf("%d,%ld,%ld,%ld,%ld,%ld,%s\n",L,cls,h,c,u,best,bw); fflush(stdout);
  }
  return 0;
}
