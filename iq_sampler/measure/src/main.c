//#include <zephyr.h>
//#include <init.h>
#include <nrf.h>
#include <nrfx.h>
#include "nrf_dm.h"
#include "nrfx_config.h"
#include "nrfx_clock.h"
#include "nrfx_uarte.h"
#include <stdint.h>
#include <stdbool.h>

#ifndef TXD_PIN
#define TXD_PIN 6
#endif

#ifndef RXD_PIN
#define RXD_PIN 8
#endif

#include "dm.c"
#include "uart.c"
#include "roles.c"

static nrf_dm_config_t dm_config;
static nrf_dm_report_t dm_report;

int main(void)
{
  dm_clock_init();
  debug_init();
  dm_init();

  int current_role = CMD_NONE; 
  current_role = read_uart_role();

  while(1){
    if (current_role == CMD_INITIATOR){
      current_role = run_initiator();
    } else if (current_role == CMD_REFLECTOR){
      current_role = run_reflector();
    } else if (current_role == CMD_NONE){
      current_role = run_none();
    }
  }
    return 0;
}

