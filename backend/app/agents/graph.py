"""
Agent Graph Definition

Main LangGraph state machine for research agent workflows.
"""

from typing import Literal
from langgraph.graph import StateGraph, END

from app.agents.state import DiscoveryState, DeepDiveState, PaperState


def create_discovery_graph():
    """
    Create the discovery agent graph.
    
    Pipeline: ScopeClarifier -> LiteratureScout -> TrendSynthesizer -> GapMiner -> DirectionGenerator
    """
    from app.agents.nodes.scope_clarifier import scope_clarifier_node
    from app.agents.nodes.literature_scout import literature_scout_node
    from app.agents.nodes.trend_synthesizer import trend_synthesizer_node
    from app.agents.nodes.gap_miner import gap_miner_node
    from app.agents.nodes.direction_generator import direction_generator_node
    
    # Create graph
    graph = StateGraph(DiscoveryState)
    
    # Add nodes
    graph.add_node("scope_clarifier", scope_clarifier_node)
    graph.add_node("literature_scout", literature_scout_node)
    graph.add_node("trend_synthesizer", trend_synthesizer_node)
    graph.add_node("gap_miner", gap_miner_node)
    graph.add_node("direction_generator", direction_generator_node)
    
    # Define edges
    graph.set_entry_point("scope_clarifier")
    graph.add_edge("scope_clarifier", "literature_scout")
    graph.add_edge("literature_scout", "trend_synthesizer")
    graph.add_edge("trend_synthesizer", "gap_miner")
    graph.add_edge("gap_miner", "direction_generator")
    graph.add_edge("direction_generator", END)
    
    return graph.compile()


def create_deep_dive_graph():
    """
    Create the deep dive agent graph.
    
    Pipeline: DeepDiveScout -> ExperimentDesigner
    """
    from app.agents.nodes.deep_dive_scout import deep_dive_scout_node
    from app.agents.nodes.experiment_designer import experiment_designer_node
    
    # Create graph
    graph = StateGraph(DeepDiveState)
    
    # Add nodes
    graph.add_node("deep_dive_scout", deep_dive_scout_node)
    graph.add_node("experiment_designer", experiment_designer_node)
    
    # Define edges
    graph.set_entry_point("deep_dive_scout")
    graph.add_edge("deep_dive_scout", "experiment_designer")
    graph.add_edge("experiment_designer", END)
    
    return graph.compile()


def create_paper_graph():
    """
    Create the paper drafting agent graph.
    
    Pipeline: PaperWriter -> PaperEditor (optional iteration)
    """
    from app.agents.nodes.paper_writer import paper_writer_node
    from app.agents.nodes.paper_editor import paper_editor_node
    
    # Create graph
    graph = StateGraph(PaperState)
    
    # Add nodes
    graph.add_node("paper_writer", paper_writer_node)
    graph.add_node("paper_editor", paper_editor_node)
    
    # Define edges
    graph.set_entry_point("paper_writer")
    graph.add_edge("paper_writer", "paper_editor")
    graph.add_edge("paper_editor", END)
    
    return graph.compile()
