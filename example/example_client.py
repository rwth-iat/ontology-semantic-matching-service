import json
import requests

from semantic_matching_interface import query
from ontology_semantic_matching_service import queries

if __name__ == '__main__':
    # Above all, we try to find out what the server we connect to can do.
    print("Finding out about the service")
    print("Get 'http://localhost:8000/semantic_matching_service_information'")
    response = requests.get(
        "http://localhost:8000/semantic_matching_service_information"
    )
    print(json.dumps(response.json(), indent=2))
    print("\n")
    # First, we're going to load the ontologies
    print("Loading the ontologies:")
    ontology_1 = "example-resources/pump_station.rdf"
    ontology_2 = "example-resources/control_system.rdf"
    print(ontology_1)
    print(ontology_2)
    print("Execute http://localhost:8000/upload_ontology")
    upload_query = queries.UploadQuery(
        ontologies=[open("../" + ontology_1).read(),
                    open("../" + ontology_2).read()]
    )
    requests.put(
        "http://localhost:8000/upload_ontology",
        data=upload_query.model_dump_json()
    )
    print("\n")
    # Second, we're going to get the matching score for two individuals
    print("Get Matching score for the individuals:")
    semantic_id_1 = "http://example.org/pump_station#Fuellstandssensor_5"
    semantic_id_2 = "http://example.org/control_system#Fuellstandssensor_1"
    print(semantic_id_1)
    print(semantic_id_2)
    print("Execute http://localhost:8000/semantic_match_objects")
    match_objects_query = query.MatchObjectsQuery(
        semantic_id_1=semantic_id_1,
        semantic_id_2=semantic_id_2
    )
    response = requests.get(
        "http://localhost:8000/semantic_match_objects",
        data=match_objects_query.model_dump_json()
    )
    print(json.dumps(response.json(), indent=2))
    print("\n")
    # Third, we're going to get the matching score for all individuals above a threshold
    # defined in Java/ontology-semantic-matching-service/config.properties
    print("Get Matching scores for all individuals above a defined threshold")
    print("Execute http://localhost:8000/semantic_match_all_objects")
    response = requests.get(
        "http://localhost:8000/semantic_match_all_objects",
    )
    print(str(response.json()))
