import mlperf_loadgen as lg
import requests
import logging
import os
from flask import Flask
from absl import flags, app

# Define flags
FLAGS = flags.FLAGS

# Define each argument as a flag
flags.DEFINE_enum("scenario", "Offline", ["Offline", "Server"], help="Scenario to run")
flags.DEFINE_string("output_log_dir", "output-logs", help="Directory where logs will be saved")
flags.DEFINE_bool("accuracy", False, help="Run accuracy mode")
flags.DEFINE_string("mlperf_conf", "mlperf.conf", help="MLPerf rules config file path")
flags.DEFINE_string("user_conf", "user.conf", help="User config for LoadGen settings")
flags.DEFINE_string("audit_conf", "audit.conf", help="Audit config for LoadGen settings during compliance runs")

log = logging.getLogger("MlperfLoadGen")

# Define Test Scenarios
scenario_map = {
    "offline": lg.TestScenario.Offline,
    "server": lg.TestScenario.Server
}

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
    def __init__(self, qdl, num_samples, num_sample_indices):
        log.info(f"QSL: Constructing with {num_samples} samples")
        self.qsl = lg.ConstructQSL(
            num_samples, num_sample_indices,
            qdl.load_samples_to_ram,
            qdl.unload_samples_from_ram
        )

    def __del__(self):
        log.info("QSL: Destroying QSL")
        lg.DestroyQSL(self.qsl)


# SUT (System Under Test)
class SUT:
    def __init__(self):
        log.info("SUT: Initializing system under test")

    def start(self):
        log.info("SUT: Starting the system")

    def stop(self):
        log.info("SUT: Stopping the system")

# SUT (WebServer System Under Test)
class WebServerSUT(SUT):
    def __init__(self, base_url, qsl):
        super().__init__()
        self.base_url = base_url
        self.qsl = qsl
        log.info(f"SUT: Initialized with base URL: {self.base_url}")

    def issue_queries(self, query_samples):
        log.info(f"SUT: Issuing queries {query_samples}")
        responses = []
        
        for s in query_samples:
            response = requests.get(f"{self.base_url}/api/data")  # Example: hitting the /api/data endpoint
            log.info(f"Received response with status {response.status_code} and data: {response.json()}")
            
            # Simulating a QuerySampleResponse with id, and dummy output sizes
            responses.append(lg.QuerySampleResponse(s.id, 0, 0))
        
        lg.QuerySamplesComplete(responses)

    def flush_queries(self):
        log.info("SUT: Flushing queries")

    def run_benchmark(self, args):
        log.info("SUT: Running benchmark")

        # Create the test settings
        settings = lg.TestSettings()
        settings.scenario = scenario_map[args['scenario']]
        settings.FromConfig(args['mlperf_conf'], "webserver-test", args['scenario'])
        settings.FromConfig(args['user_conf'], "webserver-test", args['scenario'])
        settings.mode = lg.TestMode.PerformanceOnly

        # Configure logging
        os.makedirs(args['output_log_dir'], exist_ok=True)
        log_output_settings = lg.LogOutputSettings()
        log_output_settings.outdir = args['output_log_dir']
        log_output_settings.copy_summary_to_stdout = True

        log_settings = lg.LogSettings()
        log_settings.log_output = log_output_settings
        log_settings.enable_trace = False

        # Start the test
        log.info("SUT: Constructing and running LoadGen test")
        sut_handle = lg.ConstructSUT(self.issue_queries, self.flush_queries)
        lg.StartTestWithLogSettings(sut_handle, self.qsl.qsl, settings, log_settings, args['audit_conf'])

        # Clean up
        lg.DestroySUT(sut_handle)
        log.info("SUT: Test completed and cleaned up")


def main(argv):
    del argv  # Unused argument
    
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger("MlperfLoadGen")

    # Extract values from FLAGS
    scenario = FLAGS.scenario
    output_log_dir = FLAGS.output_log_dir
    accuracy_mode = FLAGS.accuracy
    mlperf_conf = FLAGS.mlperf_conf
    user_conf = FLAGS.user_conf
    audit_conf = FLAGS.audit_conf

    # Example args (converting FLAGS into usable args dict)
    args = {
        'scenario': scenario.lower(),
        'mlperf_conf': mlperf_conf,
        'user_conf': user_conf,
        'audit_conf': audit_conf,
        'output_log_dir': output_log_dir
    }

    # Now run your MLPerf LoadGen test using these args
    qdl = QDL()
    qsl = QSL(qdl, 100, 10)
    sut = WebServerSUT("http://127.0.0.1:8000", qsl)

    sut.run_benchmark(args)

# Main execution
if __name__ == '__main__':
    app.run(main)
