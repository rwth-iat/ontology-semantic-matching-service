import os
import unittest
import requests
import ontology_semantic_matching_service.run_service

from fastapi import FastAPI
from ontology_semantic_matching_service import queries
from ontology_semantic_matching_service.service import OwlSemanticMatchingService
from semantic_matching_interface import query
from uvicorn import Config


def compare_strings(expected, actual):
    expected_lines = expected.split('\n')
    actual_lines = actual.split('\n')

    if len(expected_lines) != len(actual_lines):
        # Different number of lines
        return False

    line_count_map = {}

    for line in expected_lines:
        line_count_map[line] = line_count_map.get(line, 0) + 1

    for line in actual_lines:
        if line not in line_count_map:
            # Line not present in expected
            return False
        line_count_map[line] -= 1

    return all(count == 0 for count in line_count_map.values())


class TestYourModule(unittest.TestCase):

    def test_semantic_matching_service_information(self):
        matching_service = OwlSemanticMatchingService()
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
                "OWL-ontology matching",
                response.json()["matching_method"]
            )
            self.assertEqual(
                "Hypertableau calculus based reasoning",
                response.json()["matching_algorithm"]
            )
            self.assertEqual(
                [],
                response.json()["required_parameters"]
            )
            self.assertEqual(
                [],
                response.json()["optional_parameters"]
            )

    def test_semantic_match_objects(self):
        resource_directory = os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            "test_resources"
        )
        matching_service = OwlSemanticMatchingService()
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
                "OWL-ontology matching",
                response.json()["matching_method"]
            )
            self.assertEqual(
                "Hypertableau calculus based reasoning",
                response.json()["matching_algorithm"]
            )
            self.assertEqual(
                0.8888888888888888,
                response.json()["matching_score"]
            )

    def test_semantic_match_all_objects(self):
        # Change threshold for reasoner
        java_config_directory = os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            "Java/ontology-semantic-matching-service/"
        )
        os.chdir(java_config_directory)
        backup_threshold = ""
        with open("config.properties", "r") as file:
            lines = file.readlines()
        for i, line in enumerate(lines):
            if line.startswith("filter.maximumScoreToRemove="):
                backup_threshold = lines[i]
                lines[i] = line.split("=")[0] + "=0.0\n"
        with open("config.properties", "w") as file:
            file.writelines(lines)

        resource_directory = os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            "test_resources"
        )
        matching_service = OwlSemanticMatchingService()
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
            # Avoid resource warning
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
            # Avoid resource warning
            with open("people_result.txt", "r") as file:
                match_all_objects_result = file.read()
            # Shutdown gateway server
            matching_service.java_gateway.shutdown()
            # Restore old threshold
            os.chdir(java_config_directory)
            for i, line in enumerate(lines):
                if line.startswith("filter.maximumScoreToRemove="):
                    lines[i] = backup_threshold
            with open("config.properties", "w") as file:
                file.writelines(lines)
            # Test
            assert compare_strings(match_all_objects_result, str(response.json()))
