import contextlib
import os
import threading
import time
import uvicorn

from fastapi import FastAPI
from ontology_semantic_matching_service.service import OwlSemanticMatchingService
from uvicorn import Config


class Server(uvicorn.Server):
    def install_signal_handlers(self):
        pass

    @contextlib.contextmanager
    def run_in_thread(self):
        thread = threading.Thread(target=self.run)
        thread.start()
        try:
            while not self.started:
                time.sleep(0.1)
            yield
        finally:
            self.should_exit = True
            thread.join()


def run_matching_service(
        host: str,
        port: int
) -> None:
    original_directory = os.getcwd()
    # Run the matching server
    matching_service = OwlSemanticMatchingService()
    APP = FastAPI()
    APP.include_router(matching_service.router)
    config = Config(
        APP,
        host=host,
        port=port,
        log_level="info"
    )
    server = Server(config=config)
    # Keyboard interrupt for graceful shutdown
    with server.run_in_thread():
        try:
            while True:
                pass
        except KeyboardInterrupt:
            # Reset path to not influence next execution
            os.chdir(original_directory)
            matching_service.java_gateway.shutdown()
