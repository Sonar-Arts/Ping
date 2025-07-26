"""
Ping Map Tree Module
Manages the roguelike map tree system for campaign zones.
"""

import random
import json
from enum import Enum
from typing import List, Dict, Optional, Tuple

class NodeType(Enum):
    START = "start"
    LEVEL = "level"
    SHOP = "shop"
    BOSS = "boss"
    CONVERGENCE = "convergence"

class MapNode:
    """Represents a single node in the map tree."""
    
    def __init__(self, node_id: str, node_type: NodeType, position: Tuple[int, int]):
        self.id = node_id
        self.type = node_type
        self.position = position  # (x, y) coordinates for display
        self.connections: List[str] = []  # IDs of connected nodes
        self.level_file = None  # PMF file for level nodes
        self.is_completed = False
        self.is_accessible = False
        self.properties = {}  # Additional node-specific data
        
    def add_connection(self, node_id: str):
        """Add a connection to another node."""
        if node_id not in self.connections:
            self.connections.append(node_id)
    
    def to_dict(self):
        """Convert node to dictionary for serialization."""
        return {
            'id': self.id,
            'type': self.type.value,
            'position': self.position,
            'connections': self.connections,
            'level_file': self.level_file,
            'is_completed': self.is_completed,
            'is_accessible': self.is_accessible,
            'properties': self.properties
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create node from dictionary."""
        node = cls(
            data['id'],
            NodeType(data['type']),
            tuple(data['position'])
        )
        node.connections = data.get('connections', [])
        node.level_file = data.get('level_file')
        node.is_completed = data.get('is_completed', False)
        node.is_accessible = data.get('is_accessible', False)
        node.properties = data.get('properties', {})
        return node

class MapZone:
    """Represents a complete zone with branching paths."""
    
    def __init__(self, zone_name: str, zone_id: str):
        self.name = zone_name
        self.id = zone_id
        self.nodes: Dict[str, MapNode] = {}
        self.current_node_id = None
        self.music_file = None
        self.background_theme = "sewer"
        
    def add_node(self, node: MapNode):
        """Add a node to the zone."""
        self.nodes[node.id] = node
        
    def get_node(self, node_id: str) -> Optional[MapNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)
    
    def get_available_nodes(self) -> List[MapNode]:
        """Get all accessible nodes that aren't completed."""
        return [node for node in self.nodes.values() 
                if node.is_accessible and not node.is_completed]
    
    def complete_node(self, node_id: str):
        """Mark a node as completed and unlock connected nodes."""
        node = self.get_node(node_id)
        if node:
            node.is_completed = True
            # Unlock connected nodes
            for connection_id in node.connections:
                connected_node = self.get_node(connection_id)
                if connected_node:
                    connected_node.is_accessible = True
    
    def set_current_node(self, node_id: str):
        """Set the current player position."""
        if node_id in self.nodes:
            self.current_node_id = node_id
    
    def to_dict(self):
        """Convert zone to dictionary for serialization."""
        return {
            'name': self.name,
            'id': self.id,
            'nodes': {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            'current_node_id': self.current_node_id,
            'music_file': self.music_file,
            'background_theme': self.background_theme
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create zone from dictionary."""
        zone = cls(data['name'], data['id'])
        zone.current_node_id = data.get('current_node_id')
        zone.music_file = data.get('music_file')
        zone.background_theme = data.get('background_theme', 'sewer')
        
        # Load nodes
        for node_data in data.get('nodes', {}).values():
            node = MapNode.from_dict(node_data)
            zone.add_node(node)
        
        return zone

class MapTreeGenerator:
    """Generates randomized map trees for zones."""
    
    @staticmethod
    def generate_new_arkadia_sewerlines() -> MapZone:
        """Generate the New Arkadia Sewerlines zone."""
        zone = MapZone("New Arkadia Sewerlines", "new_arkadia_sewerlines")
        zone.music_file = "New Arkadia Sewerlines"
        zone.background_theme = "sewer"
        
        # Available level files (using existing files as placeholders)
        available_levels = [
            "Debug Level.pmf",
            "Spooky Test.pmf", 
            "Roulette Test.pmf",
            "Debug Level.pmf",  # Reuse for now since we have limited levels
            "Spooky Test.pmf",
            "Roulette Test.pmf"
        ]
        
        # Create start node
        start_node = MapNode("start", NodeType.START, (400, 50))
        start_node.level_file = "Manhole Mayhem.pmf"  # Fixed first level
        start_node.is_accessible = True
        zone.add_node(start_node)
        zone.set_current_node("start")
        
        # Create two branching paths
        path_1_nodes = []
        path_2_nodes = []
        
        # Generate Path 1 (left branch)
        path_1_x_positions = [200, 150, 100]
        path_1_y_positions = [150, 250, 350]
        
        for i in range(3):
            node_id = f"path1_node{i+1}"
            node_type = NodeType.SHOP if i == 1 else NodeType.LEVEL  # Middle node is shop
            position = (path_1_x_positions[i], path_1_y_positions[i])
            
            node = MapNode(node_id, node_type, position)
            if node_type == NodeType.LEVEL:
                node.level_file = random.choice(available_levels)
                # Allow reuse since we have limited level files available
            
            path_1_nodes.append(node)
            zone.add_node(node)
        
        # Generate Path 2 (right branch)
        path_2_x_positions = [600, 650, 700]
        path_2_y_positions = [150, 250, 350]
        
        for i in range(3):
            node_id = f"path2_node{i+1}"
            node_type = NodeType.SHOP if i == 2 else NodeType.LEVEL  # Last node is shop
            position = (path_2_x_positions[i], path_2_y_positions[i])
            
            node = MapNode(node_id, node_type, position)
            if node_type == NodeType.LEVEL:
                node.level_file = random.choice(available_levels)
                # Allow reuse since we have limited level files available
                
            path_2_nodes.append(node)
            zone.add_node(node)
        
        # Create convergence/boss node
        boss_node = MapNode("boss", NodeType.BOSS, (400, 450))
        boss_node.level_file = "Manhole Mayhem.pmf"  # Use existing level as placeholder
        zone.add_node(boss_node)
        
        # Connect start to both path starts
        start_node.add_connection(path_1_nodes[0].id)
        start_node.add_connection(path_2_nodes[0].id)
        
        # Connect path 1 nodes sequentially
        for i in range(len(path_1_nodes) - 1):
            path_1_nodes[i].add_connection(path_1_nodes[i + 1].id)
        
        # Connect path 2 nodes sequentially  
        for i in range(len(path_2_nodes) - 1):
            path_2_nodes[i].add_connection(path_2_nodes[i + 1].id)
        
        # Connect both paths to boss
        path_1_nodes[-1].add_connection(boss_node.id)
        path_2_nodes[-1].add_connection(boss_node.id)
        
        return zone

class MapTreeManager:
    """Manages multiple zones and save/load functionality."""
    
    def __init__(self, save_file_path: str = "Ping/Game Parameters/map_progress.json"):
        self.save_file_path = save_file_path
        self.zones: Dict[str, MapZone] = {}
        self.current_zone_id = None
        
    def add_zone(self, zone: MapZone):
        """Add a zone to the manager."""
        self.zones[zone.id] = zone
        
    def get_zone(self, zone_id: str) -> Optional[MapZone]:
        """Get a zone by ID."""
        return self.zones.get(zone_id)
    
    def set_current_zone(self, zone_id: str):
        """Set the active zone."""
        if zone_id in self.zones:
            self.current_zone_id = zone_id
    
    def get_current_zone(self) -> Optional[MapZone]:
        """Get the currently active zone."""
        if self.current_zone_id:
            return self.zones.get(self.current_zone_id)
        return None
    
    def generate_new_run(self):
        """Generate a fresh map tree for a new run."""
        # Clear existing zones
        self.zones.clear()
        
        # Generate New Arkadia Sewerlines
        sewerlines = MapTreeGenerator.generate_new_arkadia_sewerlines()
        self.add_zone(sewerlines)
        self.set_current_zone(sewerlines.id)
        
        # Save the new run
        self.save_progress()
    
    def save_progress(self):
        """Save current progress to file."""
        try:
            save_data = {
                'zones': {zone_id: zone.to_dict() for zone_id, zone in self.zones.items()},
                'current_zone_id': self.current_zone_id
            }
            
            with open(self.save_file_path, 'w') as f:
                json.dump(save_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving map progress: {e}")
    
    def load_progress(self) -> bool:
        """Load progress from file. Returns True if successful."""
        try:
            with open(self.save_file_path, 'r') as f:
                save_data = json.load(f)
            
            # Load zones
            self.zones.clear()
            for zone_data in save_data.get('zones', {}).values():
                zone = MapZone.from_dict(zone_data)
                self.add_zone(zone)
            
            self.current_zone_id = save_data.get('current_zone_id')
            return True
            
        except FileNotFoundError:
            # No save file exists yet
            return False
        except Exception as e:
            print(f"Error loading map progress: {e}")
            return False