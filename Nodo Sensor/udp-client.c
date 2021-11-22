/*
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. Neither the name of the Institute nor the names of its contributors
 *    may be used to endorse or promote products derived from this software
 *    without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE INSTITUTE AND CONTRIBUTORS ``AS IS'' AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL THE INSTITUTE OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 *
 * This file is part of the Contiki operating system.
 *
 */

#include "contiki.h"
#include "lib/random.h"
#include "sys/ctimer.h"
#include "net/ip/uip.h"
#include "net/ip/uiplib.h"
#include "net/ipv6/uip-ds6.h"
#include "net/ip/uip-udp-packet.h"
#include "sys/ctimer.h"
#ifdef WITH_COMPOWER
#include "powertrace.h"
#endif
#include <stdio.h>
#include <string.h>

#include "dev/serial-line.h"
#include "net/ipv6/uip-ds6-route.h"

//sensores
#include <math.h>
#include "platform/zoul/dev/dht22.h"
#include "sys/etimer.h"
#include "sys/rtimer.h"
#include "dev/leds.h"
#include "dev/adc-zoul.h"
#include "dev/adc-sensors.h"
#include <stdint.h>
#include <stdlib.h>
//

#include "list.h"

#define UDP_CLIENT_PORT 8765
#define UDP_SERVER_PORT 5678

#define UDP_EXAMPLE_ID  190

#define DEBUG DEBUG_FULL
#include "net/ip/uip-debug.h"

// #ifndef PERIOD
// #define PERIOD 30
// #endif

// #ifndef SENSE_PERIOD
// #define SENSE_PERIOD 10
// #endif

int SENSE_PERIOD = 120;

#define START_INTERVAL		(SENSE_PERIOD * CLOCK_SECOND)
#define SEND_INTERVAL		(PERIOD * CLOCK_SECOND)
#define SEND_TIME		(5 *CLOCK_SECOND)//(random_rand() % (SEND_INTERVAL))
#define SEND_TIME2		(0.5 *CLOCK_SECOND)
#define MAX_PAYLOAD_LEN		30

//sensores
#define ADC_PIN             5
#define LOOP_PERIOD         2
#define LOOP_INTERVAL       (CLOCK_SECOND * LOOP_PERIOD)
#define LEDS_PERIODIC       LEDS_GREEN
//

static struct uip_udp_conn *client_conn;
static uip_ipaddr_t server_ipaddr;

//sensores
static struct etimer et;
static uint16_t counter;
static int sensor_soil_hum;
int temperature, humidity;
int i = 0;
int max_sense_buf;
int PERIOD = 240;
int wait = 1;
int dd = 0;

static struct etimer periodic;
//int SEND_INTERVAL = (PERIOD * CLOCK_SECOND);
//
//estructura para la lista


MSG_T *l, msgs;
char buf1[MAX_PAYLOAD_LEN];

// //LISTAS


/*---------------------------------------------------------------------------*/
PROCESS(udp_client_process, "UDP client process");
//AUTOSTART_PROCESSES(&udp_client_process);
//sensores
PROCESS(acq_sensors, "Sensors acquisition");
AUTOSTART_PROCESSES(&acq_sensors, &udp_client_process);//, &acq_sensors);
//
/*---------------------------------------------------------------------------*/
static int seq_id;
static int reply;

static void
tcpip_handler(void)
{
  char *str;
  int len_str;
  int num_str;
  char *token;
  char *search = " ";
  if(uip_newdata()) {
    str = uip_appdata;
    str[uip_datalen()] = '\0';
    reply++;
    printf("DATA recv '%s' (s:%d, r:%d)\n", str, uip_datalen(), reply);
    //PERIOD = atoi(str);

    len_str= uip_datalen();
    printf("num 2 %d\n", len_str);
    if(len_str == 1){
      wait = atoi(str);
      bzero(buf1,MAX_PAYLOAD_LEN);
      dd = 0;
      printf(" VAL WAIIIIIIITTTTTT %d\n",wait );
    }

    if(len_str >= 8 && len_str <= 10){
      token = strtok(str, search);
      token = strtok(NULL, search);
      PERIOD = atoi(token);
      //printf(" VAL PERIODDDDDDDDDDDD%d\n",PERIOD );
    }

    if(len_str >= 12){
      token = strtok(str, search);
      token = strtok(NULL, search);
      num_str = atoi(token);
      SENSE_PERIOD = PERIOD / num_str;
      //printf(" VAL STARTTTTTTTT%d\n",SENSE_PERIOD );
    }
  }
}
/*---------------------------------------------------------------------------*/
static void
send_packet(void *ptr)
{

#ifdef SERVER_REPLY
  uint8_t num_used = 0;
  uip_ds6_nbr_t *nbr;

  nbr = nbr_table_head(ds6_neighbors);
  while(nbr != NULL) {
    nbr = nbr_table_next(ds6_neighbors, nbr);
    num_used++;
  }

  if(seq_id > 0) {
    ANNOTATE("#A r=%d/%d,color=%s,n=%d %d\n", reply, seq_id,
             reply == seq_id ? "GREEN" : "RED", uip_ds6_route_num_routes(), num_used);
  }
#endif /* SERVER_REPLY */
  uint8_t num_used = 0;
  uip_ds6_nbr_t *nbr;

  nbr = nbr_table_head(ds6_neighbors);
  while(nbr != NULL) {
    nbr = nbr_table_next(ds6_neighbors, nbr);
    PRINT6ADDR(nbr);
    num_used++;
    printf("Num used %d\n",num_used );
  }

  seq_id++;

  // PRINTF("DATA send %d 'Hello %d'\n",
  //        server_ipaddr.u8[sizeof(server_ipaddr.u8) - 1], seq_id);
 PRINTF("DATA send Soil Humidity %d Temperature %d Humidity %d\n",
        sensor_soil_hum, temperature, humidity);
  //Send sensors data
  //sprintf(buf1, "%d %d %d", temperature, sensor_soil_hum, humidity);
  printf("valor del buf %d\n",strlen(buf1) );
  uip_udp_packet_sendto(client_conn, buf1, strlen(buf1),
                        &server_ipaddr, UIP_HTONS(UDP_SERVER_PORT));
  printf("valor buf 0 %d\n", buf1[0]);
  printf("valor buf 1 %d\n", buf1[1]);
  printf("valor buf 2 %d\n", buf1[2]);
  //memset(buf1, 0, MAX_PAYLOAD_LEN); //Borrar el buffer
  //bzero(buf1,MAX_PAYLOAD_LEN); //Llenar el buffer con bytes de cero

  // sensor_soil_hum = 0;
  // uip_udp_packet_sendto(client_conn, buf2, strlen(buf2),
  //                       &server_ipaddr, UIP_HTONS(UDP_SERVER_PORT));
  // temperature = 0;
  // uip_udp_packet_sendto(client_conn, buf3, strlen(buf3),
  //                       &server_ipaddr, UIP_HTONS(UDP_SERVER_PORT));
  // humidity = 0;
}
/*---------------------------------------------------------------------------*/
static void
print_local_addresses(void)
{
  int i;
  uint8_t state;

  PRINTF("Client IPv6 addresses: ");
  for(i = 0; i < UIP_DS6_ADDR_NB; i++) {
    state = uip_ds6_if.addr_list[i].state;
    if(uip_ds6_if.addr_list[i].isused &&
       (state == ADDR_TENTATIVE || state == ADDR_PREFERRED)) {
      PRINT6ADDR(&uip_ds6_if.addr_list[i].ipaddr);
      PRINTF("\n");
      /* hack to make address "final" */
      if (state == ADDR_TENTATIVE) {
	uip_ds6_if.addr_list[i].state = ADDR_PREFERRED;
      }
    }
  }
}
/*---------------------------------------------------------------------------*/
static void
set_global_address(void)
{
  uip_ipaddr_t ipaddr;

  uip_ip6addr(&ipaddr, UIP_DS6_DEFAULT_PREFIX, 0, 0, 0, 0, 0, 0, 0);
  uip_ds6_set_addr_iid(&ipaddr, &uip_lladdr);
  uip_ds6_addr_add(&ipaddr, 0, ADDR_AUTOCONF);

/* The choice of server address determines its 6LoWPAN header compression.
 * (Our address will be compressed Mode 3 since it is derived from our
 * link-local address)
 * Obviously the choice made here must also be selected in udp-server.c.
 *
 * For correct Wireshark decoding using a sniffer, add the /64 prefix to the
 * 6LowPAN protocol preferences,
 * e.g. set Context 0 to fd00::. At present Wireshark copies Context/128 and
 * then overwrites it.
 * (Setting Context 0 to fd00::1111:2222:3333:4444 will report a 16 bit
 * compressed address of fd00::1111:22ff:fe33:xxxx)
 *
 * Note the IPCMV6 checksum verification depends on the correct uncompressed
 * addresses.
 */

#if 0
/* Mode 1 - 64 bits inline */
   uip_ip6addr(&server_ipaddr, UIP_DS6_DEFAULT_PREFIX, 0, 0, 0, 0, 0, 0, 1);
#elif 1
/* Mode 2 - 16 bits inline */
  //uip_ip6addr(&server_ipaddr, UIP_DS6_DEFAULT_PREFIX, 0, 0, 0, 0, 0x00ff, 0xfe00, 1);
  uip_ip6addr(&server_ipaddr,UIP_DS6_DEFAULT_PREFIX, 0, 0, 0, 0, 0, 0, 1);
#else
/* Mode 3 - derived from server link-local (MAC) address */
  uip_ip6addr(&server_ipaddr, UIP_DS6_DEFAULT_PREFIX, 0, 0, 0, 0x0250, 0xc2ff, 0xfea8, 0xcd1a); //redbee-econotag
#endif
}
/*---------------------------------------------------------------------------*/
PROCESS_THREAD(udp_client_process, ev, data)
{

  static struct ctimer backoff_timer;
#if WITH_COMPOWER
  static int print = 0;
#endif

  PROCESS_BEGIN();

  PROCESS_PAUSE();

  set_global_address();

  PRINTF("UDP client process started nbr:%d routes:%d\n",
         NBR_TABLE_CONF_MAX_NEIGHBORS, UIP_CONF_MAX_ROUTES);

  print_local_addresses();

  /* new connection with remote host */
  client_conn = udp_new(NULL, UIP_HTONS(UDP_SERVER_PORT), NULL);
  if(client_conn == NULL) {
    PRINTF("No UDP connection available, exiting the process!\n");
    PROCESS_EXIT();
  }
  udp_bind(client_conn, UIP_HTONS(UDP_CLIENT_PORT));

  PRINTF("Created a connection with the server ");
  PRINT6ADDR(&client_conn->ripaddr);
  PRINTF(" local/remote port %u/%u\n",
	UIP_HTONS(client_conn->lport), UIP_HTONS(client_conn->rport));

#if WITH_COMPOWER
  powertrace_sniff(POWERTRACE_ON);
#endif


  while(1) {

    //printf("antes de enviar period %d\n", PERIOD);
    etimer_set(&periodic, (PERIOD) * CLOCK_SECOND);

    PROCESS_YIELD();
    if(ev == tcpip_event) {
      tcpip_handler();
    }

    if(ev == serial_line_event_message && data != NULL) {
      char *str;
      str = data;
      if(str[0] == 'r') {
        uip_ds6_route_t *r;
        uip_ipaddr_t *nexthop;
        uip_ds6_defrt_t *defrt;
        uip_ipaddr_t *ipaddr;
        defrt = NULL;
        if((ipaddr = uip_ds6_defrt_choose()) != NULL) {
          defrt = uip_ds6_defrt_lookup(ipaddr);
        }
        if(defrt != NULL) {
          PRINTF("DefRT: :: -> %02d", defrt->ipaddr.u8[15]);
          PRINTF(" lt:%lu inf:%d\n", stimer_remaining(&defrt->lifetime),
                 defrt->isinfinite);
        } else {
          PRINTF("DefRT: :: -> NULL\n");
        }

        for(r = uip_ds6_route_head();
            r != NULL;
            r = uip_ds6_route_next(r)) {
          nexthop = uip_ds6_route_nexthop(r);
          PRINTF("Route: %02d -> %02d", r->ipaddr.u8[15], nexthop->u8[15]);
          /* PRINT6ADDR(&r->ipaddr); */
          /* PRINTF(" -> "); */
          /* PRINT6ADDR(nexthop); */
          PRINTF(" lt:%lu\n", r->state.lifetime);

        }
      }
    }

    if(etimer_expired(&periodic)) {
      uip_ds6_route_t *r;
      uip_ip6addr_t *nexthop, *ipaddr1;
      //uip_ipaddr_t *nex = "fe80::212:4b00:615:ab05";
      // char dir_son;
      // char buf[MAX_PAYLOAD_LEN];
      for(r = uip_ds6_route_head(); r != NULL; r = uip_ds6_route_next(r)) {
        printf("para routeeeees\n");
        nexthop = uip_ds6_route_nexthop(r);
        PRINT6ADDR(nexthop); //Imprime los nodos hijos
        //uip_ipaddr_t ipaddr1, ipaddr2;

        //dir_son = nexthop;
        //printf("NEXHOP %s\n", dir_son );
        PRINTF("Route: %02d -> %02d", r->ipaddr.u8[15], nexthop->u8[15]);
        /* PRINT6ADDR(&r->ipaddr); */
        /* PRINTF(" -> "); */
        /* PRINT6ADDR(nexthop); */
        PRINTF(" lt:%lu\n", r->state.lifetime);

      }
      wait = 0;
      etimer_reset(&periodic);
      ctimer_set(&backoff_timer, SEND_TIME, send_packet, NULL);

#if WITH_COMPOWER
      if (print == 0) {
	powertrace_print("#P");
      }
      if (++print == 3) {
	print = 0;
      }
#endif

    }
  }

  PROCESS_END();
}
/*---------------------------------------------------------------------------*/
PROCESS_THREAD(acq_sensors, ev, data)
{

  PROCESS_BEGIN();
  SENSORS_ACTIVATE(dht22);
  static struct ctimer backoff_timer;
  counter = 0;

  /* Configure the ADC ports */
  /* Use pin number not mask, for example if using the PA5 pin then use 5 */
  //adc_sensors.configure(ANALOG_AAC_SENSOR, ADC_PIN);
  adc_zoul.configure(SENSORS_HW_INIT, ZOUL_SENSORS_ADC_ALL);
  printf("AAC test application\n");

  /* Let it spin and read sensor data */

  while(1) {
    if(wait == 1){
      // bzero(buf1,MAX_PAYLOAD_LEN); //Llenar el buffer con bytes de cero
      // dd = 0;
      //etimer_set(&periodic, (PERIOD) * CLOCK_SECOND);
      wait = 2;
    }else if(wait == 0){
      ctimer_set(&backoff_timer, SEND_TIME2, send_packet, NULL);

    }

    etimer_set(&et, START_INTERVAL);

    /* The standard sensor API may be used to read sensors individually, using
     * the `dht22.value(DHT22_READ_TEMP)` and `dht22.value(DHT22_READ_HUM)`,
     * however a single read operation (5ms) returns both values, so by using
     * the function below we save one extra operation
     */

    PROCESS_YIELD();
    max_sense_buf = (PERIOD / SENSE_PERIOD) * 4;
    printf(" VAL PERIOD %d\n",PERIOD );
    //printf(" VAL SENDPERIOD %d\n",SEND_INTERVAL );
    printf(" VAL max_sense_buf %d\n",max_sense_buf );
    if(dht22_read_all(&temperature, &humidity) != DHT22_ERROR) {
      //sensor_soil_hum = (adc_sensors.value(ANALOG_AAC_SENSOR));
      sensor_soil_hum = adc_zoul.value(ZOUL_SENSORS_ADC3)/100;
      //printf("valor sensor suelo  %d\n", sensor_soil_hum);
      //printf("Temperatura Ambiente %02d.%02d ºC, ", temperature, temperature % 9);
      //printf("Humedad Ambiente %02d.%02d %%\n", humidity, humidity % 9);

      buf1[dd] = sensor_soil_hum;
      buf1[dd+1] = temperature;
      buf1[dd+2] = humidity;
      buf1[dd+3] = PERIOD + PERIOD/SENSE_PERIOD;
      dd = dd+4;

      if(dd == max_sense_buf){
        printf("valor dd> %d\n", dd);
        buf1[dd+1] = PERIOD;
        buf1[dd+2] = PERIOD/SENSE_PERIOD;

        dd = 0;
      }
      printf("valor tamano bufff %d\n",strlen(buf1) );
    } else {
      printf("Failed to read the sensor temperature\n");
    }
  }
  PROCESS_END();
}

