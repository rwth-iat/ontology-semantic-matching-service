import os
import shutil
import subprocess
import logging
import time


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    str_handler = logging.StreamHandler()
    str_handler.setLevel(logging.DEBUG)
    str_handler.setFormatter(CustomFormatter())

    logger.addHandler(str_handler)
    return logger


def colorize(text, color):
    colors = {
        "grey": "\033[37m",
        "reset": "\033[0m",
    }
    return f"{colors[color]}{text}{colors['reset']}"


class GatewayServerManager:
    def __init__(self):
        self.logger = setup_logging()
        self.gradle_tests_failed = False
        self.online = False

        self.base_directory = os.path.abspath(os.path.dirname(__file__))
        self.source_directory = os.path.join(self.base_directory, os.pardir, "Java\\ontology-semantic-matching-service")
        self.build_directory = os.path.join(self.source_directory, "build\\libs")
        self.destination_directory = os.path.join(self.base_directory, os.pardir, "Java\\lib")

        self.build_gateway_server()
        self.update_fallback_gateway_server()
        self.start_gateway_server()

    def is_online(self) -> bool:
        return self.online

    def run_command_in_directory(self, directory_path, command):
        os.chdir(directory_path)
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   universal_newlines=True)
        while True:
            line = process.stdout.readline()
            if not line:
                break
            self.logger.info(colorize(line.strip(), "grey"))
            self.gradle_tests_failed = self.gradle_tests_failed or "> Task :test FAILED" == line.strip()

    def build_gateway_server(self):
        self.logger.info("Build gateway server ...")
        self.run_command_in_directory(self.source_directory, "gradlew clean build")
        self.logger.info("... done")

    def update_fallback_gateway_server(self):
        if os.path.exists(self.build_directory) and not self.gradle_tests_failed:
            self.logger.info("Updating fallback gateway server ...")
            shutil.copy(
                os.path.join(self.build_directory, "ontology-semantic-matching-service-all.jar"),
                self.destination_directory
            )
            self.logger.info("... done")
        elif self.gradle_tests_failed:
            self.logger.error("Gradle tests failed")
        else:
            self.logger.error("Build not stable")

    def start_gateway_server(self):
        if os.path.exists(self.build_directory) and not self.gradle_tests_failed:
            self.logger.info("Starting gateway server ...")
            self.run_command_in_directory(self.build_directory,
                                          "java -jar ontology-semantic-matching-service-all.jar")
        else:
            self.logger.warning("Starting fallback gateway server ...")
            self.run_command_in_directory(self.destination_directory,
                                          "java -jar ontology-semantic-matching-service-all.jar")
        time.sleep(1)
        self.online = True


class CustomFormatter(logging.Formatter):
    format = "%(levelname)s - %(message)s"

    FORMATS = {
        logging.INFO: "\033[97m" + format + "\033[0m",
        logging.WARNING: "\033[1;93m" + format + "\033[0m",
        logging.ERROR: "\033[1;91m" + format + "\033[0m",
    }

    def format(self, record):
        formatter = logging.Formatter(self.FORMATS.get(record.levelno))
        return formatter.format(record)


if __name__ == "__main__":
    GatewayServerManager()
