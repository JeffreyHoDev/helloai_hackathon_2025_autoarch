from google.adk.tools import ToolContext

import networkx as nx
import json
import random
import os
import matplotlib.pyplot as plt
import datetime
import graphviz
import datetime
import networkx as nx
import google.genai.types as types

def create_dependency_graph(resource_data):
    """
    Creates a directed graph (DiGraph) from the resource data.
    
    Args:
        resource_data (dict): A dictionary of resources, dependencies, and durations.
        
    Returns:
        nx.DiGraph: A directed graph representing the dependencies.
    """
    G = nx.DiGraph()
    
    # Add nodes for all resources and set their duration as a node attribute
    for resource, data in resource_data.items():
        G.add_node(resource, duration=data.get("duration", 0))
        
    # Add edges to represent dependencies (parent -> child)
    for resource, data in resource_data.items():
        for dependency in data.get("dependencies", []):
            # The edge weight is the duration of the dependent resource (the source node)
            dep_duration = resource_data.get(dependency, {}).get("duration", 0)
            G.add_edge(dependency, resource, weight=dep_duration)
            
    return G

def find_and_visualize_critical_paths(graph, start_node, end_node, near_critical_threshold):
    """
    Finds and visualizes the critical and near-critical paths.

    Args:
        graph (nx.DiGraph): The dependency graph.
        start_node (str): The starting node for the path analysis.
        end_node (str): The ending node for the path analysis.
        near_critical_threshold (float): A percentage threshold to identify near-critical paths.
    """
    print(f"\n--- Analyzing Migration Paths from '{start_node}' to '{end_node}' ---")

    # Find all simple paths
    try:
        all_paths = list(nx.all_simple_paths(graph, source=start_node, target=end_node))
    except nx.NetworkXNoPath:
        print("No paths found between these nodes.")
        return

    # Calculate path duration and sort by weight
    path_durations = []
    for path in all_paths:
        total_duration = sum(graph.nodes[node]['duration'] for node in path)
        path_durations.append((total_duration, path))

    path_durations.sort(key=lambda x: x[0], reverse=True)

    if not path_durations:
        print("No paths found between these nodes.")
        return

    # Identify critical and near-critical paths
    critical_path = path_durations[0][1]
    max_duration = path_durations[0][0]
    print(f"Primary Critical Path (Duration: {max_duration}): {' -> '.join(critical_path)}")

    critical_edges = list(zip(critical_path, critical_path[1:]))
    near_critical_edges = []
    
    print("\n--- Near-Critical Paths ---")
    for duration, path in path_durations[1:]:
        if duration >= max_duration * near_critical_threshold:
            print(f"Path (Duration: {duration}): {' -> '.join(path)}")
            near_critical_edges.extend(list(zip(path, path[1:])))

    # Visualization using Matplotlib
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(graph, seed=42) # For consistent layout

    # Draw all edges in a default color
    nx.draw_networkx_edges(graph, pos, edge_color='lightgray', width=1)
    
    # Draw near-critical edges in a distinct color
    nx.draw_networkx_edges(graph, pos, edgelist=near_critical_edges, edge_color='orange', width=2)

    # Draw the critical path edges in a different, prominent color
    nx.draw_networkx_edges(graph, pos, edgelist=critical_edges, edge_color='red', width=3)
    
    # Draw nodes and labels
    nx.draw_networkx_nodes(graph, pos, node_color='lightblue', node_size=1000)
    nx.draw_networkx_labels(graph, pos, font_size=10, font_family='sans-serif')
    
    # Add edge labels with weights (durations)
    edge_labels = nx.get_edge_attributes(graph, 'weight')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)

    plt.title(f"Critical Path Analysis from '{start_node}' to '{end_node}'")
    plt.show()

def analyze_dependencies(graph):
    """
    Performs basic dependency analysis on the graph.
    
    Args:
        graph (nx.DiGraph): The dependency graph.
    """
    print("--- Cloud Architecture Dependency Report ---")
    print(f"Total Resources (Nodes): {graph.number_of_nodes()}")
    print(f"Total Dependencies (Edges): {graph.number_of_edges()}\n")

    # Find resources with no dependencies (potential "roots" of the architecture)
    root_resources = [node for node, degree in graph.in_degree() if degree == 0]
    print("--- Root Resources (No Incoming Dependencies) ---")
    for resource in root_resources:
        print(f"- {resource}")

    # Find resources that are highly dependent on others (have many incoming edges)
    highly_dependent_resources = sorted(graph.in_degree(), key=lambda x: x[1], reverse=True)[:3]
    print("\n--- Top 3 Most Dependent Resources ---")
    for resource, degree in highly_dependent_resources:
        print(f"- {resource} (Dependent on {degree} resources)")

    # Find resources that are critical for many others (have many outgoing edges)
    critical_resources = sorted(graph.out_degree(), key=lambda x: x[1], reverse=True)[:3]
    print("\n--- Top 3 Critical Resources (Depend on Many Others) ---")
    for resource, degree in critical_resources:
        print(f"- {resource} (Critical for {degree} resources)")

async def analyze_and_visualize_migration_path(resource_data: dict, start_node: str, end_node: str, num_paths_to_show: int, tool_context: ToolContext) -> str:
    """
    Combines graph creation and visualization into a single function.
    
    This function will build the graph, find the critical path, and save
    the visualization to a file. It returns a success message or an error.
    Selecting Start and End Nodes
    start_node: This should be a resource that has no incoming dependencies within the scope of your analysis. It's the "root" of a dependency chain. For example, a Virtual Private Cloud (VPC), a top-level security group, or a foundational storage bucket.

    end_node: This should be the final resource in a specific application's migration chain, which has no outgoing dependencies to other resources within the same migration wave. This is often the user-facing web server or the final database.
    
    Args:
        resource_data (dict): A dictionary of resources, dependencies, and durations.
        start_node (str): The starting node for the path analysis.
        end_node (str): The ending node for the path analysis.
        num_paths_to_show (int): The number of top critical paths to highlight. Default to 3, but can put more if you think appropriate and cover all the paths possible
        
    Returns:
        str: A message indicating the success or failure of the operation.
    """
    try:
        # 1. Build the dependency graph
        graph = create_dependency_graph(resource_data)
        
        # 2. Find all simple paths
        all_paths = list(nx.all_simple_paths(graph, source=start_node, target=end_node))
        
        if not all_paths:
            return f"Error: No paths found between '{start_node}' and '{end_node}'."

        # 3. Calculate path duration and sort by weight
        path_durations = []
        for path in all_paths:
            total_duration = sum(graph.nodes[node]['duration'] for node in path)
            path_durations.append((total_duration, path))

        path_durations.sort(key=lambda x: x[0], reverse=True)

        # 4. Identify the top N critical paths
        top_n_paths = path_durations[:num_paths_to_show]
        path_colors = ['red', 'blue', 'green', 'purple', 'orange']

        print(f"\n--- Top {num_paths_to_show} Critical Paths ---")
        for i, (duration, path) in enumerate(top_n_paths):
            print(f"Path {i+1} (Duration: {duration}): {' -> '.join(path)}")

        # 5. Visualization using Matplotlib
        plt.figure(figsize=(20, 15)) # Increased figure size
        pos = nx.fruchterman_reingold_layout(graph, k=2.0, iterations=100, seed=42) # Increased spacing and iterations
        
        # Draw all nodes and labels first
        nx.draw_networkx_nodes(graph, pos, node_color='lightblue', node_size=1500)
        nx.draw_networkx_labels(graph, pos, font_size=12, font_family='sans-serif')
        
        # Draw all edges in a default color
        nx.draw_networkx_edges(graph, pos, edge_color='lightgray', width=1)
        
        # Draw each of the top paths with a unique color and a legend
        for i, (duration, path) in enumerate(top_n_paths):
            path_edges = list(zip(path, path[1:]))
            nx.draw_networkx_edges(graph, pos, edgelist=path_edges, edge_color=path_colors[i % len(path_colors)], 
                                   width=3, label=f"Path {i+1} (Dur: {duration})")

        # Add edge labels with weights (durations)
        edge_labels = nx.get_edge_attributes(graph, 'weight')
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)

        plt.title(f"Critical Path Analysis from '{start_node}' to '{end_node}'", fontsize=16)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10) # Adjust legend position
        
        # Generate a unique filename with a timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"critical_paths_single_{timestamp}.png"
        plt.savefig(filename)
        plt.close() # Close the plot to free up memory
        with open(filename, "rb") as file:
            image_bytes = file.read()
        artifact = types.Part(
            inline_data=types.Blob(
                data=image_bytes,
                mime_type="image/png"
            )
        )
        
        await tool_context.save_artifact(
            filename=filename,
            artifact=artifact
        )
        return f"Success: The critical path image has been saved to '{filename}'."
        
    except nx.NetworkXError as e:
        return f"Error: A NetworkX error occurred during path analysis. Details: {e}"
    except Exception as e:
        return f"Error: An unexpected error occurred. Details: {e}"
    
def save_weightage(dependecies_data: dict, tool_context: ToolContext) -> str:
    """
    Saves the dependencies_data to state for reference.
    
    Args:
        dependecies_data (dict): A dictionary of resources, their dependencies, their weightage value and their reasoning.
        
    Returns:
        Either operation is success or error
    """
    try:
        tool_context.state["dependencies_with_weightage"] = dependecies_data
    except Exception as e:
        return str(e)
    return "success"



def create_dependency_graph(resource_data: dict):
    # This is a placeholder for your actual graph creation logic
    # It should return a NetworkX DiGraph object
    G = nx.DiGraph()
    for node, data in resource_data.items():
        G.add_node(node, duration=data.get('duration', 0))
        for dependency in data.get('dependencies', []):
            G.add_edge(dependency, node)
    return G

async def analyze_and_visualize_migration_path_graphviz(resource_data: dict, start_node: str, end_node: str, num_paths_to_show: int, tool_context: ToolContext) -> str:
    """
    Combines graph creation and visualization into a single function using Graphviz.
    
    
    Args:
        resource_data (dict): A dictionary of resources, dependencies, and their durations.
        start_node (str): The starting node for the path analysis.
        end_node (str): The ending node for the path analysis.
        num_paths_to_show (int): The number of top critical paths to highlight.
        
    Returns:
        str: A message indicating the success or failure of the operation.
    """
    try:
        # 1. Build the dependency graph
        graph = create_dependency_graph(resource_data)
        
        # 2. Find all simple paths
        all_paths = list(nx.all_simple_paths(graph, source=start_node, target=end_node))
        
        if not all_paths:
            return f"Error: No paths found between '{start_node}' and '{end_node}'."

        # 3. Calculate path total durations and sort
        path_durations = []
        for path in all_paths:
            total_duration = sum(graph.nodes[node]['duration'] for node in path)
            path_durations.append({'total_duration': total_duration, 'path': path})

        path_durations.sort(key=lambda x: x['total_duration'], reverse=True)

        # 4. Identify the top N critical paths
        top_n_paths = path_durations[:num_paths_to_show]
        print(f"\n--- Top {num_paths_to_show} Critical Paths ---")
        for i, path_info in enumerate(top_n_paths):
            print(f"Path {i+1} (Total Weightage: {path_info['total_duration']}): {' -> '.join(path_info['path'])}")

        # 5. Visualization using Graphviz
        dot = graphviz.Digraph(comment='Migration Path', engine='dot')
        dot.attr(rankdir='LR', overlap='false', splines='true')
        dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue')

        # Create sets of nodes and edges to be highlighted
        highlighted_nodes = set()
        highlighted_edges = set()
        path_edge_colors = {}
        
        path_colors = ['red', 'blue', 'green', 'purple', 'orange']

        for i, path_info in enumerate(top_n_paths):
            path = path_info['path']
            color = path_colors[i % len(path_colors)]
            
            highlighted_nodes.update(path)

            path_edges = list(zip(path, path[1:]))
            for u, v in path_edges:
                if (u, v) not in path_edge_colors:
                    path_edge_colors[(u, v)] = color
                highlighted_edges.add((u, v))

        # 6. Build the graph based on analysis
        for node in graph.nodes:
            duration = graph.nodes[node].get('duration', 0)
            dot.node(node, f"{node}\n({duration} weightage)")

        for u, v in graph.edges:
            if (u, v) in path_edge_colors:
                dot.edge(u, v, color=path_edge_colors[(u,v)], penwidth='3.0')
            else:
                dot.edge(u, v, color='lightgray', penwidth='1.0')
        
        for node in graph.nodes:
            if node in highlighted_nodes:
                dot.node(node, f"{node}\n({graph.nodes[node]['duration']} weightage)", style='rounded,filled', fillcolor='white', color='red', fontcolor='red', penwidth='3.0')
            else:
                dot.node(node, f"{node}\n({graph.nodes[node]['duration']} weightage)")

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"critical_paths_graphviz_{timestamp}"
        
        dot.render(filename, view=False, format='png')
        
        with open(filename + ".png", "rb") as file:
            image_bytes = file.read()
            artifact = types.Part(
                inline_data=types.Blob(
                    data=image_bytes,
                    mime_type="image/png"
                )
            )
            
        await tool_context.save_artifact(
            filename=filename + ".png",
            artifact=artifact
        )
        
        return f"Success: The critical path image has been saved to '{filename}.png'."
        
    except nx.NetworkXError as e:
        return f"Error: A NetworkX error occurred during path analysis. Details: {e}"
    except Exception as e:
        return f"Error: An unexpected error occurred. Details: {e}"