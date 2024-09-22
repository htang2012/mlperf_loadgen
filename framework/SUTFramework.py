import os
import time
import logging
from absl import flags, app

FLAGS = flags.FLAGS
flags.DEFINE_enum('scenario', 'Offline', ['Offline', 'Server', 'SingleStream'], 'Scenario')
flags.DEFINE_string('output_log_dir', 'output-logs', 'Where logs are saved')
flags.DEFINE_bool('accuracy', False, 'Run accuracy mode')
flags.DEFINE_string('mlperf_conf', 'mlperf.conf', 'mlperf rules config')
flags.DEFINE_string('user_conf', 'user.conf', 'User config for LoadGen settings such as target QPS')
flags.DEFINE_string('audit_conf', 'audit.conf', 'Audit config for LoadGen settings during compliance runs')

import mlperf_loadgen as lg

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("MlperfBenchMark")


class QSL:
    def __init__(self):
        print("QSL.__init__")
        pass
    
    def LoadSamplesToRam(self, query_samples):
        del query_samples
        print("QSL.LoadSamplesToRam")
        return 
    
    def UnloadSamplesFromRam(self, query_samples):
        del query_samples
        print("QSL.UnloadSamplesFromRam")
        return 
    
    def __del__(self):
        print("QSL.__del__")
        pass


class QDL:
    def __init__(self, qsl):
        print("QDL.__init__")
        self.qsl = qsl
    
    def process_queries(self):
        print("QDL.process_queries")
        pass
    
    def issue_queries(self, query_samples):
        print("QDL.issue_queries")
        responses = []
        for s in query_samples:
            responses.append(lg.QuerySampleResponse(s.id, 0, 0))
        lg.QuerySamplesComplete(responses)
        return
    
    def flush_queries(self):
        print("QDL.flush_queries")
        pass
    
    def start(self):
        print("QDL.start")
        pass
    
    def stop(self):
        print("QDL.stop")
        pass
    
    def __del__(self):
        print("QDL.__del__")
        pass


class SUT:
    def __init__(self):
        print("SUT.__init__")
        self.qsl = QSL()
        self.qdl = QDL(self.qsl)
        self.qsl_handle = lg.ConstructQSL(100, 10, self.qsl.LoadSamplesToRam, self.qsl.UnloadSamplesFromRam)
    
    def process_queries(self):
        self.qdl.process_queries()
    
    def issue_queries(self, query_samples):
        self.qdl.issue_queries(query_samples)
    
    def flush_queries(self):
        self.qdl.flush_queries()
    
    def start(self):
        self.qdl.start()
    
    def stop(self):
        self.qdl.stop()
    
    def __del__(self):
        print("SUT.__del__")
        pass


scenario_map = {
    "offline": lg.TestScenario.Offline,
    "server": lg.TestScenario.Server,
    "singlestream": lg.TestScenario.SingleStream,
}


def main(argv):
    settings = lg.TestSettings()
    settings.scenario = scenario_map[FLAGS.scenario.lower()]
    settings.FromConfig(FLAGS.mlperf_conf, "llama2-70b", FLAGS.scenario)
    settings.FromConfig(FLAGS.user_conf, "llama2-70b", FLAGS.scenario)
    
    settings.mode = lg.TestMode.PerformanceOnly
     
    os.makedirs(FLAGS.output_log_dir, exist_ok=True)
    log_output_settings = lg.LogOutputSettings()
    log_output_settings.outdir = FLAGS.output_log_dir
    log_output_settings.copy_summary_to_stdout = True
    log_settings = lg.LogSettings()
    log_settings.log_output = log_output_settings
    log_settings.enable_trace = False 

    # Create the SUT (System Under Test) instance
    sut = SUT()
      
    sut.start()
    log_sut = lg.ConstructSUT(sut.issue_queries, sut.flush_queries)
    
    log.info("Starting Benchmark run")
    
    # Start the test with the log settings, the SUT, and the test settings
    lg.StartTestWithLogSettings(log_sut, sut.qsl_handle, settings, log_settings, FLAGS.audit_conf)
    
    sut.stop()

    log.info("Run Completed!")
    log.info("Destroying SUT...") 
    
    # Destroy the SUT after test completion
    lg.DestroySUT(log_sut)
    
    log.info("Destroying QSL...")
    
    # Destroy the QSL as well
    lg.DestroyQSL(sut.qsl_handle)
        
if __name__ == "__main__":
    app.run(main)

        
      