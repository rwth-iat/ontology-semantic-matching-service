import logging
import threading
import time

from py4j import java_gateway
from py4j.protocol import Py4JError
from semantic_matching_interface import interface, query, response
from ontology_semantic_matching_service import exceptions, queries
from ontology_semantic_matching_service.gateway_connection import GatewayServerManager


class OwlSemanticMatchingService(
    interface.AbstractSemanticMatchingInterface
):
    """
    The OWLSemanticMatchingService class provides a semantic matching service for ontology individuals.
    It allows users to calculate matching scores between individuals based on their classes, object
    properties and data properties within the ontology.

    Moreover, it implements the semantic matching interface, providing a range of standard functions
    for ontology semantic matching.

    This service is designed to work with ontologies processed by the HermiT OWL Reasoner. Therefore, it
    is connected with a matching service written in Java via a gateway server.
    """

    def __init__(self):
        super().__init__()
        # Disable the py4j gateway logger
        py4j_logger = logging.getLogger("py4j")
        py4j_logger.setLevel(logging.CRITICAL + 1)
        # Build gateway server for matching service
        gateway_thread = threading.Thread(target=connect_gateway)
        gateway_thread.start()
        # Connect to gateway server
        self.java_gateway = java_gateway.JavaGateway(
            gateway_parameters=java_gateway.GatewayParameters(
                port=55555
            )
        )
        # Wait until connection to gateway server
        while True:
            time.sleep(5)
            try:
                self.java_gateway.jvm.java.util.Random()
                break
            except Py4JError:
                time.sleep(5)
        # Add new commands to service
        self.router.add_api_route(
            "/upload_ontology",
            self.upload_ontology,
            methods=["PUT"]
        )
        self.router.add_api_route(
            "/semantic_match_all_objects",
            self.semantic_match_all_objects,
            methods=["GET"]
        )

    def upload_ontology(
            self,
            query: queries.UploadQuery
    ) -> None:
        try:
            # Convert query to java set
            ontology_set = self.java_gateway.jvm.java.util.HashSet()
            for index in query.ontologies:
                ontology_set.add(index)
            # Send it to gateway server
            self.java_gateway.uploadOntology(ontology_set)
        except Exception:
            raise exceptions.HTTPError503

    def semantic_matching_service_information(self) -> response.SemanticMatchingServiceInformation:
        try:
            return response.SemanticMatchingServiceInformation(
                matching_method="OWL-ontology matching",
                matching_algorithm="Hypertableau calculus based reasoning",
                required_parameters=[],
                optional_parameters=[]
            )
        except Exception:
            raise exceptions.HTTPError418

    def semantic_query_asset_administration_shell(
            self,
            query: query.AssetAdministrationShellQuery
    ) -> response.AssetAdministrationShellMatchingResponse:
        raise exceptions.HTTPError501

    def semantic_query_submodel_element(
            self,
            query: query.SubmodelElementQuery
    ) -> response.SubmodelElementMatchingResponse:
        raise exceptions.HTTPError501

    def semantic_match_objects(
            self,
            query: query.MatchObjectsQuery
    ) -> response.MatchObjectsMatchingResponse:
        try:
            score = self.java_gateway.semanticMatchObjects(
                query.semantic_id_1,
                query.semantic_id_2
            )
            return response.MatchObjectsMatchingResponse(
                matching_method="OWL-ontology matching",
                matching_algorithm="Hypertableau calculus based reasoning",
                matching_score=score
            )
        except Exception:
            raise exceptions.HTTPError503

    def semantic_match_all_objects(self) -> str:
        try:
            return self.java_gateway.semanticMatchAllObjects()
        except Exception:
            raise exceptions.HTTPError503


def connect_gateway() -> None:
    GatewayServerManager()
