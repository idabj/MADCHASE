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


// Common functions, probably need to copy this file if you're on windows
#include "dm.c"
#include "uart.c"

//------------------------------------------------------------------
// Main loop
//------------------------------------------------------------------

static nrf_dm_config_t dm_config;
static nrf_dm_report_t dm_report;

int main(void)
{

  //- Functions in dm.c to init stuff
  dm_clock_init();
  debug_init();
  dm_init();

  dm_config = NRF_DM_DEFAULT_CONFIG;
  dm_config.role            = NRF_DM_ROLE_INITIATOR;
  dm_config.rng_seed = 40;

  while (1)
  {
    //Clear previous result
    dm_report.link_loss = 0;
    dm_report.rssi_local = 0;
    dm_report.rssi_remote = 0;
    dm_report.txpwr_local = 0;
    dm_report.txpwr_remote = 0;
    dm_report.quality = 100;
    dm_report.distance_estimates.mcpd.ifft = 0;
    dm_report.distance_estimates.mcpd.phase_slope = 0;
    dm_report.distance_estimates.mcpd.rssi_openspace = 0;
    dm_report.distance_estimates.mcpd.best = 0;
    for(int i=0;i<80;i++){
      dm_report.iq_tones->i_local[i] =0;
      dm_report.iq_tones->q_local[i] =0;
      dm_report.iq_tones->i_remote[i] =0;
      dm_report.iq_tones->q_remote[i] =0;
    }
    for(int i=0;i<80;i++){
      dm_report.tone_sinr_indicators.sinr_indicator_local[i] =0;
      dm_report.tone_sinr_indicators.sinr_indicator_remote[i] =0;
    }

    //- Wait for a character, any character
    uart_init();
    char c = 0;

    uart_get_char(&c);
    uart_uninit();

    //- Execute a ranging
    nrf_dm_status_t status = nrf_dm_configure(&dm_config);
    debug_start();
    uint32_t timeout_us = 0.5e6;
    status     = nrf_dm_proc_execute(timeout_us);
    debug_stop();

    float distance = 0;
    uint32_t duration = 0;
    uint8_t hopping_sequence[NRF_DM_CHANNEL_MAP_LEN];

    if(status == NRF_DM_STATUS_SUCCESS){
      nrf_dm_populate_report(&dm_report);
      nrf_dm_quality_t quality = nrf_dm_calc(&dm_report);
      duration = nrf_dm_get_duration_us(&dm_config);
      distance = nrf_dm_high_precision_calc(&dm_report);
      nrf_dm_get_hopping_sequence(&dm_config,hopping_sequence);

    }else{
      //- Set quality to 100 if it's a failure
      dm_report.quality = 100;
      debug_pulse(10);
    }

    //- Send report to UART
    uart_init();
    nrf_dm_report_to_json(&dm_report,distance,duration,hopping_sequence);
    uart_uninit();

  }
}
