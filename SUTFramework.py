import os
import time
import logging
import argparse
import mlperf_loadgen as lg
from absl import flags, app

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("MlperfBenchMark")

# Define flags
FLAGS = flags.FLAGS
flags.DEFINE_enum("scenario", "Offline", ["Offline", "Server"], help="Scenario")
flags.DEFINE_string("output_log_dir", "output-logs", help="Where logs are saved")
flags.DEFINE_bool("accuracy", False, help="Run accuracy mode")
flags.DEFINE_string("mlperf_conf", "mlperf.conf", help="mlperf rules config")
flags.DEFINE_string("user_conf", "user.conf", help="user config for user LoadGen settings such as target QPS")
flags.DEFINE_string("audit_conf", "audit.conf", help="audit config for LoadGen settings during compliance runs")


# QDL (Query Data Layer)
class QDL:
    def __init__(self):
        log.info("QDL: Initializing dataset")

    def load_samples_to_ram(self, query_samples):
        del query_samples
        log.info("QDL: Loading samples to RAM")
        return

    def unload_samples_from_ram(self, query_samples):
        del query_samples
        log.info("QDL: Unloading samples from RAM")
        return

    def __del__(self):
        log.info("QDL: Dataset cleanup")


# QSL (Query Service Layer)
class QSL:
    def __init__(self, qdl, num_samples=100, num_sample_indices=10):
        log.info("QSL: Constructing QSL with %d samples and %d sample indices", num_samples, num_sample_indices)
        self.qdl = qdl
        self.qsl = lg.ConstructQSL(num_samples, num_sample_indices, self.qdl.load_samples_to_ram, self.qdl.unload_samples_from_ram)

    def issue_queries(self, query_samples):
        log.info("QSL: Issuing queries")
        responses = []
        for s in query_samples:
            responses.append(lg.QuerySampleResponse(s.id, 0, 0))
        lg.QuerySamplesComplete(responses)
        return

    def flush_queries(self):
        log.info("QSL: Flushing queries")

    def __del__(self):
        log.info("QSL: Destroying QSL")
        lg.DestroyQSL(self.qsl)


# SUT (System Under Test)
class SUT:
    def __init__(self, qsl):
        log.info("SUT: Initializing system under test")
        self.qsl = qsl

    def start(self):
        log.info("SUT: Starting the system")

    def stop(self):
        log.info("SUT: Stopping the system")
        
    def run_benchmark(self):

        log.info("SUT: Running benchmark")

        # Setup test settings
        settings = lg.TestSettings()
        settings.scenario = scenario_map[FLAGS.scenario.lower()]
        settings.FromConfig(FLAGS.mlperf_conf, "llama2-70b", FLAGS.scenario)
        settings.FromConfig(FLAGS.user_conf, "llama2-70b", FLAGS.scenario)
        settings.mode = lg.TestMode.PerformanceOnly

        # Setup logging
        os.makedirs(FLAGS.output_log_dir, exist_ok=True)
        log_output_settings = lg.LogOutputSettings()
        log_output_settings.outdir = FLAGS.output_log_dir
        log_output_settings.copy_summary_to_stdout = True
        log_settings = lg.LogSettings()
        log_settings.log_output = log_output_settings
        log_settings.enable_trace = False

        # Start test
        log.info("SUT: Constructing SUT")
        sut_handle = lg.ConstructSUT(self.qsl.issue_queries, self.qsl.flush_queries)
        log.info("SUT: Starting benchmark run")
        lg.StartTestWithLogSettings(sut_handle, self.qsl.qsl, settings, log_settings, FLAGS.audit_conf)
        log.info("SUT: Benchmark run completed")

        # Clean up
        lg.DestroySUT(sut_handle)
        log.info("SUT: Destroyed SUT")

scenario_map = {
    "offline": lg.TestScenario.Offline,
    "server": lg.TestScenario.Server,
}


def main(argv):
    del argv
    # Initialize components
    qdl = QDL()
    qsl = QSL(qdl)
    sut = SUT(qsl)

    # Start and run the benchmark
    sut.start()
    sut.run_benchmark()
    sut.stop()

    log.info("Run Completed!")


if __name__ == "__main__":
    app.run(main)

        
      