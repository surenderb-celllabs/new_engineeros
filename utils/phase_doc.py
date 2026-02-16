
from utils.colored_logger import ColoredLogger
from utils import file_management

from typing import Literal
import logging
from pathlib import Path

BASE_PATH = str(Path(__file__).parents[1]) + "/_docs/"

util_logger = ColoredLogger(name="Phase Documents", level=logging.DEBUG)

PHASE2_DOCUMENTS = Literal[
    "selected_concept", "target_audience", "technical_team", "market_research",
    "customer_persona", "value_proposition", "go_nogo_decision", "tech_fisibility",
    "detailed_selected_concept"
]
PHASE3_DOCUMENTS = Literal[
    "customer_need_validation", "competitive_analysis"
]
PHASE4_DOCUMENTS = Literal[
""
]
PHASE5_DOCUMENTS = Literal[
    "customer_needs", "tech_constrains", "stakeholder_req", "prd",
    "feature_prio", "tech_specifications", "success_metrix",
    "use_case", "functional_requirements", "non_functional_requirements"
]
PHASE6_DOCUMENTS = Literal[
    "product_requirements", "wireframes", "mockups", "prototypes",
    "design_specifications", "user_flows"
]
PHASE7_DOCUMENTS = Literal[
    ""
]
PHASE8_DOCUMENTS = Literal[
    "team_capacity", "tech_decision", "dev_roadmap", "sprint_plan",
    "milestone_definitions", "resource_allocation", "epic_generated", "user_stories", "just_user_stories",
    "tickets_list", "developer_tasks"
]

def phase2_document(mode: Literal["load", "save"], document: PHASE2_DOCUMENTS, data: None|dict = None):
    util_logger.debug("{} file: {} {}...".\
                      format("loading from" if mode == "load" else "saving to",
                             document, BASE_PATH))

    filename = ""
    key = ""



    if document == "selected_concept":
        filename = BASE_PATH + "_2_concept_validation/000_shortlisted_concept.yaml"
        key = "shortlisted_concepts"

    elif document == "detailed_selected_concept":
        filename = BASE_PATH + "_2_concept_validation/001_detailed_selected_concept.yaml"
        key = "detailed_selected_concept"

    elif document == "target_audience":
        filename = BASE_PATH + "_2_concept_validation/004_target_audience.yaml"
        key = "target_audience_profiles"

    elif document == "technical_team":
        filename = BASE_PATH + "_2_concept_validation/002_technical_team.yaml"
        key = "team_members"

    elif document == "market_research":
        filename = BASE_PATH + "_2_concept_validation/003_market_research.yaml"
        key = "preliminary_market_research"

    elif document == "customer_persona":
        filename = BASE_PATH + "_2_concept_validation/005_customer_persona.yaml"
        key = "customer_personas"

    elif document == "value_proposition":
        filename = BASE_PATH + "_2_concept_validation/value_proposition.yaml"
        key = "value_propositions"

    elif document == "go_nogo_decision":
        filename = BASE_PATH + "_2_concept_validation/go_nogo_decision.yaml"
        key = "go_no_go_decision"

    elif document == "tech_fisibility":
        filename = BASE_PATH + "_2_concept_validation/tech_fisibility.yaml"
        key = "technical_feasibility"


    if mode == "save":
        # util_logger.debug("Saving: {}".format(data))
        return file_management.save_yaml(file_name=filename, data=data)

    elif mode == "load":
        return file_management.load_yaml(file_name=filename)[key]

    return None


def phase3_document(mode: Literal["load", "save"], document: PHASE3_DOCUMENTS, data: None|dict = None):
    util_logger.debug("{} file: {} ...".\
                      format("loading" if mode == "load" else "saving",
                             document))
    filename = ""
    key = ""


    if document == "customer_need_validation":
        filename = BASE_PATH + "_3_market_research_analysis/customer_need_validation.yaml"
        key = "customer_needs_documentation"

    if document == "competitive_analysis":
        filename = BASE_PATH + "_3_market_research_analysis/competitive_analysis.yaml"
        key = "competitive_analysis"


    if mode == "save":
        util_logger.debug("Saving: {}".format(data))
        return file_management.save_yaml(file_name=filename, data=data)

    elif mode == "load":
        return file_management.load_yaml(file_name=filename)[key]

    return None


def phase4_document(mode: Literal["load", "save"], document: PHASE4_DOCUMENTS, data: None|dict = None):
    util_logger.debug("{} file: {} ...".\
                      format("loading" if mode == "load" else "saving",
                             document))
    filename = ""
    key = ""



    if mode == "save":
        util_logger.debug("Saving: {}".format(data))
        return file_management.save_yaml(file_name=filename, data=data)

    elif mode == "load":
        return file_management.load_yaml(file_name=filename)[key]

    return None


def phase5_document(mode: Literal["load", "save"], document: PHASE5_DOCUMENTS, data: None|dict = None):
    util_logger.debug("{} file: {} ...".\
                      format("loading" if mode == "load" else "saving",
                             document))
    filename = ""
    key = ""


    if document == "customer_needs":
        filename = BASE_PATH + "_5_product_requirements_definition/001_customer_needs.yaml"
        key = "customer_needs"

    elif document == "tech_constrains":
        filename = BASE_PATH + "_5_product_requirements_definition/technical_constraints.yaml"
        key = "technical_constraints"

    elif document == "stakeholder_req":
        filename = BASE_PATH + "_5_product_requirements_definition/stakeholder_requirements.yaml"
        key = "stakeholder_requirements"

    elif document == "prd":
        filename = BASE_PATH + "_5_product_requirements_definition/product_requirements_document.yaml"
        key = "product_requirements_document"

    elif document == "feature_prio":
        filename = BASE_PATH + "_5_product_requirements_definition/005_feature_prioritization.yaml"
        key = "feature_prioritization"

    elif document == "tech_specifications":
        filename = BASE_PATH + "_5_product_requirements_definition/technical_specifications.yaml"
        key = "technical_specifications"

    elif document == "success_metrix":
        filename = BASE_PATH + "_5_product_requirements_definition/success_metrics.yaml"
        key = "success_metrics"

    elif document == "use_case":
        filename = BASE_PATH + "_5_product_requirements_definition/002_use_case.yaml"
        key = "use_case"

    elif document == "functional_requirements":
        filename = BASE_PATH + "_5_product_requirements_definition/003_functional_requirements.yaml"
        key = "functional_requirements"

    elif document == "non_functional_requirements":
        filename = BASE_PATH + "_5_product_requirements_definition/004_non_functional_requirements.yaml"
        key = "non_functional_requirements"


    if mode == "save":
        util_logger.debug("Saving: {}".format(data))
        return file_management.save_yaml(file_name=filename, data=data)

    elif mode == "load":
        return file_management.load_yaml(file_name=filename)[key]

    return None


def phase6_document(mode: Literal["load", "save"], document: PHASE6_DOCUMENTS, data: None|dict = None):
    util_logger.debug("{} file: {} ...".\
                      format("loading" if mode == "load" else "saving",
                             document))
    filename = ""
    key = ""


    if document == "product_requirements":
        filename = BASE_PATH + "_6_design_prototyping/000_product_requirements.yaml"
        key = "product_requirements"

    if document == "wireframes":
        filename = BASE_PATH + "_6_design_prototyping/001_wireframes.yaml"
        key = "wireframes"

    if document == "mockups":
        filename = BASE_PATH + "_6_design_prototyping/mockups.yaml"
        key = "mockups"

    if document == "prototypes":
        filename = BASE_PATH + "_6_design_prototyping/prototypes.yaml"
        key = "prototypes"

    if document == "design_specifications":
        filename = BASE_PATH + "_6_design_prototyping/design_specifications.yaml"
        key = "design_specifications"

    if document == "user_flows":
        filename = BASE_PATH + "_6_design_prototyping/002_user_flows.yaml"
        key = "user_flows"



    if mode == "save":
        util_logger.debug("Saving: {}".format(data))
        return file_management.save_yaml(file_name=filename, data=data)

    elif mode == "load":
        return file_management.load_yaml(file_name=filename)[key]

    return None


def phase8_document(mode: Literal["load", "save"], document: PHASE8_DOCUMENTS, data: None|dict = None):
    util_logger.debug("{} file: {} ...".\
                      format("loading" if mode == "load" else "saving",
                             document))
    filename = ""
    key = ""
    base_folder = BASE_PATH + "_8_planning"



    if document == "team_capacity":
        filename = base_folder + "/team_capacity.yaml"
        key = "team_capacity"

    if document == "tech_decision":
        filename = base_folder + "/technology_decisions.yaml"
        key = "technology_decisions"


    if document == "dev_roadmap":
        filename = base_folder + "/development_roadmap.yaml"
        key = "development_roadmap"

    if document == "sprint_plan":
        filename = base_folder + "/005_sprint_plans.yaml"
        key = "sprint_plans"

    if document == "resource_allocation":
        filename = base_folder + "/resource_allocation.yaml"
        key = "resource_allocation"

    if document == "milestone_definitions":
        filename = base_folder + "/milestone_definitions.yaml"
        key = "milestone_definitions"

    elif document == "epic_generated":
        filename = base_folder + "/002_epic_generated.yaml"
        key = "epic_list"

    elif document == "user_stories":
        filename = base_folder + "/004_user_stories.yaml"
        key = "user_stories"

    elif document == "just_user_stories":
        filename = base_folder + "/003_just_user_stories.yaml"
        key = "just_user_stories"

    elif document == "tickets_list":
        filename = base_folder + "/006_tickets_list.yaml"
        key = "tickets_list"

    elif document == "developer_tasks":
        filename = base_folder + "/007_developer_tasks.yaml"
        key = "developer_tasks"




    if mode == "save":
        util_logger.debug("Saving: {}".format(data))
        return file_management.save_yaml(file_name=filename, data=data)

    elif mode == "load":
        return file_management.load_yaml(file_name=filename)[key]

    return None


PHASE8_MD_DOCS = Literal[
    "phase1", "phase2", "phase3", "phase4", "phase5"
]
def phase8_md_doc(mode: Literal["load", "save"], document: PHASE8_MD_DOCS, data: None|dict = None):
    if mode == "save":
        util_logger.debug("Saving: {}".format(data))
        file_path = f"{BASE_PATH}_8_planning/001_{document}.md"
        return file_management.save_md(file_name=file_path, data=data)

    elif mode == "load":
        util_logger.debug("Loading: {}".format(data))
        file_path = f"{BASE_PATH}_8_planning/001_{document}.md"
        return file_management.load_md(file_name=file_path)

    return None
