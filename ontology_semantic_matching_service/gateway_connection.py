import logging
import os
import platform
import shutil
import subprocess
import time


class GatewayServerManager:
    def __init__(self):
        self.logger = setup_logging()
        self.gradle_failed = False
        # Initialise some paths
        self.base_directory = os.path.dirname(__file__)
        self.source_directory = os.path.join(
            self.base_directory,
            os.pardir,
            "Java/ontology-semantic-matching-service"
        )
        self.build_directory = os.path.join(
            self.source_directory,
            "build/libs"
        )
        self.destination_directory = os.path.join(
            self.base_directory,
            os.pardir,
            "Java/lib"
        )
        # Run the gateway server
        self.build_gateway_server()
        self.update_fallback_gateway_server()
        self.start_gateway_server()

    def run_command_in_directory(
            self,
            directory_path,
            command
    ) -> None:
        os.chdir(directory_path)
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        # Close subprocess, avoid resource warning
        try:
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                self.logger.info(
                    colorize(
                        line.strip(),
                        "grey"
                    )
                )
                fail_txt = "> Task :test FAILED"
                self.gradle_failed |= (fail_txt == line.strip())
        finally:
            process.stdout.close()
            process.stderr.close()
            process.wait()

    def build_gateway_server(self) -> None:
        self.logger.info("Build gateway server ...")
        # Use gradle to build hermit matching service and gateway server
        if platform.system() == "Windows":
            self.run_command_in_directory(
                self.source_directory,
                "gradlew clean build"
            )
        elif platform.system() == "Linux":
            self.run_command_in_directory(
                self.source_directory,
                "./gradlew clean build"
            )
        else:
            self.logger.warning("Current os not supported")
        self.logger.info("... done")

    def update_fallback_gateway_server(self) -> None:
        build_path_exists = os.path.exists(self.build_directory)
        if build_path_exists and not self.gradle_failed:
            self.logger.info("Updating fallback gateway server ...")
            shutil.copy(
                os.path.join(
                    self.build_directory,
                    "ontology-semantic-matching-service-all.jar"
                ),
                self.destination_directory
            )
            self.logger.info("... done")
        elif self.gradle_failed:
            self.logger.error("Gradle tests failed")
        else:
            self.logger.error("Build not stable, check gradlew permissions")

    def start_gateway_server(self):
        build_path_exists = os.path.exists(self.build_directory)
        if build_path_exists and not self.gradle_failed:
            self.logger.info("Starting gateway server ...")
            self.run_command_in_directory(
                self.build_directory,
                "java -jar ontology-semantic-matching-service-all.jar"
            )
        else:
            self.logger.warning("Starting fallback gateway server ...")
            self.run_command_in_directory(
                self.destination_directory,
                "java -jar ontology-semantic-matching-service-all.jar"
            )
        time.sleep(1)


class CustomFormatter(logging.Formatter):
    format = "%(levelname)s Gateway: %(message)s"
    formats = {
        logging.INFO: "\033[34m" + format + "\033[0m",
        logging.WARNING: "\033[1;93m" + format + "\033[0m",
        logging.ERROR: "\033[1;91m" + format + "\033[0m",
    }

    def format(self, record):
        formatter = logging.Formatter(
            self.formats.get(
                record.levelno
            )
        )
        return formatter.format(record)


def setup_logging():
    logger = logging.getLogger()
    # Reset logger
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    for filter in logger.filters[:]:
        logger.removeFilter(filter)
    # Setup logger
    logger.setLevel(logging.DEBUG)
    str_handler = logging.StreamHandler()
    str_handler.setLevel(logging.DEBUG)
    str_handler.setFormatter(CustomFormatter())
    logger.addHandler(str_handler)
    return logger


def colorize(text, color):
    colors = {
        "grey": "\033[37m",
        "reset": "\033[0m"
    }
    return f"{colors[color]}{text}{colors['reset']}"
