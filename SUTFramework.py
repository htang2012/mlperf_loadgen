import os
import time
import logging
import argparse

import mlperf_loadgen as lg

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("MlperfBenchMark")


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", type=str, choices=[ "Offline", "Server"], default="Offline", help="Scenario")
    parser.add_argument("--output-log-dir", type=str, default="output-logs", help="Where logs are saved")
    parser.add_argument("--accuracy", action="store_true", help="Run accuracy mode")
    parser.add_argument("--mlperf-conf", type=str, default="mlperf.conf", help="mlperf rules config")
    parser.add_argument("--user-conf", type=str, default="user.conf", help="user config for user LoadGen settings such as target QPS")
    parser.add_argument("--audit-conf", type=str, default="audit.conf", help="audit config for LoadGen settings during compliance runs")
    args = parser.parse_args()
    return args

    
class Dataset:
    def __init__(self):
        print("dataset.__init__")
        pass
    def LoadSamplesToRam(self, query_samples):
        del query_samples
        print("dataset.LoadSamplesToRam")
        return 
     
    def UnloadSamplesFromRam(self, query_samples):
        del query_samples
        print("dataset.UnloadSamplesFromRam")
        return 
       
    def __del__(self):
        print("dataset.__del__")
        pass

class SUT:
    def __init__(self):
        print("__init__")
        self.dataset = Dataset()
        self.qsl = lg.ConstructQSL(100, 10, self.dataset.LoadSamplesToRam, self.dataset.UnloadSamplesFromRam) 
        pass
    def process_queries(self):
        print("SUT.process_queries")
        pass       
    def issue_queries(self, query_samples):
        print("SUT.issue_queries")
        responses = []
        for s in query_samples:
            responses.append(lg.QuerySampleResponse(s.id, 0, 0))
        lg.QuerySamplesComplete(responses)
        
        return 
      
    def flush_queries(self):
        print("SUT.flush_queeries")
        pass
        
    def start(self):
        print("SUT.start") 
        pass     
        
    def stop(self):
        print("SUT.stop")
        pass 
        
    def __del__(self):
        pass

scenario_map = {
    "offline": lg.TestScenario.Offline,
    "server": lg.TestScenario.Server,
}


        

def main():
    
    args = get_args()
    settings = lg.TestSettings()
    settings.scenario = scenario_map[args.scenario.lower()]
    settings.FromConfig(args.mlperf_conf, "llama2-70b", args.scenario)
    settings.FromConfig(args.user_conf, "llama2-70b", args.scenario)
    
    settings.mode = lg.TestMode.PerformanceOnly
     
    os.makedirs(args.output_log_dir, exist_ok=True)
    log_output_settings = lg.LogOutputSettings()
    log_output_settings.outdir = args.output_log_dir
    log_output_settings.copy_summary_to_stdout = True
    log_settings = lg.LogSettings()
    log_settings.log_output = log_output_settings
    log_settings.enable_trace = False 

    sut = SUT() 
      
    sut.start()
    logSUT = lg.ConstructSUT(sut.issue_queries, sut.flush_queries)
    log.info("Starting Benchmark run")
    lg.StartTestWithLogSettings(logSUT, sut.qsl, settings, log_settings, args.audit_conf)
    sut.stop()
    log.info("Run Completed!")
    log.info("Destroying SUT...") 
    lg.DestroySUT(logSUT)
    log.info("Destroying QSL...")
    lg.DestroyQSL(sut.qsl)
        
if __name__ == "__main__":
    main()
        
        
      