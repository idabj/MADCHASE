/*********************************************************************
 *        Copyright (c) 2022 Carsten Wulff Software, Norway
 * *******************************************************************
 * Created       : wulff at 2022-5-28
 * *******************************************************************
 *  The MIT License (MIT)
 *
 *  Permission is hereby granted, free of charge, to any person obtaining a copy
 *  of this software and associated documentation files (the "Software"), to deal
 *  in the Software without restriction, including without limitation the rights
 *  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 *  copies of the Software, and to permit persons to whom the Software is
 *  furnished to do so, subject to the following conditions:
 *
 *  The above copyright notice and this permission notice shall be included in all
 *  copies or substantial portions of the Software.
 *
 *  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 *  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 *  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 *  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 *  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 *  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 *  SOFTWARE.
 *
 ********************************************************************/


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

