#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <sys/time.h>
#include <time.h>

#define MAX_HEAP_SIZE   10
#define MAX_QUERY_LEN   40
#define QUEUEING    0x0001
#define VOTING      0x0002


/* Data model */
/* ========== */

typedef struct Query {
    char query[MAX_QUERY_LEN+1];
    struct timeval ts_created;
    unsigned int votes;
} Query;

void Query_init(Query **new)
{
    *new = malloc(sizeof(Query));
    strcpy((*new)->query, "");
    gettimeofday(&(*new)->ts_created, NULL);
    (*new)->votes = 0;
}

void Query_dest(Query **old)
{
    free(*old);
    *old = NULL;
}

int ts_cmp(struct timeval *ts1, struct timeval *ts2)
{   /* compare two timeval structs */

    if (ts1->tv_sec < ts2->tv_sec)
        return -1;
    if (ts1->tv_sec > ts2->tv_sec)
        return 1;
    if (ts1->tv_usec < ts2->tv_usec)
        return -1;
    if (ts1->tv_usec > ts2->tv_usec)
        return 1;
    return 0;
}

int query_cmp(Query *q1, Query *q2)
{   /* Compare queries on votes and then time created (earlier wins). */

    if (q1->votes < q2->votes)
        return -1;
    if (q1->votes > q2->votes)
        return 1;
    return (1 == ts_cmp(&q1->ts_created, &q2->ts_created)) ? -1 : 1;
}


/* Heap
 * ====

 * Heaps per CLRS (chapter 6) are 1-indexed so that the parent/left/right math 
 * works. Since our arrays here are 0-indexed we need to tweak the algorithms
 * slightly. The way I do it here is:
  
 *      o leave element 0 in the heap array unused
 *      o make g_heap_size be 1 larger than the actual size of the heap
       
 * This allows us to use g_heap_size as an index without subtracting one, and
 * as a < target in for loops, though remember to start such loops at 1.

 */


Query *g_heap[MAX_HEAP_SIZE+1]; /* heap of queries; +1 because 0 is unused */
int g_heap_size = 1;            /* heap helper; starts empty; empty = 1 */

#define m_parent(i)  (i >> 1)
#define m_left(i)    (i << 1)
#define m_right(i)  ((i << 1) + 1)

void swap(int i, int j)
{   
    Query *tmp = g_heap[i];
    g_heap[i] = g_heap[j];
    g_heap[j] = tmp;
}

void heapify(int i)
{
    int left = m_left(i);
    int right = m_right(i);
    int largest = i;

    if (left && left < g_heap_size)
        if (1 == query_cmp(g_heap[left], g_heap[i]))
            largest = left;

    if (right && right < g_heap_size)
        if (1 == query_cmp(g_heap[right], g_heap[largest]))
            largest = right;

    if (largest != i)
    {
        swap(i, largest);
        heapify(largest);
    }
}

void sort()
{   /* in-place heapsort; you don't have a heap anymore after this */

    int i;
    for (i=g_heap_size-1; i>1; i--)
    {
        swap(1, i);
        g_heap_size--;
        heapify(1);
    }
}


/* CLI usage helpers */
/* ================= */

void error(char *msg)
{
    printf("%s\n", msg);
    exit(EXIT_FAILURE);
}

void usage()
{
    error("usage: return ~/file.dat {next,list,future,\"query\"}");
}


/* File I/O */
/* ======== */

time_t g_oldest = 0;            /* timestamp of oldest entry in the queue */
time_t g_voting_deadline = 0;   /* timestamp in the future when voting ends
                                    this is set when the queue fills up */


void write_int(FILE *fp, int *i)
{   /* helper to write an int to disk */
    if (1 != fwrite(i, sizeof(i), 1, fp))
        error("We couldn't write to the data file.");
}

void write_time_t(FILE *fp, time_t *t)
{   /* helper to write an int to disk */
    if (1 != fwrite(t, sizeof(t), 1, fp))
        error("We couldn't write to the data file.");
}
  
int read_int(FILE *fp)
{   /* helper to read an int from disk */
    int i;
    if (1 != fread(&i, sizeof(i), 1, fp))
    {
        if (ferror(fp))
            error("We couldn't read from the data file.");
        else
            error("Corrupt data file.");
    }
    return i;
}

time_t read_time_t(FILE *fp)
{   /* helper to read a time_t from disk */
    int t;
    if (1 != fread(&t, sizeof(t), 1, fp))
    {
        if (ferror(fp))
            error("We couldn't read from the data file.");
        else
            error("Corrupt data file.");
    }
    return t;
}


void dump(char *filename)
{   /* write the heap to a binary file */

    FILE *fp;
    int i;

    if (NULL == (fp = fopen(filename, "w+")))
        error("We couldn't open the data file for writing.");

    write_int(fp, &g_heap_size);
    write_time_t(fp, &g_oldest);
    write_time_t(fp, &g_voting_deadline);

    for (i=1; i<g_heap_size; i++)
    {
        if (fwrite(g_heap[i], sizeof(**g_heap), 1, fp) != 1)
            error("We couldn't write an entry to the data file.");
        Query_dest(&g_heap[i]);
    }

    if (fclose(fp))
        error("We couldn't close the data file after writing.");

}


void load(char *filename)
{   /* load the heap from a binary file */

    FILE *fp;
    int i;

    if (NULL == (fp = fopen(filename, "r")))
        return;         /* file doesn't exist; will create on exit */

    g_heap_size = read_int(fp);
    g_oldest = read_time_t(fp);
    g_voting_deadline = read_time_t(fp);

    /*
    if (fread(&g_heap_size, sizeof(g_heap_size), 1, fp) != 1)
    {
        if (ferror(fp))
            error("We couldn't read from the data file.");
        else
            error("Corrupt data file.")
    }
    */

    for (i=1; i<g_heap_size; i++)
    {
        Query *rec;
        Query_init(&rec);
        if (fread(rec, sizeof(*rec), 1, fp) != 1)
        {
            if (ferror(fp))
                error("We couldn't read an entry from the data file.");
            else
                error("The data file is corrupt.");
        }
        g_heap[i] = rec;
    }

    if (fclose(fp))
        error("We couldn't close the data file after reading.");

}


/* Output routines
 * ===============

 * When these are invoked, we don't rewrite the data file, so we can safely use
 * an in-place heapsort. However, sort() destroys g_heap_size, so we have to 
 * store that value locally before calling sort. Also note that sort() sorts 
 * the array in ascending order. We actually want to reverse that semantic in
 * list/future.

 */


int deadline()
{
    printf("%d", (int)g_voting_deadline);
    return 0;
}


int list()
{   /* used in tests; votes,query in forward order */

    int i,heap_size=g_heap_size;

    sort();
    for (i=heap_size-1; i>0; i--)
    {
        printf("%d,%d,%s\n", heap_size-i, g_heap[i]->votes, g_heap[i]->query);
        Query_dest(&g_heap[i]);
    }

    return 0;
}


int future()
{   /* used from the web; vote,time,query in reverse order */
    
    int i,heap_size=g_heap_size;
    
    sort();
    for (i=1; i<heap_size; i++)
    {
        printf( "%d,%ld.%ld,%s\n"
              , g_heap[i]->votes
              , g_heap[i]->ts_created.tv_sec
              , g_heap[i]->ts_created.tv_usec
              , g_heap[i]->query
               );
        Query_dest(&g_heap[i]);
    }
    return 0;
}


/* Manipulation routines */
/* ===================== */
/* These all result in the data file being rewritten. */

void clear()
{   /* Clear the queue. */

    while (g_heap_size > 1)
        Query_dest(&g_heap[g_heap_size--]);
    g_voting_deadline = 0;
    g_oldest = 0;

}


void next(char *logfilename)
{   /* output the next query in the queue; write to logfile; clear queue 
        if we are in the voting period, then return the timestamp when the 
        voting period ends, and the empty string
     
     */

    FILE *fp;
    struct timeval now;


    /* Return early if we can. */
    /* ======================= */

    if (g_heap_size <= MAX_HEAP_SIZE)
        return;

    if (g_voting_deadline > time(NULL))
    {
        printf("%d,", (int)g_voting_deadline);
        return;
    }


    /* Log to file and print to stdout. */
    /* ================================ */

    if (NULL == (fp = fopen(logfilename, "a")))
        error("We couldn't open the log file.");

    gettimeofday(&now, NULL);

    fprintf( fp
           , "%d,%ld.%ld,%ld.%ld,%s\n"
           , g_heap[1]->votes
           , g_heap[1]->ts_created.tv_sec
           , g_heap[1]->ts_created.tv_usec
           , now.tv_sec
           , now.tv_usec 
           , g_heap[1]->query
            );

    if (fclose(fp))
        error("We couldn't close the log file.");

    printf("%ld.%ld,%s", now.tv_sec, now.tv_usec, g_heap[1]->query);

    clear();

}


void upvote(short i)
{   /* upvote the query at g_heap[i] */

    int parent;

    if (g_voting_deadline && g_voting_deadline < time(NULL))
        error("Sorry, voting is closed.");
    if (!g_voting_deadline)
    {
        return; /* silently ignore duplicates during competition */
    }

    if (UINT_MAX == g_heap[i]->votes)
        {} /* silently ignore requests to push votes beyond max possible */
    else
    {
        g_heap[i]->votes++;

        while (i > 1)
        {
            parent = m_parent(i);
            if (1 == query_cmp(g_heap[parent], g_heap[i]))
                break; /* parent > child */
            swap(i, parent);
            i = parent;
        }
    }
}


void schedule(char *query)
{   /* add a query to the queue */

    if (MAX_HEAP_SIZE < g_heap_size)
        error("Sorry, the queue is full. Time for voting!");
    else
    {
        Query *new;
        Query_init(&new);
        strcpy(new->query, query);
        g_heap[g_heap_size++] = new;

        /*printf("%d < %d", MAX_HEAP_SIZE, g_heap_size);*/

        if (2 == g_heap_size)                   /* first item added */
            g_oldest = time(NULL);
        else if (MAX_HEAP_SIZE < g_heap_size)   /* last item added */
        {
            time_t now = time(NULL);
            time_t elapsed = (now - g_oldest);
            g_voting_deadline = now + elapsed;
            /*printf("set g_voting_deadline to %d\n", (int)g_voting_deadline);*/
        }
    }
}


/* main */
/* ==== */

int main(int argc, char *argv[])
{   /* user interface */

    int i,j;
    assert(MAX_HEAP_SIZE < INT_MAX); /* sanity check */
        /* We can push g_heap_size up to one more than MAX_HEAP_SIZE, so this
           test ensures that we don't overflow. */

    
    if (argc != 4)
        usage();


    /* Load from disk
     * ==============
     * This creates Query objects and adds them to the heap.
     */

    load(argv[1]);


    /* Branch based on subcommand */
    /* ========================== */

    if (!strcmp("list", argv[3]))           /* list */
        return list();
    else if (!strcmp("future", argv[3]))    /* future */
        return future();
    else if (!strcmp("deadline", argv[3]))  /* deadline */
        return deadline();

    else if (!strcmp("clear", argv[3]))     /* clear */
        clear();
    else if (!strcmp("next", argv[3]))      /* next */
        next(argv[2]);
    else                                    /* query */
    {

        /* Validate input */
        /* ============== */

        char *query = argv[3];

        while (*query != '\0')
        {
            if (query - argv[3] == MAX_QUERY_LEN)  /* 40 chars */
                error("Sorry, we don't take more than 40 characters.");
            if (query)
            if (!(*query > 31 && *query < 127))    /* printable */
                error("Sorry, we only take ASCII input. :^(");
            query++;
        }
        query = argv[3];


        /* Add or upvote 
         * =============

         * This depends on whether it's already in the queue or not. We ignore
         * case differences.
         
         * We have an inefficient (O(n)) search strategy here, but we've only
         * got a few elements, and this is a heap exercise. If we wanted an
         * arbitrarily large queue I'd probably implement a second data
         * structure (hash, tree) for indexing queries into the heap. That 
         * would roughly double our storage requirements, but come on, then
         * we're building our own database, and that's not what this is about.
         * I mean, it *could* be about that, but I really want to get this 
         * working for Return.

         */

        j = g_heap_size;
        for (i=1; i<g_heap_size; i++)
            if (!strcasecmp(g_heap[i]->query, query))
                j = i;
        if (j < g_heap_size)    /* already scheduled */
            upvote(j);
        else                    /* new query */
            schedule(query);

    }


    /* Write to disk
     * =============
     * This destroys objects on the heap.
     */

    dump(argv[1]);


    return 0;

}
