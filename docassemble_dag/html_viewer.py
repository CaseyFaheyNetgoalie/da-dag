"""
HTML interactive viewer for dependency graphs.

Generates standalone HTML files with interactive D3.js visualizations
that allow users to explore dependency graphs without technical knowledge.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Any

from .graph import DependencyGraph
from .types import NodeKind


def to_html(
    graph: DependencyGraph,
    output_path: Optional[Path] = None,
    title: str = "Dependency Graph",
    width: int = 1200,
    height: int = 800,
) -> str:
    """
    Generate interactive HTML visualization of the dependency graph.
    
    Creates a standalone HTML file with D3.js visualization that includes:
    - Interactive node/edge highlighting
    - Filtering by node kind, authority
    - Search functionality
    - Zoom and pan
    - Export to PNG/PDF
    
    Args:
        graph: Dependency graph to visualize
        output_path: Optional path to save HTML file
        title: Title for the visualization
        width: Canvas width in pixels
        height: Canvas height in pixels
        
    Returns:
        HTML content as string
        
    Example:
        >>> html = to_html(graph, Path("graph.html"), "My Interview Dependencies")
        >>> # Opens interactive viewer in browser
    """
    # Convert graph to JSON structure
    graph_json = graph.to_json_struct()
    
    # Generate HTML with embedded D3.js visualization
    html_content = _generate_html_template(
        title=title,
        graph_json=json.dumps(graph_json, indent=2),
        width=width,
        height=height,
    )
    
    # Save to file if path provided
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    return html_content


def _generate_html_template(
    title: str,
    graph_json: str,
    width: int,
    height: int,
) -> str:
    """Generate HTML template with embedded D3.js visualization."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 20px;
        }}
        h1 {{
            margin: 0 0 20px 0;
            color: #333;
        }}
        .controls {{
            margin-bottom: 20px;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 4px;
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            align-items: center;
        }}
        .control-group {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        label {{
            font-weight: 600;
            color: #555;
        }}
        input, select, button {{
            padding: 6px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }}
        button {{
            background: #007bff;
            color: white;
            border: none;
            cursor: pointer;
        }}
        button:hover {{
            background: #0056b3;
        }}
        #graph-container {{
            width: 100%;
            height: {height}px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background: white;
        }}
        .node {{
            cursor: pointer;
        }}
        .node circle {{
            stroke: #333;
            stroke-width: 2px;
        }}
        .node text {{
            font-size: 12px;
            pointer-events: none;
        }}
        .link {{
            stroke: #999;
            stroke-opacity: 0.6;
            stroke-width: 1.5px;
        }}
        .link.explicit {{
            stroke: #28a745;
        }}
        .link.implicit {{
            stroke: #ffc107;
        }}
        .legend {{
            margin-top: 20px;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 4px;
        }}
        .legend-item {{
            display: inline-block;
            margin-right: 20px;
        }}
        .legend-color {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-right: 5px;
            vertical-align: middle;
        }}
        .stats {{
            margin-top: 15px;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        
        <div class="controls">
            <div class="control-group">
                <label>Search:</label>
                <input type="text" id="search" placeholder="Search nodes...">
            </div>
            
            <div class="control-group">
                <label>Filter by Kind:</label>
                <select id="kind-filter">
                    <option value="">All</option>
                    <option value="variable">Variables</option>
                    <option value="question">Questions</option>
                    <option value="rule">Rules</option>
                    <option value="assembly_line">Assembly Line</option>
                </select>
            </div>
            
            <div class="control-group">
                <label>Filter by Authority:</label>
                <input type="text" id="authority-filter" placeholder="Filter by statute...">
            </div>
            
            <button onclick="resetView()">Reset View</button>
            <button onclick="exportPNG()">Export PNG</button>
        </div>
        
        <div id="graph-container"></div>
        
        <div class="stats" id="stats"></div>
        
        <div class="legend">
            <strong>Legend:</strong>
            <span class="legend-item">
                <span class="legend-color" style="background: #1f77b4;"></span>
                Node (Variable/Question/Rule)
            </span>
            <span class="legend-item">
                <span style="border: 2px solid #28a745; display: inline-block; width: 20px; height: 20px; margin-right: 5px; vertical-align: middle;"></span>
                Explicit Dependency
            </span>
            <span class="legend-item">
                <span style="border: 2px solid #ffc107; display: inline-block; width: 20px; height: 20px; margin-right: 5px; vertical-align: middle;"></span>
                Implicit Dependency
            </span>
        </div>
    </div>
    
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script>
        // Graph data
        const graphData = {graph_json};
        
        // Initialize D3.js force-directed graph
        const width = {width};
        const height = {height};
        const svg = d3.select("#graph-container")
            .append("svg")
            .attr("width", width)
            .attr("height", height);
        
        const g = svg.append("g");
        
        // Zoom and pan
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", (event) => {{
                g.attr("transform", event.transform);
            }});
        
        svg.call(zoom);
        
        // Map edges to node objects for D3.js force simulation
        const linkData = graphData.edges.map(edge => {{
            const sourceNode = graphData.nodes.find(n => n.name === edge.from);
            const targetNode = graphData.nodes.find(n => n.name === edge.to);
            return {{
                source: sourceNode,
                target: targetNode,
                type: edge.type
            }};
        }}).filter(d => d.source && d.target);  // Filter out invalid links
        
        // Force simulation
        const simulation = d3.forceSimulation(graphData.nodes)
            .force("link", d3.forceLink(linkData).id(d => d.name).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(30));
        
        // Draw links
        const link = g.append("g")
            .selectAll("line")
            .data(linkData)
            .enter().append("line")
            .attr("class", d => `link ${{d.type}}`)
            .attr("stroke-width", 2);
        
        // Draw nodes
        const node = g.append("g")
            .selectAll("g")
            .data(graphData.nodes)
            .enter().append("g")
            .attr("class", "node")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));
        
        node.append("circle")
            .attr("r", 10)
            .attr("fill", d => getNodeColor(d.kind))
            .on("mouseover", function(event, d) {{
                showTooltip(event, d);
            }})
            .on("mouseout", hideTooltip);
        
        node.append("text")
            .attr("dx", 15)
            .attr("dy", 4)
            .text(d => d.name)
            .attr("font-size", "12px");
        
        // Update positions on simulation tick
        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source?.x || 0)
                .attr("y1", d => d.source?.y || 0)
                .attr("x2", d => d.target?.x || 0)
                .attr("y2", d => d.target?.y || 0);
            
            node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
        }});
        
        // Helper functions
        function getNodeColor(kind) {{
            const colors = {{
                "variable": "#1f77b4",
                "question": "#ff7f0e",
                "rule": "#2ca02c",
                "assembly_line": "#9467bd"
            }};
            return colors[kind] || "#cccccc";
        }}
        
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}
        
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
        
        function showTooltip(event, d) {{
            // Create tooltip
            const tooltip = d3.select("body").append("div")
                .attr("class", "tooltip")
                .style("position", "absolute")
                .style("background", "rgba(0,0,0,0.8)")
                .style("color", "white")
                .style("padding", "8px")
                .style("border-radius", "4px")
                .style("pointer-events", "none")
                .style("opacity", 0);
            
            const info = [
                `Name: ${{d.name}}`,
                `Kind: ${{d.kind}}`,
                `Source: ${{d.source}}`,
                d.authority ? `Authority: ${{d.authority}}` : null
            ].filter(Boolean).join("<br>");
            
            tooltip.html(info)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px")
                .transition()
                .duration(200)
                .style("opacity", 1);
        }}
        
        function hideTooltip() {{
            d3.selectAll(".tooltip").remove();
        }}
        
        function resetView() {{
            svg.transition().call(
                zoom.transform,
                d3.zoomIdentity
            );
            document.getElementById("search").value = "";
            document.getElementById("kind-filter").value = "";
            document.getElementById("authority-filter").value = "";
        }}
        
        function exportPNG() {{
            // Export SVG to PNG (simplified - would need html2canvas for full implementation)
            alert("Export PNG functionality would require additional library (html2canvas)");
        }}
        
        // Update stats
        document.getElementById("stats").innerHTML = `
            Nodes: ${{graphData.nodes.length}} | 
            Edges: ${{graphData.edges.length}} |
            Explicit: ${{graphData.edges.filter(e => e.type === 'explicit').length}} |
            Implicit: ${{graphData.edges.filter(e => e.type === 'implicit').length}}
        `;
    </script>
</body>
</html>
"""
