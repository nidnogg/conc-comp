#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

#define NTHREADS_READ 2
#define NTHREADS_WRITE 2
#define NTHREADS NTHREADS_READ + NTHREADS_WRITE

typedef struct {
    int tid;
    int count;
} t_args;

// A linked list (LL) node to store a queue entry 
struct QNode { 
    int key; 
    struct QNode* next; 
}; 
  
// The queue, front stores the front node of LL and rear stores the 
// last node of LL 
struct Queue { 
    struct QNode *front, *rear; 
}; 
  
// A utility function to create a new linked list node. 
struct QNode* newNode(int k) 
{ 
    struct QNode* temp = (struct QNode*)malloc(sizeof(struct QNode)); 
    temp->key = k; 
    temp->next = NULL; 
    return temp; 
} 
  
// A utility function to create an empty queue 
struct Queue* createQueue() 
{ 
    struct Queue* q = (struct Queue*)malloc(sizeof(struct Queue)); 
    q->front = q->rear = NULL; 
    return q; 
} 
  
// The function to add a key k to q 
void enQueue(struct Queue* q, int k) 
{ 
    // Create a new LL node 
    struct QNode* temp = newNode(k); 
  
    // If queue is empty, then new node is front and rear both 
    if (q->rear == NULL) { 
        q->front = q->rear = temp; 
        return; 
    } 
  
    // Add the new node at the end of queue and change rear 
    q->rear->next = temp; 
    q->rear = temp; 
} 
  
// Function to remove a key from given queue q 
struct QNode* deQueue(struct Queue* q) 
{ 
    // If queue is empty, return NULL. 
    if (q->front == NULL) 
        return NULL; 
  
    // Store previous front and move front one node ahead 
    struct QNode* temp = q->front; 
    free(temp); 
  
    q->front = q->front->next; 
  
    // If front becomes NULL, then change rear also as NULL 
    if (q->front == NULL) 
        q->rear = NULL; 
    return temp; 
} 

// Global variables 
int reading = 0, writing = 0, waitingToWrite = 0, waitingToRead = 0;
struct Queue* writerQueue; 
int threadCount = 0;

pthread_mutex_t mutex, writeQueueMutex;
pthread_cond_t cond_read, cond_write, cond_write_barrier;
t_args args;

int bobo (int id, int baba) {
    for(int i = id * 1000000; i > 0; i--) 
        baba = baba + i;
    return baba;
}



void startRead(int tid) {
    pthread_mutex_lock(&mutex);

    if(writing > 0 || waitingToWrite > waitingToRead) {
        waitingToRead++;
        //printf("Thread Leitora de ID %d irá se bloquear esperando writing > 0 (writing == %d) (waitingToRead = %d, waitingToWrite = %d)\n", tid, writing, waitingToRead, waitingToWrite);
        pthread_cond_wait(&cond_read, &mutex);
        waitingToRead--;
    }
   // printf("Thread Leitora de ID %d segue porque writing == %d\n", tid, writing);
    reading++;

    pthread_mutex_unlock(&mutex);
}

void endRead(int tid) {
    pthread_mutex_lock(&mutex);

    reading--;
    if(reading == 0) {
        printf("Thread Leitora de ID %d irá sinalizar cond_write (pois reading == %d)\n", tid, reading);
        pthread_cond_signal(&cond_write);
    }

    pthread_mutex_unlock(&mutex);
}

void startWrite(int tid) {
    pthread_mutex_lock(&mutex);


    if(reading > 0 || writing > 0 || waitingToRead > waitingToWrite) {
        waitingToWrite++;
        printf("Thread Escritora de ID %d irá esperar cond_write (pois reading (%d) > 0 ou writing (%d) > 0 (waitingToRead = %d, waitingToWrite = %d) )\n", tid, reading, writing, waitingToRead, waitingToWrite);
        pthread_cond_wait(&cond_write, &mutex);
        waitingToWrite--;
    }

    writing++;
    pthread_mutex_unlock(&mutex);

}

void endWrite(int tid) {
    pthread_mutex_lock(&mutex);

    writing--;
    
    printf("Thread Escritora de ID %d irá sinalizar cond_write e broacastear cond_read\n", tid);

    if(waitingToWrite) pthread_cond_signal(&cond_write);
    if(waitingToRead) pthread_cond_broadcast(&cond_read);

    pthread_mutex_unlock(&mutex);
}

void * reader (void *arg) {
    int tid = * (int *) arg;

    int readId;
    int readCount;

    while(1) {
        startRead(tid);
        
        readId = args.tid;
        readCount = args.count;
        printf("Thread Leitora de ID %d leu: id = %d e count = %d\n", tid, readId, readCount);
        
        endRead(tid);
        bobo(readId, readCount);
        //sleep(1);

    }
    pthread_exit(NULL);
}

void * writer (void *arg) {
    int tid = * (int *) arg;
    while(1) {
        startWrite(tid); //!! tranca outros escritores/leitores

        args.count++; // protegido em startWrite
        args.tid = tid;
        printf("Thread Escritora de ID %d modificou o struct para: id = %d e count = %d\n", tid, tid, args.count);

        endWrite(tid);
        bobo(tid, args.count*100);
        //sleep(1);
    }
    pthread_exit(NULL);
}
    

int main(int agrc, char* argv[]) { 
    pthread_t *tids;

    pthread_mutex_init(&mutex, NULL);
    pthread_mutex_init(&writeQueueMutex, NULL);

    pthread_cond_init(&cond_read, NULL);
    pthread_cond_init(&cond_write, NULL);
    pthread_cond_init(&cond_write_barrier, NULL);

    writerQueue = createQueue();

    int* tid;
    tids = malloc(sizeof(pthread_t) * (NTHREADS)); if(!tids) exit(-1);
    
    args.count = 0;

    for(int i = 0; i < NTHREADS_READ; i++) {
        tid = malloc(sizeof(int));  if(!tid) exit(-1);
        *tid = i;
        pthread_create(&tids[i], NULL, reader, (void * ) tid);
    }

    for(int i = 0; i < NTHREADS_WRITE; i++) {
        tid = malloc(sizeof(int));  if(!tid) exit(-1);
        *tid = i;
        pthread_create(&tids[i], NULL, writer, (void * ) tid);
    }

    free(tids);
    free(tid); // NAS THREADS
    pthread_exit(NULL);
    
}

