// SARK-based program
#include <sark.h>

// ------------------------------------------------------------------------
// constants
// ------------------------------------------------------------------------
#define TICK_PERIOD        10      // attempt to bounce dumped packets
#define PKT_QUEUE_SIZE     256     // dumped packet queue length

#define ROUTER_SLOT        SLOT_0  // router VIC slot -- not used currently!
#define CC_SLOT            SLOT_1  // comms. cont. VIC slot
#define TIMER_SLOT         SLOT_2  // timer VIC slot

#define RTR_BLOCKED_BIT    25
#define RTR_DOVRFLW_BIT    30
#define RTR_DENABLE_BIT    2

#define RTR_BLOCKED_MASK   (1 << RTR_BLOCKED_BIT)   // router blocked
#define RTR_DOVRFLW_MASK   (1 << RTR_DOVRFLW_BIT)   // router dump overflow
#define RTR_DENABLE_MASK   (1 << RTR_DENABLE_BIT)   // enable dump interrupts

#define PKT_CONTROL_SHFT   16
#define PKT_PLD_SHFT       17
#define PKT_TYPE_SHFT      22
#define PKT_ROUTE_SHFT     24

#define PKT_CONTROL_MASK   (0xff << PKT_CONTROL_SHFT)
#define PKT_PLD_MASK       (1 << PKT_PLD_SHFT)
#define PKT_TYPE_MASK      (3 << PKT_TYPE_SHFT)
#define PKT_ROUTE_MASK     (7 << PKT_ROUTE_SHFT)

#define PKT_TYPE_MC        (0 << PKT_TYPE_SHFT)
#define PKT_TYPE_PP        (1 << PKT_TYPE_SHFT)
#define PKT_TYPE_NN        (2 << PKT_TYPE_SHFT)
#define PKT_TYPE_FR        (3 << PKT_TYPE_SHFT)

#define TIMER2_CONF        0x82
#define TIMER2_LOAD        0
// ------------------------------------------------------------------------


// ------------------------------------------------------------------------
// types
// ------------------------------------------------------------------------
typedef struct  // dumped packet type
{
  uint hdr;
  uint key;
  uint pld;
} packet_t;


typedef struct  // packet queue type
{
  uint head;
  uint tail;
  packet_t queue[PKT_QUEUE_SIZE];
} pkt_queue_t;
// ------------------------------------------------------------------------


// ------------------------------------------------------------------------
// global variables
// ------------------------------------------------------------------------
uint coreID;

uint rtr_control;
uint cc_sar;

uint pkt_ctr0;
uint pkt_ctr1;
uint pkt_ctr2;
uint pkt_ctr3;

uint max_time;

pkt_queue_t pkt_queue;  // dumped packet queue
// ------------------------------------------------------------------------


// ------------------------------------------------------------------------
// functions
// ------------------------------------------------------------------------
INT_HANDLER timer_int_han (void)
{
  #ifdef DEBUG
    // count entries //##
    sark.vcpu->user2++;
  #endif

  // clear interrupt in timer,
  tc[T1_INT_CLR] = (uint) tc;

  // check if router not blocked
  if ((rtr[RTR_STATUS] & RTR_BLOCKED_MASK) == 0)
  {
    // access packet queue with fiq disabled,
    uint cpsr = cpu_fiq_disable ();

    // if queue not empty turn on packet bouncing,
    if (pkt_queue.tail != pkt_queue.head)
    {
      // restore fiq after queue access,
      cpu_int_restore (cpsr);

      // enable comms. cont. interrupt to bounce packets
      vic[VIC_ENABLE] = 1 << CC_TNF_INT;
    }
    else
    {
      // restore fiq after queue access,
      cpu_int_restore (cpsr);
    }
  }

  #ifdef DEBUG
    // update packet counters,
    //##  sark.vcpu->user0 = pkt_ctr0;
    sark.vcpu->user1 = pkt_ctr1;
    //##  sark.vcpu->user2 = pkt_ctr2;
    //##  sark.vcpu->user3 = pkt_ctr3;
  #endif

  // and tell VIC we're done
  vic[VIC_VADDR] = (uint) vic;
}


INT_HANDLER router_int_han (void)
{
  #ifdef DEBUG
    // count entries //##
    sark.vcpu->user0++;
  #endif

  #ifdef DEBUG
    // profiling
    uint start_time = tc[T2_COUNT];
  #endif

  // clear interrupt in router,
  (void) rtr[RTR_STATUS];

  // get packet from router,
  uint hdr = rtr[RTR_DHDR];
  uint pld = rtr[RTR_DDAT];
  uint key = rtr[RTR_DKEY];

  #ifdef DEBUG
    // profiling -- T2 is a down counter!
    uint run_time = start_time - tc[T2_COUNT];
  #endif

  #ifdef DEBUG
    // check for overflow -- non-recoverable error!,
    if (rtr[RTR_DSTAT] & RTR_DOVRFLW_MASK)
      pkt_ctr1++;
  #endif

  // bounce mc packets only
  if ((hdr & PKT_TYPE_MASK) == PKT_TYPE_MC)
  {
    // try to insert dumped packet in the queue,
    uint new_tail = (pkt_queue.tail + 1) % PKT_QUEUE_SIZE;

    // check for space in the queue
    if (new_tail != pkt_queue.head)
    {
      // queue packet,
      pkt_queue.queue[pkt_queue.tail].hdr = hdr;
      pkt_queue.queue[pkt_queue.tail].key = key;
      pkt_queue.queue[pkt_queue.tail].pld = pld;

      // update queue pointer,
      pkt_queue.tail = new_tail;

      #ifdef DEBUG
        // and count packet
        //# pkt_ctr0++;
      #endif

    }
    #ifdef DEBUG
      else
      {
        // full queue -- non-recoverable error!
        //# pkt_ctr2++;
      }
    #endif
  }

  #ifdef DEBUG
    // profiling -- keep track of maximum
    if (run_time > max_time)
      max_time = run_time;
  #endif
}


INT_HANDLER cc_int_han (void)
{
  //TODO: may need to deal with packet timestamp.

  // check if router not blocked
  if ((rtr[RTR_STATUS] & RTR_BLOCKED_MASK) == 0)
  {
    // access packet queue with fiq disabled,
    uint cpsr = cpu_fiq_disable ();

    // if queue not empty bounce packet,
    if (pkt_queue.tail != pkt_queue.head)
    {
      // dequeue packet,
      uint hdr = pkt_queue.queue[pkt_queue.head].hdr;
      uint pld = pkt_queue.queue[pkt_queue.head].pld;
      uint key = pkt_queue.queue[pkt_queue.head].key;

      // update queue pointer,
      pkt_queue.head = (pkt_queue.head + 1) % PKT_QUEUE_SIZE;

      // restore fiq after queue access,
      cpu_int_restore (cpsr);

      // write header and route,
      cc[CC_TCR] = hdr & PKT_CONTROL_MASK;
      cc[CC_SAR] = cc_sar | (hdr & PKT_ROUTE_MASK);

      // maybe write payload,
      if (hdr & PKT_PLD_MASK)
      {
        cc[CC_TXDATA] = pld;
      }

      // write key to fire packet,
      cc[CC_TXKEY] = key;

      #ifdef DEBUG
        // count entries //##
        sark.vcpu->user3++;

        // and count packet
        //# pkt_ctr3++;
      #endif
    }
    else
    {
      // restore fiq after queue access,
      cpu_int_restore (cpsr);

      // and disable comms. cont. interrupts
      vic[VIC_DISABLE] = 1 << CC_TNF_INT;
    }
  }
  else
  {
    // disable comms. cont. interrupts
    vic[VIC_DISABLE] = 1 << CC_TNF_INT;
  }

  // and tell VIC we're done
  vic[VIC_VADDR] = (uint) vic;
}


void timer_init (uint period)
{
  // set up count-down mode,
  tc[T1_CONTROL] = 0xe2;

  // load time in microsecs,
  tc[T1_LOAD] = sark.cpu_clk * period;

  // and configure VIC slot
  sark_vic_set (TIMER_SLOT, TIMER1_INT, 1, timer_int_han);
}


void router_init ()
{
  // re-configure wait values in router
  rtr[RTR_CONTROL] = (rtr[RTR_CONTROL] & 0x0000ffff) | 0x004f0000;

  // configure fiq vector,
  sark_vec->fiq_vec = router_int_han;

  // configure as fiq,
  vic[VIC_SELECT] = 1 << RTR_DUMP_INT;

  // enable interrupt,
  vic[VIC_ENABLE] = 1 << RTR_DUMP_INT;

  // clear router interrupts,
  (void) rtr[RTR_STATUS];

  // clear router dump status,
  (void) rtr[RTR_DSTAT];

  // and enable router interrupts when dumping packets
  rtr[RTR_CONTROL] |= (1 << RTR_DENABLE_BIT);
}


void cc_init ()
{
  // remember SAR register contents (p2p source ID)
  cc_sar = cc[CC_SAR] & 0x00ff;

  // configure VIC slot -- don't enable yet!
  sark_vic_set (CC_SLOT, CC_TNF_INT, 0, cc_int_han);
}


void timer2_init ()
{
  // configure timer 2 for profiling
  // enabled, 32 bit, free running, 1x pre-scaler
  tc[T2_CONTROL] = TIMER2_CONF;
  tc[T2_LOAD] = TIMER2_LOAD;
}
// ------------------------------------------------------------------------


// ------------------------------------------------------------------------
// main
// ------------------------------------------------------------------------
void c_main()
{
  io_printf (IO_STD, "starting dumped packet bouncer\n");

  timer_init (TICK_PERIOD);  // setup timer to maybe turn on bouncing

  cc_init ();                // setup comms. cont. interrupt when not full

  router_init ();            // setup router to interrupt when dumping

  #ifdef DEBUG
    timer2_init ();          // setup timer2 for profiling
  #endif

  cpu_sleep ();		     // Send core to sleep
}
// ------------------------------------------------------------------------
