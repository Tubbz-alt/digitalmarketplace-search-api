import pytest
import pathlib
import json

import app.mapping

from .helpers import make_service, services_mappings


mappings_dir = (pathlib.Path(__file__).parent / "../mappings").resolve()


@pytest.fixture(scope="module", params=services_mappings)
def services_mapping_file_name_and_path(request):
    return (request.param, mappings_dir / f"{request.param}.json")


@pytest.fixture()
def services_mapping(services_mapping_file_name_and_path):
    """Fixture that provides an Elastic Search mapping, for unit testing functions that expect to be passed one."""
    services_mapping_dict = json.loads(services_mapping_file_name_and_path[1].read_text())
    return app.mapping.Mapping(services_mapping_dict, "services")


@pytest.fixture()
def service():
    """
    A fixture for a service such as might be indexed in the Search API.
    :return: dict
    """
    return make_service()
