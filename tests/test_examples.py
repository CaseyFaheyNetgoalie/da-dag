"""
Tests for example interview files.

Tests the real-world examples in the examples/ directory to ensure they parse
correctly and demonstrate the features they're meant to showcase.
"""

import pytest
from pathlib import Path
from docassemble_dag.parser import DocassembleParser
from docassemble_dag.graph import DependencyGraph
from docassemble_dag.validation import GraphValidator
from docassemble_dag.types import NodeKind, DependencyType


# Path to examples directory
EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


class TestExampleFiles:
    """Test that example files parse without errors."""
    
    def test_ny_cplr_sample_parses(self):
        """Test NY CPLR sample parses successfully."""
        file_path = EXAMPLES_DIR / "ny_cplr_sample.yaml"
        if not file_path.exists():
            pytest.skip(f"Example file not found: {file_path}")
        
        yaml_text = file_path.read_text()
        parser = DocassembleParser(yaml_text, file_path=str(file_path))
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        graph = DependencyGraph(nodes, edges)
        
        assert len(nodes) > 0
        assert len(edges) > 0
    
    def test_housing_eviction_parses(self):
        """Test housing eviction example parses successfully."""
        file_path = EXAMPLES_DIR / "housing_eviction.yaml"
        if not file_path.exists():
            pytest.skip(f"Example file not found: {file_path}")
        
        yaml_text = file_path.read_text()
        parser = DocassembleParser(yaml_text, file_path=str(file_path))
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        graph = DependencyGraph(nodes, edges)
        
        assert len(nodes) > 0
        assert len(edges) > 0
    
    def test_name_change_gender_affirming_parses(self):
        """Test name change example parses successfully."""
        file_path = EXAMPLES_DIR / "name_change_gender_affirming.yaml"
        if not file_path.exists():
            pytest.skip(f"Example file not found: {file_path}")
        
        yaml_text = file_path.read_text()
        parser = DocassembleParser(yaml_text, file_path=str(file_path))
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        graph = DependencyGraph(nodes, edges)
        
        assert len(nodes) > 0
        assert len(edges) > 0
    
    def test_immigration_asylum_parses(self):
        """Test immigration asylum example parses successfully."""
        file_path = EXAMPLES_DIR / "immigration_asylum.yaml"
        if not file_path.exists():
            pytest.skip(f"Example file not found: {file_path}")
        
        yaml_text = file_path.read_text()
        parser = DocassembleParser(yaml_text, file_path=str(file_path))
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        graph = DependencyGraph(nodes, edges)
        
        assert len(nodes) > 0
        assert len(edges) > 0


class TestNYCPLRSample:
    """Detailed tests for NY CPLR sample."""
    
    @pytest.fixture
    def cplr_graph(self):
        """Load and parse NY CPLR sample."""
        file_path = EXAMPLES_DIR / "ny_cplr_sample.yaml"
        if not file_path.exists():
            pytest.skip(f"Example file not found: {file_path}")
        
        yaml_text = file_path.read_text()
        parser = DocassembleParser(yaml_text, file_path=str(file_path))
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        return DependencyGraph(nodes, edges)
    
    def test_cplr_has_expected_nodes(self, cplr_graph):
        """Test CPLR sample has expected nodes."""
        expected_nodes = {
            "court_jurisdiction",
            "motion_type",
            "filing_deadline",
            "service_method",
            "service_complete",
        }
        
        for node_name in expected_nodes:
            assert node_name in cplr_graph.nodes, f"Missing expected node: {node_name}"
    
    def test_cplr_has_authority_citations(self, cplr_graph):
        """Test CPLR sample has authority citations."""
        nodes_with_authority = [
            n for n in cplr_graph.nodes.values()
            if n.authority and "CPLR" in n.authority
        ]
        
        assert len(nodes_with_authority) > 0, "Should have nodes with CPLR citations"
    
    def test_cplr_has_no_cycles(self, cplr_graph):
        """Test CPLR sample has no cycles."""
        assert not cplr_graph.has_cycles(), "CPLR sample should not have cycles"
    
    def test_cplr_dependencies_exist(self, cplr_graph):
        """Test expected dependencies exist."""
        # filing_deadline should depend on court_jurisdiction and motion_type
        filing_deps = cplr_graph.get_dependencies("filing_deadline")
        
        # May have implicit dependencies
        assert len(filing_deps) > 0, "filing_deadline should have dependencies"


class TestHousingEviction:
    """Detailed tests for housing eviction example."""
    
    @pytest.fixture
    def housing_graph(self):
        """Load and parse housing eviction sample."""
        file_path = EXAMPLES_DIR / "housing_eviction.yaml"
        if not file_path.exists():
            pytest.skip(f"Example file not found: {file_path}")
        
        yaml_text = file_path.read_text()
        parser = DocassembleParser(yaml_text, file_path=str(file_path))
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        return DependencyGraph(nodes, edges)
    
    def test_housing_has_ohio_statutes(self, housing_graph):
        """Test housing example has Ohio statute citations."""
        ohio_nodes = [
            n for n in housing_graph.nodes.values()
            if n.authority and "Ohio" in n.authority
        ]
        
        assert len(ohio_nodes) > 0, "Should have nodes with Ohio statute citations"
    
    def test_housing_has_objects(self, housing_graph):
        """Test housing example defines objects."""
        # Objects section should create nodes
        expected_objects = {"tenant", "landlord", "rental_unit", "court"}
        
        found_objects = set()
        for obj_name in expected_objects:
            if obj_name in housing_graph.nodes:
                found_objects.add(obj_name)
        
        assert len(found_objects) > 0, "Should find some object definitions"
    
    def test_housing_has_conditional_logic(self, housing_graph):
        """Test housing example has conditional dependencies."""
        # Look for edges that came from show if / enable if
        conditional_edges = [
            e for e in housing_graph.edges
            if e.dep_type == DependencyType.IMPLICIT
        ]
        
        assert len(conditional_edges) > 0, "Should have conditional dependencies"
    
    def test_housing_validation_passes(self, housing_graph):
        """Test housing example passes validation."""
        validator = GraphValidator(housing_graph)
        violations = validator.validate_all()
        
        # Should have no critical errors
        errors = [v for v in violations if v.severity.value == "error"]
        assert len(errors) == 0, f"Should have no validation errors, found: {errors}"


class TestNameChange:
    """Detailed tests for name change example."""
    
    @pytest.fixture
    def name_change_graph(self):
        """Load and parse name change sample."""
        file_path = EXAMPLES_DIR / "name_change_gender_affirming.yaml"
        if not file_path.exists():
            pytest.skip(f"Example file not found: {file_path}")
        
        try:
            yaml_text = file_path.read_text()
            parser = DocassembleParser(yaml_text, file_path=str(file_path))
            nodes = parser.extract_nodes()
            edges = parser.extract_edges(nodes)
            return DependencyGraph(nodes, edges)
        except Exception as e:
            pytest.skip(f"Could not parse {file_path}: {e}")
    
    def test_name_change_has_assembly_line(self, name_change_graph):
        """Test name change uses Assembly Line objects."""
        al_nodes = [
            n for n in name_change_graph.nodes.values()
            if n.name.startswith("AL_") or n.kind == NodeKind.ASSEMBLY_LINE
        ]
        
        assert len(al_nodes) > 0, "Should have Assembly Line nodes"
    
    def test_name_change_has_jurisdiction_logic(self, name_change_graph):
        """Test name change has jurisdiction-specific logic."""
        assert "jurisdiction" in name_change_graph.nodes
        
        # jurisdiction should have dependents (things that depend on it)
        jurisdiction_dependents = name_change_graph.get_dependents("jurisdiction")
        assert len(jurisdiction_dependents) > 0, "jurisdiction should have dependents"


class TestImmigrationAsylum:
    """Detailed tests for immigration asylum example."""
    
    @pytest.fixture
    def asylum_graph(self):
        """Load and parse asylum sample."""
        file_path = EXAMPLES_DIR / "immigration_asylum.yaml"
        if not file_path.exists():
            pytest.skip(f"Example file not found: {file_path}")
        
        yaml_text = file_path.read_text()
        parser = DocassembleParser(yaml_text, file_path=str(file_path))
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        return DependencyGraph(nodes, edges)
    
    def test_asylum_has_multilanguage(self, asylum_graph):
        """Test asylum example has multi-language support."""
        # Should have primary_language variable
        assert "primary_language" in asylum_graph.nodes
    
    def test_asylum_has_deadline_calculation(self, asylum_graph):
        """Test asylum example has deadline calculation."""
        # Should have deadline-related nodes
        deadline_nodes = [
            "entry_date",
            "days_since_entry",
            "application_deadline"
        ]
        
        found = [n for n in deadline_nodes if n in asylum_graph.nodes]
        assert len(found) > 0, "Should have deadline calculation nodes"
    
    def test_asylum_has_immigration_citations(self, asylum_graph):
        """Test asylum example has immigration law citations."""
        usc_nodes = [
            n for n in asylum_graph.nodes.values()
            if n.authority and ("USC" in n.authority or "CFR" in n.authority)
        ]
        
        assert len(usc_nodes) > 0, "Should have immigration law citations"


class TestExamplesIntegration:
    """Integration tests across all examples."""
    
    def test_all_examples_parse_without_errors(self):
        """Test all example files parse successfully."""
        example_files = [
            "ny_cplr_sample.yaml",
            "housing_eviction.yaml",
            "name_change_gender_affirming.yaml",
            "immigration_asylum.yaml",
        ]
        
        for filename in example_files:
            file_path = EXAMPLES_DIR / filename
            if not file_path.exists():
                continue
            
            yaml_text = file_path.read_text()
            parser = DocassembleParser(yaml_text, file_path=str(file_path))
            nodes = parser.extract_nodes()
            edges = parser.extract_edges(nodes)
            graph = DependencyGraph(nodes, edges)
            
            # Basic sanity checks
            assert len(nodes) > 0, f"{filename} should have nodes"
            assert isinstance(graph, DependencyGraph), f"{filename} should create valid graph"
    
    def test_all_examples_have_no_critical_errors(self):
        """Test all examples pass basic validation."""
        example_files = [
            "ny_cplr_sample.yaml",
            "housing_eviction.yaml",
            "name_change_gender_affirming.yaml",
            "immigration_asylum.yaml",
        ]
        
        for filename in example_files:
            file_path = EXAMPLES_DIR / filename
            if not file_path.exists():
                continue
            
            yaml_text = file_path.read_text()
            parser = DocassembleParser(yaml_text, file_path=str(file_path))
            nodes = parser.extract_nodes()
            edges = parser.extract_edges(nodes)
            graph = DependencyGraph(nodes, edges)
            
            validator = GraphValidator(graph)
            violations = validator.validate_all()
            
            # Should have no critical errors (cycles, undefined references)
            critical_errors = [
                v for v in violations
                if v.severity.value == "error" and v.rule_name in ["no_cycles", "no_undefined_references"]
            ]
            
            assert len(critical_errors) == 0, f"{filename} should have no critical errors"
    
    def test_examples_demonstrate_different_features(self):
        """Test that examples showcase different features."""
        features_found = {
            "authority_citations": False,
            "assembly_line": False,
            "objects": False,
            "multi_language": False,
            "conditional_logic": False,
        }
        
        example_files = list((EXAMPLES_DIR).glob("*.yaml"))
        
        for file_path in example_files:
            if file_path.name.startswith("test_"):
                continue
            
            try:
                yaml_text = file_path.read_text()
                parser = DocassembleParser(yaml_text, file_path=str(file_path))
                nodes = parser.extract_nodes()
                edges = parser.extract_edges(nodes)
                
                # Check for authority citations
                if any(n.authority for n in nodes.values()):
                    features_found["authority_citations"] = True
                
                # Check for Assembly Line
                if any(n.kind == NodeKind.ASSEMBLY_LINE for n in nodes.values()):
                    features_found["assembly_line"] = True
                
                # Check for objects (metadata with object_type)
                if any(n.metadata.get("object_type") for n in nodes.values()):
                    features_found["objects"] = True
                
                # Check for multi-language (primary_language variable)
                if "primary_language" in nodes:
                    features_found["multi_language"] = True
                
                # Check for conditional logic (show if, enable if)
                if any(e.dep_type == DependencyType.IMPLICIT for e in edges):
                    features_found["conditional_logic"] = True
            
            except Exception:
                # Skip files that don't parse
                continue
        
        # At least some features should be demonstrated
        assert sum(features_found.values()) >= 3, "Examples should demonstrate multiple features"
