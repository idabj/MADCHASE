//------------------------------------------------------------------
// Setup UARTE to PC
//------------------------------------------------------------------
static nrfx_uarte_t instance = NRFX_UARTE_INSTANCE(0);

void uart_init(void){
    nrfx_uarte_config_t config = NRFX_UARTE_DEFAULT_CONFIG(TXD_PIN, RXD_PIN);
    config.baudrate            = NRF_UARTE_BAUDRATE_115200;
    nrfx_uarte_init(&instance, &config, NULL);
}

void uart_uninit(void){
    nrfx_uarte_uninit(&instance);
}

void uart_put_string(const char * string)
{
  while (*string != '\0')
  {
    uart_put_char(*string++);
  }
}

int uart_cbprint(int ch, void * ctx){
  nrfx_uarte_tx(&instance, &ch, 1, 0);
}

void uart_put_char(uint8_t ch)
{
  nrfx_uarte_tx(&instance, &ch, 1, 0);
}

bool uart_chars_available(void)
{
  return nrfx_uarte_rx_ready(&instance, NULL);
}

void uart_get_char(uint8_t * p_ch)
{
  nrfx_uarte_errorsrc_get(&instance);
  nrfx_uarte_rx(&instance, p_ch, 1);
}

void dist_to_json(char *str, float f){

  int d = ((int)1000*f);
  cbprintf(&uart_cbprint, 0, "\"%s\" : %d",str, d);
}

void int_to_json(char *str, int d){
  cbprintf(&uart_cbprint, 0, "\"%s\" : %d",str, d);
}

void tones_to_json(char * str, float *array,uint32_t length){

  uart_put_string("\"");
  uart_put_string(str);
  uart_put_string("\":[");
  for (uint32_t i = 0; i < length; i++)
  {
    //- Assume 10-bit ADC, and scale resolution to 15-bit, should be more than enough precision
    int f = ((int)32*array[i]);
    cbprintf(&uart_cbprint, 0, "%d", f);

    if ((i + 1) < length)
    {
      uart_put_string(",");
    }
  }
  uart_put_string("]");
}

void uint8array_to_json(char * str, uint8_t *array,uint32_t length){

  uart_put_string("\"");
  uart_put_string(str);
  uart_put_string("\":[");
  for (uint32_t i = 0; i < length; i++)
  {

    cbprintf(&uart_cbprint, 0, "%u", array[i]);

    if ((i + 1) < length)
    {
      uart_put_string(",");
    }
  }
  uart_put_string("]");
}

void sinr_to_json(char * str, nrf_dm_sinr_indicator_t *array,uint32_t length){

  uart_put_string("\"");
  uart_put_string(str);
  uart_put_string("\":[");
  for (uint32_t i = 0; i < length; i++)
  {

    cbprintf(&uart_cbprint, 0, "%d", ((int)array[i]));

    if ((i + 1) < length)
    {
      uart_put_string(",");
    }
  }
  uart_put_string("]");
}

void nrf_dm_report_to_json(nrf_dm_report_t *dm_report,float distance,int32_t duration, uint8_t *hopping_sequence){
  uart_put_string("{");

  //- Print tones

  tones_to_json("i_local",&dm_report->iq_tones->i_local[0],80); uart_put_string(",");
  tones_to_json("q_local",&dm_report->iq_tones->q_local[0],80); uart_put_string(",");
  tones_to_json("i_remote",&dm_report->iq_tones->i_remote[0],80); uart_put_string(",");
  tones_to_json("q_remote",&dm_report->iq_tones->q_remote[0],80); uart_put_string(",");
  uint8array_to_json("hopping_sequence",hopping_sequence,NRF_DM_CHANNEL_MAP_LEN); uart_put_string(",");


  //- Print tone_sinr
  sinr_to_json("sinr_local",&dm_report->tone_sinr_indicators.sinr_indicator_local[0],80); uart_put_string(",");
  sinr_to_json("sinr_remote",&dm_report->tone_sinr_indicators.sinr_indicator_remote[0],80); uart_put_string(",");

  //- Print ranging mode
  //- Print distance
  dist_to_json("ifft[mm]",dm_report->distance_estimates.mcpd.ifft);uart_put_char(',');
  dist_to_json("phase_slope[mm]",dm_report->distance_estimates.mcpd.phase_slope);uart_put_char(',');
  dist_to_json("rssi_openspace[mm]",dm_report->distance_estimates.mcpd.rssi_openspace);uart_put_char(',');
  dist_to_json("best[mm]",dm_report->distance_estimates.mcpd.best);uart_put_char(',');
  dist_to_json("highprec[mm]",distance);uart_put_char(',');

  //- Status params
  int_to_json("link_loss[dB]",dm_report->link_loss); uart_put_char(',');
  int_to_json("duration[us]",duration); uart_put_char(',');
  int_to_json("rssi_local[dB]",dm_report->rssi_local); uart_put_char(',');
  int_to_json("rssi_remote[dB]",dm_report->rssi_remote); uart_put_char(',');
  int_to_json("txpwr_local[dB]",dm_report->txpwr_local); uart_put_char(',');
  int_to_json("txpwr_remote[dB]",dm_report->txpwr_remote); uart_put_char(',');
  int_to_json("quality",dm_report->quality);
  uart_put_string("}\n\r");
}