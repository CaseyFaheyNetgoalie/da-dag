"""
Utility functions for batch processing, graph merging, and multi-file support.
"""

import logging
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple

import yaml

from .graph import DependencyGraph
from .parser import DocassembleParser
from .types import DependencyType, Edge, Node, NodeKind

logger = logging.getLogger(__name__)


def find_yaml_files(path: Path, recursive: bool = True) -> List[Path]:
    """
    Find all YAML files in a directory.
    
    Args:
        path: Directory or file path
        recursive: If True, search recursively
        
    Returns:
        List of YAML file paths
    """
    path = Path(path)
    
    if path.is_file():
        if path.suffix in ('.yaml', '.yml'):
            return [path]
        return []
    
    if not path.is_dir():
        return []
    
    yaml_files = []
    if recursive:
        yaml_files = list(path.rglob('*.yaml')) + list(path.rglob('*.yml'))
    else:
        yaml_files = list(path.glob('*.yaml')) + list(path.glob('*.yml'))
    
    return sorted(yaml_files)


def merge_graphs(graphs: List[DependencyGraph]) -> DependencyGraph:
    """
    Merge multiple dependency graphs into a single graph.
    
    Nodes with the same name are merged (keeping metadata from first occurrence).
    Edges are combined.
    
    Args:
        graphs: List of DependencyGraph objects to merge
        
    Returns:
        Merged DependencyGraph
    """
    merged_nodes: Dict[str, Node] = {}
    merged_edges: List[Edge] = []
    edges_seen: Set[Tuple[str, str]] = set()
    
    for graph in graphs:
        # Merge nodes (first occurrence wins for conflicts)
        for name, node in graph.nodes.items():
            if name not in merged_nodes:
                merged_nodes[name] = node
        
        # Merge edges (avoid duplicates)
        for edge in graph.edges:
            edge_key = (edge.from_node, edge.to_node)
            if edge_key not in edges_seen:
                merged_edges.append(edge)
                edges_seen.add(edge_key)
    
    return DependencyGraph(merged_nodes, merged_edges)


def parse_multiple_files(file_paths: List[Path]) -> DependencyGraph:
    """
    Parse multiple YAML files and merge into a single dependency graph.
    
    Args:
        file_paths: List of YAML file paths
        
    Returns:
        Merged DependencyGraph
    """
    graphs = []
    
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml_text = f.read()
            
            parser = DocassembleParser(yaml_text, file_path=str(file_path))
            nodes = parser.extract_nodes()
            edges = parser.extract_edges(nodes)
            graph = DependencyGraph(nodes, edges)
            graphs.append(graph)
            logger.debug(f"Successfully parsed {file_path}: {len(nodes)} nodes, {len(edges)} edges")
        except Exception as e:
            logger.warning(
                f"Failed to parse {file_path}: {e}. "
                "This file will be skipped. Check YAML syntax and try again."
            )
            continue
    
    if not graphs:
        return DependencyGraph({}, [])
    
    return merge_graphs(graphs)


def find_nodes_by_authority(graph: DependencyGraph, authority_pattern: str) -> List[Node]:
    """
    Find all nodes that have an authority matching the pattern.
    
    Args:
        graph: DependencyGraph to search
        authority_pattern: Pattern to match (substring match, case-insensitive)
        
    Returns:
        List of Node objects matching the pattern
    """
    pattern_lower = authority_pattern.lower()
    matching_nodes = []
    
    for node in graph.nodes.values():
        if node.authority and pattern_lower in node.authority.lower():
            matching_nodes.append(node)
    
    return matching_nodes


def parse_include_directives(yaml_text: str, base_path: Optional[Path] = None) -> List[str]:
    """
    Parse 'include:' directives from YAML to find referenced files.
    
    Args:
        yaml_text: YAML content as string
        base_path: Base path for resolving relative includes
        
    Returns:
        List of file paths referenced in include directives
    """
    try:
        data = yaml.safe_load(yaml_text)
        if not isinstance(data, dict):
            return []
        
        includes = []
        
        # Check top-level 'include:' key
        include_val = data.get('include', [])
        if isinstance(include_val, list):
            includes.extend(include_val)
        elif isinstance(include_val, str):
            includes.append(include_val)
        
        # Check 'modules:' key (Docassemble alternative to include)
        modules_val = data.get('modules', [])
        if isinstance(modules_val, list):
            includes.extend(modules_val)
        elif isinstance(modules_val, str):
            includes.append(modules_val)
        
        # Resolve relative paths if base_path provided
        if base_path:
            resolved = []
            for inc in includes:
                if isinstance(inc, str):
                    # Try relative to base_path directory
                    if base_path.is_file():
                        base_dir = base_path.parent
                    else:
                        base_dir = base_path
                    
                    resolved_path = (base_dir / inc).resolve()
                    if resolved_path.exists():
                        resolved.append(str(resolved_path))
                    else:
                        # Keep original if not found (might be module name)
                        resolved.append(inc)
                else:
                    resolved.append(inc)
            includes = resolved
        
        return [str(inc) for inc in includes if isinstance(inc, str)]
    except Exception:
        return []


def parse_with_includes(file_path: Path, visited: Optional[Set[str]] = None) -> Tuple[DependencyGraph, Set[str]]:
    """
    Parse a YAML file and all its included files recursively.
    
    Args:
        file_path: Path to main YAML file
        visited: Set of already-visited file paths (to prevent cycles)
        
    Returns:
        Tuple of (merged DependencyGraph, set of all file paths visited)
    """
    if visited is None:
        visited = set()
    
    file_path = Path(file_path).resolve()
    file_str = str(file_path)
    
    # Prevent infinite recursion
    if file_str in visited:
        return DependencyGraph({}, []), visited
    
    visited.add(file_str)
    
    # Parse main file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            yaml_text = f.read()
    except FileNotFoundError as e:
        logger.warning(
            f"File not found: {file_path}. "
            "This file will be skipped. Check the file path and try again."
        )
        return DependencyGraph({}, []), visited
    except Exception as e:
        logger.warning(
            f"Failed to read {file_path}: {e}. "
            "This file will be skipped. Check file permissions and try again."
        )
        return DependencyGraph({}, []), visited
    
    # Find includes
    include_paths = parse_include_directives(yaml_text, base_path=file_path)
    
    # Parse main file
    parser = DocassembleParser(yaml_text, file_path=file_str)
    nodes = parser.extract_nodes()
    edges = parser.extract_edges(nodes)
    graph = DependencyGraph(nodes, edges)
    
    # Recursively parse included files
    for include_path in include_paths:
        include_file = Path(include_path)
        if include_file.exists():
            include_graph, visited = parse_with_includes(include_file, visited)
            graph = merge_graphs([graph, include_graph])
    
    return graph, visited
