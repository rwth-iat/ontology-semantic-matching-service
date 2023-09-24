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
    # First, we're going to load the ontology
    print("Loading the ontology")
    print("Execute http://localhost:8000/upload_ontology")
    upload_query = queries.UploadQuery(
        ontologies=[open("../test-resources/people.owl").read()]
    )
    requests.put(
        "http://localhost:8000/upload_ontology",
        data=upload_query.model_dump_json()
    )
    # Second, we're going to get the matching score for two individuals
    print("Get Matching score for two individuals")
    print("Execute http://localhost:8000/semantic_match_objects")
    match_objects_query = query.MatchObjectsQuery(
        semantic_id_1="http://www.semanticweb.org/mdebe/ontologies/example#Daisy_Buchanan",
        semantic_id_2="http://www.semanticweb.org/mdebe/ontologies/example#Beth_Doe"
    )
    response = requests.get(
        "http://localhost:8000/semantic_match_objects",
        data=match_objects_query.model_dump_json()
    )
    print(json.dumps(response.json(), indent=2))
    print("\n")
    # Third, we're going to get the matching score for all individuals
    print("Get Matching score for all individuals")
    print("Execute http://localhost:8000/semantic_match_all_objects")
    response = requests.get(
        "http://localhost:8000/semantic_match_all_objects",
    )
    print(str(response.json()))
