"""
Tests for SiddhiEngine (server.service.siddhi).

`prashna` (QuestionTemplate / Prashna) and the root concept graph
(`mool.ConceptGraph`) are assumed to already have their own test suites.
This file focuses on SiddhiEngine itself, with two layers:

  1. ISOLATED UNIT TESTS (`engine_isolated` fixture)
     prashna / mool / prashna_template are stubbed with lightweight
     fakes, and `rcg` is replaced with a MagicMock, so level counting /
     branching / call wiring can be tested fast and deterministically.

  2. REAL-COMPONENT TESTS (`engine_real` fixture)
     Import the actual prashna, prashna_template, and mool modules
     unmodified. Only `rcg` is swapped out (by default, to a MagicMock;
     specific tests can replace it with a real ConceptGraph instance).

--------------------------------------------------------------------------
WHY `rcg` IS PATCHED POST-IMPORT INSTEAD OF VIA sys.modules:

`siddhi.py` does `from server.service import RootConceptGraph as rcg`.
There is no `server/service/RootConceptGraph.py` file in this project --
`RootConceptGraph` is exposed as an attribute on the already-loaded
`server.service` package (set in its `__init__.py`), not a submodule.
`from package import name` resolves `name` against the loaded package's
namespace first, so stubbing `sys.modules["server.service.RootConceptGraph"]`
is never consulted and has no effect.

The fix: import the real `siddhi` module normally, then reassign the
`rcg` name directly on the imported module object
(`module.rcg = MagicMock(...)`). Module-level names are looked up
dynamically at call time, so this reliably controls what `topic_switch()`
sees, regardless of how `rcg` was originally constructed.

Similarly, `siddhi.py` does `from server.service.mool import *`, a
star-import -- it binds `ConceptGraph`, `nx`, `log`, etc. directly into
`siddhi`'s namespace, but never binds a name `mool` itself. So real
component tests reference `engine_real.ConceptGraph`, not
`engine_real.mool.ConceptGraph`.
--------------------------------------------------------------------------

PREVIOUSLY FOUND, STILL-OPEN BUG:
`generate()` mutates `template.lower_bound` / `upper_bound` in place on
the shared object stored in TEMPLATES, so repeated calls widen the range
cumulatively and the effect leaks across SiddhiEngine instances sharing a
topic. See `test_generate_mutates_shared_template_cumulatively` and
`test_full_pipeline_correct_answers_raise_level_and_widen_real_bounds`.
--------------------------------------------------------------------------
"""
import sys
import types
import random
import importlib
import pytest
from unittest.mock import MagicMock, patch

SIDDHI_ENGINE_MODULE = "server.service.siddhi"


# ==========================================================================
# Layer 1: isolated fixtures / fakes
# ==========================================================================

class FakeTemplate:
    """Stand-in for a QuestionTemplate with mutable numeric bounds."""
    def __init__(self, lower_bound=0, upper_bound=100):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def __repr__(self):
        return f"FakeTemplate({self.lower_bound}, {self.upper_bound})"


@pytest.fixture
def fake_templates():
    return {
        "algebra": FakeTemplate(0, 100),
        "arithmetic": FakeTemplate(0, 50),
        "fractions": FakeTemplate(0, 20),
    }


@pytest.fixture
def mock_prashna_cls():
    mock_instance = MagicMock()
    mock_instance.generate.return_value = "GENERATED_QUESTION"
    mock_cls = MagicMock(return_value=mock_instance)
    return mock_cls, mock_instance


@pytest.fixture
def engine_isolated(fake_templates, mock_prashna_cls):
    """SiddhiEngine with prashna/mool/prashna_template stubbed, and rcg
    replaced post-import with a controllable MagicMock."""
    mock_cls, _ = mock_prashna_cls

    prashna_mod = types.ModuleType("server.service.prashna")
    prashna_mod.Prashna = mock_cls

    mool_mod = types.ModuleType("server.service.mool")  # empty: nothing needed by isolated tests

    template_mod = types.ModuleType("server.service.prashna_template")
    template_mod.TEMPLATES = fake_templates

    modules_patch = {
        "server.service.prashna": prashna_mod,
        "server.service.mool": mool_mod,
        "server.service.prashna_template": template_mod,
    }
    with patch.dict(sys.modules, modules_patch):
        sys.modules.pop(SIDDHI_ENGINE_MODULE, None)
        module = importlib.import_module(SIDDHI_ENGINE_MODULE)

        # `rcg` can't be intercepted via sys.modules (see module docstring) --
        # replace it directly on the freshly imported module instead.
        module.rcg = MagicMock()
        module.rcg.downgrade_concept = MagicMock(return_value=[])

        yield module
        sys.modules.pop(SIDDHI_ENGINE_MODULE, None)


# ==========================================================================
# Layer 2: real prashna / prashna_template / mool, controllable rcg only
# ==========================================================================

@pytest.fixture
def real_prashna_and_templates():
    """Import the real prashna + prashna_template modules directly (no
    SiddhiEngine involved) so their real shapes can be inspected and real
    QuestionTemplate objects reused in integration tests."""
    prashna_module = importlib.import_module("server.service.prashna")
    template_module = importlib.import_module("server.service.prashna_template")
    return prashna_module, template_module


@pytest.fixture
def engine_real():
    """
    SiddhiEngine imported with REAL prashna, REAL prashna_template, and
    REAL mool (all untouched). `rcg` is replaced post-import with a
    MagicMock by default; individual tests may reassign `module.rcg` to
    a real ConceptGraph instance for full end-to-end behavior.
    """
    sys.modules.pop(SIDDHI_ENGINE_MODULE, None)
    module = importlib.import_module(SIDDHI_ENGINE_MODULE)

    module.rcg = MagicMock()
    module.rcg.downgrade_concept = MagicMock(return_value=[])

    yield module
    sys.modules.pop(SIDDHI_ENGINE_MODULE, None)


# --------------------------------------------------------------------------
# Real-template shape / wiring checks
# --------------------------------------------------------------------------

def test_templates_is_a_dict_keyed_by_topic(real_prashna_and_templates):
    prashna_module, template_module = real_prashna_and_templates
    templates = template_module.TEMPLATES

    assert isinstance(templates, dict)
    assert templates  # non-empty
    for topic_key, template in templates.items():
        assert isinstance(template, prashna_module.QuestionTemplate)
        assert template.topic == topic_key


@pytest.mark.parametrize(
    "topic",
    ["Basic Arithmetic", "Variable", "Expression", "Operation Order", "Simplification"],
)
def test_templates_contains_expected_topics(real_prashna_and_templates, topic):
    _, template_module = real_prashna_and_templates
    assert topic in template_module.TEMPLATES


def test_siddhi_engine_init_succeeds_against_real_templates(engine_real, real_prashna_and_templates):
    _, template_module = real_prashna_and_templates

    eng = engine_real.SiddhiEngine("Expression")

    assert eng.target_topic == "Expression"
    assert eng.template is template_module.TEMPLATES["Expression"]
    assert eng.level == 1
    assert eng.trace == []


def test_siddhi_engine_init_unknown_topic_raises_keyerror(engine_real):
    with pytest.raises(KeyError):
        engine_real.SiddhiEngine("Not A Real Topic")


# ==========================================================================
# Layer 1 tests: __init__
# ==========================================================================

def test_init_sets_defaults(engine_isolated, fake_templates):
    eng = engine_isolated.SiddhiEngine("algebra")
    assert eng.target_topic == "algebra"
    assert eng.template is fake_templates["algebra"]
    assert eng.level == 1
    assert eng.trace == []


def test_init_unknown_topic_raises_keyerror(engine_isolated):
    with pytest.raises(KeyError):
        engine_isolated.SiddhiEngine("does_not_exist")


# ==========================================================================
# topic_switch
# ==========================================================================

def test_topic_switch_moves_to_first_downgraded_topic(engine_isolated):
    eng = engine_isolated.SiddhiEngine("algebra")
    engine_isolated.rcg.downgrade_concept.return_value = ["arithmetic", "fractions"]

    eng.topic_switch()

    assert eng.target_topic == "arithmetic"
    assert eng.trace == ["algebra"]
    engine_isolated.rcg.downgrade_concept.assert_called_once_with("algebra")


def test_topic_switch_dead_end_no_change(engine_isolated):
    eng = engine_isolated.SiddhiEngine("algebra")
    engine_isolated.rcg.downgrade_concept.return_value = []

    eng.topic_switch()

    assert eng.target_topic == "algebra"
    assert eng.trace == []


def test_topic_switch_called_multiple_times_appends_trace(engine_isolated):
    eng = engine_isolated.SiddhiEngine("algebra")
    engine_isolated.rcg.downgrade_concept.side_effect = [
        ["arithmetic"],
        ["fractions"],
    ]

    eng.topic_switch()
    eng.topic_switch()

    assert eng.target_topic == "fractions"
    assert eng.trace == ["algebra", "arithmetic"]


# ==========================================================================
# package_question
# ==========================================================================

def test_package_question_both_right_increments_level_by_two(engine_isolated):
    eng = engine_isolated.SiddhiEngine("algebra")
    eng.level = 3

    with patch.object(eng, "bulk_generate", return_value=["q1", "q2", "q3"]) as mock_bulk:
        result = eng.package_question(prev_response=1, quantity=3)

    assert eng.level == 5
    mock_bulk.assert_called_once_with(3, 5)
    assert result == ["q1", "q2", "q3"]


def test_package_question_one_wrong_keeps_level_unchanged(engine_isolated):
    eng = engine_isolated.SiddhiEngine("algebra")
    eng.level = 4

    with patch.object(eng, "bulk_generate", return_value=["q1"]) as mock_bulk:
        result = eng.package_question(prev_response=0, quantity=1)

    assert eng.level == 4
    mock_bulk.assert_called_once_with(1, 4)
    assert result == ["q1"]


def test_package_question_both_wrong_downgrades_topic_and_resets_level(engine_isolated):
    eng = engine_isolated.SiddhiEngine("algebra")
    eng.level = 5

    with patch.object(eng, "topic_switch") as mock_switch, \
         patch.object(eng, "bulk_generate", return_value=["easy_q"]) as mock_bulk:
        result = eng.package_question(prev_response=-1, quantity=2)

    mock_switch.assert_called_once_with()
    assert eng.level == 1
    mock_bulk.assert_called_once_with(2, 1)
    assert result == ["easy_q"]


def test_package_question_default_quantity_is_three(engine_isolated):
    eng = engine_isolated.SiddhiEngine("algebra")

    with patch.object(eng, "bulk_generate", return_value=[]) as mock_bulk:
        eng.package_question(prev_response=0)

    mock_bulk.assert_called_once_with(3, eng.level)


@pytest.mark.parametrize("prev_response", [1, 0, -1])
def test_package_question_returns_whatever_bulk_generate_returns(engine_isolated, prev_response):
    eng = engine_isolated.SiddhiEngine("algebra")
    sentinel = ["sentinel_question"]

    with patch.object(eng, "bulk_generate", return_value=sentinel), \
         patch.object(eng, "topic_switch"):
        result = eng.package_question(prev_response=prev_response, quantity=1)

    assert result is sentinel


# ==========================================================================
# generate
# ==========================================================================

def test_generate_computes_length_and_grouping_from_level(engine_isolated, mock_prashna_cls, fake_templates):
    mock_cls, mock_instance = mock_prashna_cls
    eng = engine_isolated.SiddhiEngine("algebra")
    template = fake_templates["algebra"]

    result = eng.generate(level=2)

    # hyper_parameter is hardcoded to 2 -> length = level * 2, grouping = level
    mock_cls.assert_called_once_with(template)
    mock_instance.generate.assert_called_once_with(2, length=4)
    assert result == "GENERATED_QUESTION"


def test_generate_widens_template_bounds_by_level(engine_isolated, fake_templates):
    eng = engine_isolated.SiddhiEngine("algebra")
    template = fake_templates["algebra"]
    orig_lower, orig_upper = template.lower_bound, template.upper_bound

    eng.generate(level=3)

    expected_delta = 10 * 3 * 2  # 10 * level * hyper_parameter
    assert template.lower_bound == orig_lower - expected_delta
    assert template.upper_bound == orig_upper + expected_delta


def test_generate_mutates_shared_template_cumulatively(engine_isolated, fake_templates):
    """
    Real bug, still present: generate() mutates the SAME template object
    stored in TEMPLATES in place. Repeated calls keep expanding the
    bounds indefinitely, and the effect leaks to any SiddhiEngine
    instance sharing that topic -- not just the caller.
    """
    eng = engine_isolated.SiddhiEngine("algebra")
    template = fake_templates["algebra"]
    start = (template.lower_bound, template.upper_bound)

    eng.generate(level=1)
    after_first = (template.lower_bound, template.upper_bound)
    eng.generate(level=1)
    after_second = (template.lower_bound, template.upper_bound)

    assert after_first != start
    assert after_second[0] < after_first[0]
    assert after_second[1] > after_first[1]

    other_eng = engine_isolated.SiddhiEngine("algebra")
    assert other_eng.template.lower_bound == after_second[0]
    assert other_eng.template.upper_bound == after_second[1]


def test_generate_uses_current_target_topic(engine_isolated, mock_prashna_cls, fake_templates):
    mock_cls, _ = mock_prashna_cls
    eng = engine_isolated.SiddhiEngine("algebra")
    eng.target_topic = "fractions"  # simulate a prior topic_switch

    eng.generate(level=1)

    mock_cls.assert_called_once_with(fake_templates["fractions"])


# ==========================================================================
# bulk_generate
# ==========================================================================

def test_bulk_generate_calls_generate_quantity_times_with_level(engine_isolated):
    eng = engine_isolated.SiddhiEngine("algebra")

    with patch.object(eng, "generate", return_value="Q") as mock_gen:
        result = eng.bulk_generate(quantity=4, level=2)

    assert mock_gen.call_count == 4
    mock_gen.assert_called_with(2)
    assert result == ["Q", "Q", "Q", "Q"]


def test_bulk_generate_zero_quantity_returns_empty_list(engine_isolated):
    eng = engine_isolated.SiddhiEngine("algebra")

    with patch.object(eng, "generate") as mock_gen:
        result = eng.bulk_generate(quantity=0, level=1)

    mock_gen.assert_not_called()
    assert result == []


def test_bulk_generate_preserves_generation_order(engine_isolated):
    eng = engine_isolated.SiddhiEngine("algebra")

    with patch.object(eng, "generate", side_effect=["q1", "q2", "q3"]):
        result = eng.bulk_generate(quantity=3, level=1)

    assert result == ["q1", "q2", "q3"]


# ==========================================================================
# Layer 1 integration: package_question -> bulk_generate -> generate
# ==========================================================================

def test_full_flow_correct_answer_raises_difficulty_and_produces_questions(engine_isolated, mock_prashna_cls):
    _, mock_instance = mock_prashna_cls
    mock_instance.generate.return_value = "Q"
    eng = engine_isolated.SiddhiEngine("algebra")
    eng.level = 1

    questions = eng.package_question(prev_response=1, quantity=3)

    assert eng.level == 3
    assert questions == ["Q", "Q", "Q"]
    assert mock_instance.generate.call_count == 3
    mock_instance.generate.assert_called_with(3, length=6)  # level=3, hyper_parameter=2


def test_full_flow_wrong_answer_downgrades_and_resets_to_level_one(engine_isolated, mock_prashna_cls):
    _, mock_instance = mock_prashna_cls
    mock_instance.generate.return_value = "Q"
    engine_isolated.rcg.downgrade_concept.return_value = ["arithmetic"]
    eng = engine_isolated.SiddhiEngine("algebra")
    eng.level = 5

    questions = eng.package_question(prev_response=-1, quantity=2)

    assert eng.target_topic == "arithmetic"
    assert eng.trace == ["algebra"]
    assert eng.level == 1
    assert questions == ["Q", "Q"]
    mock_instance.generate.assert_called_with(1, length=2)


def test_full_flow_wrong_answer_at_dead_end_stays_on_topic(engine_isolated, mock_prashna_cls):
    _, mock_instance = mock_prashna_cls
    mock_instance.generate.return_value = "Q"
    engine_isolated.rcg.downgrade_concept.return_value = []  # dead end
    eng = engine_isolated.SiddhiEngine("algebra")
    eng.level = 5

    questions = eng.package_question(prev_response=-1, quantity=1)

    assert eng.target_topic == "algebra"
    assert eng.trace == []
    assert eng.level == 1
    assert questions == ["Q"]


# ==========================================================================
# Layer 2 integration: real Prashna + real ConceptGraph + real TEMPLATES
# ==========================================================================

def test_full_pipeline_with_real_components(engine_real, real_prashna_and_templates):
    """
    End-to-end: real QuestionTemplate/Prashna question generation, a real
    ConceptGraph dependency chain driving topic downgrades, and the real
    dict-keyed TEMPLATES store. `ConceptGraph` is available directly on
    the siddhi module because `siddhi.py` star-imports it from mool.
    """
    _, template_module = real_prashna_and_templates
    ConceptGraph = engine_real.ConceptGraph

    # Build a real dependency chain: "Basic Arithmetic" -> "Variable" -> "Expression"
    graph = ConceptGraph()
    for topic in ["Basic Arithmetic", "Variable", "Expression"]:
        graph.add_concept(topic)
    graph.add_dependency("Basic Arithmetic", "Variable")
    graph.add_dependency("Variable", "Expression")

    # Swap the default rcg mock's downgrade_concept for the real graph's real method.
    engine_real.rcg.downgrade_concept = graph.downgrade_concept

    random.seed(1234)  # determinism for Prashna's internal randomness
    eng = engine_real.SiddhiEngine("Expression")
    assert eng.template is template_module.TEMPLATES["Expression"]

    # Wrong answer -> downgrades one step via the real graph, resets level.
    questions = eng.package_question(prev_response=-1, quantity=2)

    assert eng.target_topic == "Variable"
    assert eng.trace == ["Expression"]
    assert eng.level == 1
    assert len(questions) == 2
    assert all(isinstance(q, str) and len(q) > 0 for q in questions)

    # Downgrading again reaches the root, then a further downgrade is a dead end.
    eng.package_question(prev_response=-1, quantity=1)
    assert eng.target_topic == "Basic Arithmetic"
    eng.package_question(prev_response=-1, quantity=1)
    assert eng.target_topic == "Basic Arithmetic"  # root: dead end, unchanged


def test_full_pipeline_correct_answers_raise_level_and_widen_real_bounds(
    engine_real, real_prashna_and_templates
):
    _, template_module = real_prashna_and_templates
    template = template_module.TEMPLATES["Basic Arithmetic"]
    orig_lower, orig_upper = template.lower_bound, template.upper_bound

    random.seed(42)
    eng = engine_real.SiddhiEngine("Basic Arithmetic")

    questions = eng.package_question(prev_response=1, quantity=2)

    assert eng.level == 3  # 1 + 2
    assert len(questions) == 2
    assert all(isinstance(q, str) and len(q) > 0 for q in questions)
    # generate() widened the real, shared template bounds -- same bug as
    # the isolated test, now shown against the real QuestionTemplate.
    expected_delta = 10 * 3 * 2  # 10 * level * hyper_parameter, per call
    assert template.lower_bound == orig_lower - 2 * expected_delta
    assert template.upper_bound == orig_upper + 2 * expected_delta
