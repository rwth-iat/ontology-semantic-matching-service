import os
import unittest
import requests
import ontology_semantic_matching_service.run_service

from fastapi import FastAPI
from ontology_semantic_matching_service import queries
from ontology_semantic_matching_service.service import OWLSemanticMatchingService
from semantic_matching_interface import query
from uvicorn import Config


class TestYourModule(unittest.TestCase):

    def test_semantic_matching_service_information(self):
        matching_service = OWLSemanticMatchingService()
        APP = FastAPI()
        APP.include_router(matching_service.router)
        config = Config(
            APP,
            host="127.0.0.1",
            port=8000,
            log_level="info"
        )
        server = ontology_semantic_matching_service.run_service.Server(config=config)

        with server.run_in_thread():
            response = requests.get(
                "http://localhost:8000/semantic_matching_service_information"
            )
            # Shutdown gateway server
            matching_service.java_gateway.shutdown()
            # Tests
            self.assertEqual(
                response.json()["matching_method"],
                "OWL-ontology matching"
            )
            self.assertEqual(
                response.json()["matching_algorithm"],
                "Hypertableau calculus based reasoning"
            )
            self.assertEqual(
                response.json()["required_parameters"],
                []
            )
            self.assertEqual(
                response.json()["optional_parameters"],
                []
            )

    def test_semantic_match_objects(self):
        resource_directory = os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            "test-resources"
        )
        matching_service = OWLSemanticMatchingService()
        APP = FastAPI()
        APP.include_router(matching_service.router)
        config = Config(
            APP,
            host="127.0.0.1",
            port=8000,
            log_level="info"
        )
        server = ontology_semantic_matching_service.run_service.Server(config=config)

        with server.run_in_thread():
            # Avoid resource warning
            os.chdir(resource_directory)
            with open("people.owl", "r") as file:
                ontology_contents = file.read()
            upload_query = queries.UploadQuery(ontologies=[ontology_contents])
            requests.put(
                "http://localhost:8000/upload_ontology",
                data=upload_query.model_dump_json()
            )
            match_objects_query = query.MatchObjectsQuery(
                semantic_id_1="http://www.semanticweb.org/mdebe/ontologies/example#Daisy_Buchanan",
                semantic_id_2="http://www.semanticweb.org/mdebe/ontologies/example#Beth_Doe"
            )
            response = requests.get(
                "http://localhost:8000/semantic_match_objects",
                data=match_objects_query.model_dump_json()
            )
            # Shutdown gateway server
            matching_service.java_gateway.shutdown()
            # Tests
            self.assertEqual(
                response.json()["matching_method"],
                "OWL-ontology matching"
            )
            self.assertEqual(
                response.json()["matching_algorithm"],
                "Hypertableau calculus based reasoning"
            )
            self.assertEqual(
                response.json()["matching_score"],
                0.8888888888888888
            )

    def test_semantic_match_all_objects(self):
        resource_directory = os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            "test-resources"
        )
        matching_service = OWLSemanticMatchingService()
        APP = FastAPI()
        APP.include_router(matching_service.router)
        config = Config(
            APP,
            host="127.0.0.1",
            port=8000,
            log_level="info"
        )
        server = ontology_semantic_matching_service.run_service.Server(config=config)

        with server.run_in_thread():
            os.chdir(resource_directory)
            # avoid resource warning
            with open("people.owl", "r") as file:
                ontology = file.read()
            upload_query = queries.UploadQuery(ontologies=[ontology])
            requests.put(
                "http://localhost:8000/upload_ontology",
                data=upload_query.model_dump_json()
            )
            response = requests.get(
                "http://localhost:8000/semantic_match_all_objects",
            )
            # avoid resource warning
            with open("people_result.txt", "r") as file:
                match_all_objects_result = file.read()
            # Shutdown gateway server
            matching_service.java_gateway.shutdown()
            # Test
            self.assertEqual(
                str(response.json()),
                match_all_objects_result
            )
