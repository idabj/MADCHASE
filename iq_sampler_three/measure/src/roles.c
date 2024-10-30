enum Role {
    CMD_INITIATOR,
    CMD_REFLECTOR,
    CMD_NONE,
    CMD_UNKNOWN = -1
};

int read_uart_role(void){
    uart_init();
    char role_char;

    if (uart_chars_available()){
        uart_get_char((uint8_t*)&role_char);
        uart_uninit();

        if (role_char == 'i') {
            return CMD_INITIATOR;
        } else if (role_char == 'r') {
            return CMD_REFLECTOR;
        } else if (role_char == 'n') {
            return CMD_NONE;
        } else {
            return CMD_UNKNOWN;
        }
    }
    uart_uninit();
    return CMD_UNKNOWN;  // No new input
}

int run_initiator(void){

    static nrf_dm_config_t dm_config;
    static nrf_dm_report_t dm_report;

    dm_config = NRF_DM_DEFAULT_CONFIG;
    dm_config.role = NRF_DM_ROLE_INITIATOR;
    dm_config.rng_seed = 40;

    while(1){
        // Clear previous result
        dm_report.link_loss = 0;
        dm_report.rssi_local = 0;
        dm_report.rssi_remote = 0;
        dm_report.txpwr_local = 0;
        dm_report.txpwr_remote = 0;
        dm_report.quality = 90;
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

        // Execute measurement
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

        } else{  // Failure
       
        dm_report.quality = 100;
        debug_pulse(10);
        }

        //Send report to UART
        uart_init();
        nrf_dm_report_to_json(&dm_report,distance,duration,hopping_sequence);
        uart_uninit();


        // Check for role change after each execution
        int new_role = read_uart_role();
        if (new_role != CMD_UNKNOWN) {
            return new_role; 
        }
    }
}


int run_reflector(void){
    static nrf_dm_config_t dm_config;

    dm_config = NRF_DM_DEFAULT_CONFIG;
    dm_config.role = NRF_DM_ROLE_REFLECTOR;
    dm_config.rng_seed = 40;


    while(1){
        nrf_dm_status_t status = nrf_dm_configure(&dm_config);
        debug_start();
        uint32_t timeout_us = 3e6;
        status = nrf_dm_proc_execute(timeout_us);
        debug_stop();

        if (status == NRF_DM_STATUS_SUCCESS){
            debug_pulse(10);
        } else {
            debug_pulse(5);
        }

        // Check for role change after each execution
        int new_role = read_uart_role();
        if (new_role != CMD_UNKNOWN) {
            return new_role; 
        }
    }
}

int run_none(void){
    static nrf_dm_config_t dm_config;

    dm_config = NRF_DM_DEFAULT_CONFIG;
    dm_config.role = NRF_DM_ROLE_REFLECTOR;
    dm_config.rng_seed = 40;

    nrf_dm_status_t status = nrf_dm_configure(&dm_config);
    while(1){
        // Check for role change after each execution
        int new_role = read_uart_role();
        if (new_role != CMD_UNKNOWN) {
            return new_role; 
        }
    }

}