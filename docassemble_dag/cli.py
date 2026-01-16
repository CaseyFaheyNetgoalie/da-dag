"""
Command-line interface for extracting DAG from Docassemble YAML files.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, List

from .comparison import compare_graphs
from .graph import DependencyGraph
from .parser import DocassembleParser
from .template_validator import validate_templates
from .utils import (
    find_nodes_by_authority,
    find_yaml_files,
    parse_multiple_files,
    parse_with_includes,
)
from .validation import GraphValidator

# Configure logging for CLI
logging.basicConfig(
    level=logging.WARNING,  # Only show warnings and errors by default
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Extract explicit dependency DAG from a Docassemble YAML interview file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m docassemble_dag interview.yaml
  python -m docassemble_dag interview.yaml -o output.json
  python -m docassemble_dag interview.yaml --check-cycles
        """
    )
    parser.add_argument(
        "input",
        help="Path to Docassemble YAML interview file or directory (for batch processing)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Path to output JSON file (default: stdout)"
    )
    parser.add_argument(
        "--check-cycles",
        action="store_true",
        help="Check for cycles and exit with error code if found"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run policy validation checks on the graph"
    )
    parser.add_argument(
        "--policies",
        nargs="+",
        help="Specific policies to check (default: all). Options: no_cycles, no_orphans, no_missing_dependencies, all_nodes_used, no_undefined_references"
    )
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with error code if validation finds any errors"
    )
    parser.add_argument(
        "--format",
        choices=["json", "dot", "graphml", "html"],
        default="json",
        help="Output format: json (default), dot (GraphViz), graphml (GraphML XML), or html (interactive viewer)"
    )
    parser.add_argument(
        "--pretty",
        dest="pretty",
        action="store_true",
        default=True,
        help="Pretty-print JSON output (default: True)"
    )
    parser.add_argument(
        "--no-pretty",
        dest="pretty",
        action="store_false",
        help="Output compact JSON (disable pretty printing)"
    )
    parser.add_argument(
        "--find-authority",
        dest="find_authority",
        help="Find all nodes with authority matching this pattern (case-insensitive substring match)"
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        default=True,
        help="When input is a directory, search recursively for YAML files (default: True)"
    )
    parser.add_argument(
        "--no-recursive",
        dest="recursive",
        action="store_false",
        help="When input is a directory, only search in top-level directory"
    )
    parser.add_argument(
        "--include-files",
        action="store_true",
        help="Parse 'include:' directives and analyze included files recursively"
    )
    parser.add_argument(
        "--compare-baseline",
        dest="compare_baseline",
        help="Path to baseline graph JSON file for comparison. Shows what changed."
    )
    parser.add_argument(
        "--validate-templates",
        dest="validate_templates",
        nargs="+",
        help="Validate template files (DOCX, PDF, Mako) against interview graph. Provide paths to template files."
    )
    
    args = parser.parse_args()
    
    # Handle input (file, directory, or glob pattern)
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(
            f"Error: Input path not found: {input_path}\n"
            "Please check the path and try again. Use --help for usage information.",
            file=sys.stderr
        )
        sys.exit(1)
    
    # Determine if we're processing multiple files
    yaml_files: List[Path] = []
    
    if input_path.is_file():
        # Single file
        if input_path.suffix not in ('.yaml', '.yml'):
            print(
                f"Error: Input file must be a YAML file (.yaml or .yml): {input_path}\n"
                "Please provide a valid Docassemble interview YAML file.",
                file=sys.stderr
            )
            sys.exit(1)
        yaml_files = [input_path]
    elif input_path.is_dir():
        # Directory - find all YAML files
        yaml_files = find_yaml_files(input_path, recursive=args.recursive)
        if not yaml_files:
            print(
                f"Error: No YAML files found in directory: {input_path}\n"
                "Please ensure the directory contains .yaml or .yml files.",
                file=sys.stderr
            )
            sys.exit(1)
        logger.info(f"Found {len(yaml_files)} YAML file(s) in {input_path}")
    
    # Parse files
    try:
        if args.include_files and len(yaml_files) == 1:
            # Parse with includes (recursive)
            graph, visited_files = parse_with_includes(yaml_files[0])
            if len(visited_files) > 1:
                logger.info(f"Parsed {len(visited_files)} file(s) including includes")
        elif len(yaml_files) == 1:
            # Single file, no includes
            file_path = yaml_files[0]
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml_text = f.read()
            parser = DocassembleParser(yaml_text, file_path=str(file_path))
            nodes = parser.extract_nodes()
            edges = parser.extract_edges(nodes)
            graph = DependencyGraph(nodes, edges)
        else:
            # Multiple files - batch processing
            graph = parse_multiple_files(yaml_files)
            logger.info(f"Merged {len(yaml_files)} file(s) into single graph")
    except ValueError as e:
        print(
            f"Error: Invalid YAML or interview structure\n"
            f"Details: {e}\n"
            "Please check your YAML syntax and try again.",
            file=sys.stderr
        )
        sys.exit(1)
    except Exception as e:
        print(
            f"Error: Failed to parse YAML or build graph\n"
            f"Details: {e}\n"
            "Please check your input file and try again.",
            file=sys.stderr
        )
        sys.exit(1)
    
    # Check for cycles if requested
    if args.check_cycles:
        cycles = graph.find_cycles()
        if cycles:
            print("Error: Cycles detected in dependency graph:", file=sys.stderr)
            for cycle in cycles:
                print(f"  {' -> '.join(cycle)}", file=sys.stderr)
            sys.exit(1)
    
    # Run validation if requested
    if args.validate:
        validator = GraphValidator(graph)
        violations = validator.validate_all(policies=args.policies)
        
        # Print validation results
        summary = validator.get_summary()
        print(f"Validation Results:", file=sys.stderr)
        print(f"  Total: {summary['total']}", file=sys.stderr)
        print(f"  Errors: {summary['errors']}", file=sys.stderr)
        print(f"  Warnings: {summary['warnings']}", file=sys.stderr)
        print(f"  Info: {summary['info']}", file=sys.stderr)
        print("", file=sys.stderr)
        
        if violations:
            print("Violations:", file=sys.stderr)
            for violation in violations:
                severity_marker = "✗" if violation.severity.value == "error" else "⚠" if violation.severity.value == "warning" else "ℹ"
                print(f"  {severity_marker} [{violation.rule_name}] {violation.message}", file=sys.stderr)
                if violation.node_name:
                    print(f"      Node: {violation.node_name}", file=sys.stderr)
                if violation.metadata and violation.metadata.get('file_path'):
                    print(f"      File: {violation.metadata['file_path']}:{violation.metadata.get('line_number', '?')}", file=sys.stderr)
            print("", file=sys.stderr)
        
        # Exit with error if requested and errors found
        if args.fail_on_error and summary['errors'] > 0:
            sys.exit(1)
    
    # Handle authority query
    if args.find_authority:
        matching_nodes = find_nodes_by_authority(graph, args.find_authority)
        print(f"\nFound {len(matching_nodes)} node(s) with authority matching '{args.find_authority}':", file=sys.stderr)
        for node in matching_nodes:
            print(f"  - {node.name} ({node.kind.value}): {node.authority}", file=sys.stderr)
            if node.file_path:
                print(f"    File: {node.file_path}:{node.line_number or '?'}", file=sys.stderr)
        print("", file=sys.stderr)
        
        # If authority query was requested, optionally output only matching nodes
        # For now, continue with full graph output
    
    # Handle graph comparison if baseline provided
    if args.compare_baseline:
        baseline_path = Path(args.compare_baseline)
        if not baseline_path.exists():
            print(
                f"Error: Baseline graph file not found: {baseline_path}\n"
                "Please provide a valid JSON file with graph data.",
                file=sys.stderr
            )
            sys.exit(1)
        
        try:
            with open(baseline_path, 'r', encoding='utf-8') as f:
                baseline_data = json.load(f)
            
            # Reconstruct baseline graph from JSON
            from .types import Node, NodeKind, Edge, DependencyType
            baseline_nodes = {
                n['name']: Node(
                    name=n['name'],
                    kind=NodeKind(n['kind']),
                    source=n['source'],
                    authority=n.get('authority'),
                    file_path=n.get('file_path'),
                    line_number=n.get('line_number'),
                )
                for n in baseline_data.get('nodes', [])
            }
            baseline_edges = [
                Edge(
                    from_node=e['from'],
                    to_node=e['to'],
                    dep_type=DependencyType(e['type']),
                    file_path=e.get('file_path'),
                    line_number=e.get('line_number'),
                )
                for e in baseline_data.get('edges', [])
            ]
            baseline_graph = DependencyGraph(baseline_nodes, baseline_edges)
            
            # Compare graphs
            diff = compare_graphs(baseline_graph, graph)
            diff_dict = diff.to_dict()
            
            print("Graph Comparison Results:", file=sys.stderr)
            print(f"  Added nodes: {len(diff.added_nodes)}", file=sys.stderr)
            print(f"  Removed nodes: {len(diff.removed_nodes)}", file=sys.stderr)
            print(f"  Changed nodes: {len(diff.changed_nodes)}", file=sys.stderr)
            print(f"  Added edges: {len(diff.added_edges)}", file=sys.stderr)
            print(f"  Removed edges: {len(diff.removed_edges)}", file=sys.stderr)
            print(f"  Authority changes: {len(diff.authority_changes)}", file=sys.stderr)
            print(f"  Affected nodes: {len(diff.affected_nodes)}", file=sys.stderr)
            
            # Output diff as JSON
            output_text = json.dumps(diff_dict, indent=2 if args.pretty else None, ensure_ascii=False)
        except Exception as e:
            print(
                f"Error comparing graphs: {e}\n"
                "Please ensure the baseline file contains valid graph JSON.",
                file=sys.stderr
            )
            sys.exit(1)
    
    # Handle template validation
    elif args.validate_templates:
        from pathlib import Path as PathType
        template_paths = [PathType(p) for p in args.validate_templates]
        results = validate_templates(template_paths, graph)
        
        print("Template Validation Results:", file=sys.stderr)
        all_valid = True
        for template_path, result in results.items():
            status = "✓ VALID" if result.is_valid else "✗ INVALID"
            print(f"\n{status}: {template_path}", file=sys.stderr)
            if result.undefined_variables:
                print(f"  Undefined variables: {', '.join(result.undefined_variables)}", file=sys.stderr)
            if result.undefined_objects:
                print(f"  Undefined objects: {', '.join(result.undefined_objects)}", file=sys.stderr)
            if not result.is_valid:
                all_valid = False
        
        if not all_valid and args.fail_on_error:
            sys.exit(1)
        
        # Output results as JSON
        results_dict = {path: result.to_dict() for path, result in results.items()}
        output_text = json.dumps(results_dict, indent=2 if args.pretty else None, ensure_ascii=False)
    
    # Generate output based on format
    elif args.format == "html":
        title = input_path.name if input_path.is_file() else f"DAG: {input_path.name} ({len(yaml_files)} files)"
        output_path_obj = Path(args.output) if args.output else None
        output_text = graph.to_html(output_path=output_path_obj, title=title)
        # HTML output always goes to file
        if not args.output:
            default_output = input_path.with_suffix('.html') if input_path.is_file() else Path(input_path.name + '.html')
            logger.info(f"HTML output saved to: {default_output}")
            output_text = graph.to_html(output_path=default_output, title=title)
            print(f"HTML visualization saved to: {default_output}", file=sys.stderr)
            sys.exit(0)
    elif args.format == "dot":
        title = input_path.name if input_path.is_file() else f"DAG: {input_path.name} ({len(yaml_files)} files)"
        output_text = graph.to_dot(title=title)
    elif args.format == "graphml":
        graph_id = input_path.stem if input_path.is_file() else input_path.name.replace('/', '_')
        output_text = graph.to_graphml(graph_id=graph_id)
    else:
        struct = graph.to_json_struct()
        # Pretty print by default (unless --no-pretty is specified)
        indent = 2 if args.pretty else None
        output_text = json.dumps(struct, indent=indent, ensure_ascii=False)
    
    # Write output
    if args.output:
        output_path = Path(args.output)
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output_text)
        except Exception as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output_text)


if __name__ == "__main__":
    main()
