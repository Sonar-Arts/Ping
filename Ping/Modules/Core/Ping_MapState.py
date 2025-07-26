"""
Ping Map State Module
Manages persistent state for the roguelike map system.
"""

import json
import os
from typing import Optional, Dict, Any
from .Ping_MapTree import MapTreeManager, MapZone, MapNode

class MapStateManager:
    """Manages the persistent state of the map progression system."""
    
    def __init__(self, save_directory: str = "Ping/Game Parameters/"):
        self.save_directory = save_directory
        self.map_progress_file = os.path.join(save_directory, "map_progress.json")
        self.player_stats_file = os.path.join(save_directory, "player_stats.json")
        
        # Ensure save directory exists
        os.makedirs(save_directory, exist_ok=True)
        
        self.map_manager = MapTreeManager(self.map_progress_file)
        self.player_stats = {
            "currency": 0,
            "upgrades_purchased": [],
            "levels_completed": 0,
            "total_score": 0,
            "best_streak": 0
        }
        
    def initialize_new_run(self):
        """Start a completely new campaign run."""
        # Reset player stats
        self.player_stats = {
            "currency": 0,
            "upgrades_purchased": [],
            "levels_completed": 0,
            "total_score": 0,
            "best_streak": 0
        }
        
        # Generate new map tree
        self.map_manager.generate_new_run()
        
        # Save both map progress and player stats
        self.save_all_data()
        
    def continue_existing_run(self) -> bool:
        """Load and continue an existing run. Returns True if successful."""
        map_loaded = self.map_manager.load_progress()
        stats_loaded = self.load_player_stats()
        
        return map_loaded and stats_loaded
    
    def has_existing_run(self) -> bool:
        """Check if there's an existing run to continue."""
        return (os.path.exists(self.map_progress_file) and 
                os.path.exists(self.player_stats_file))
    
    def get_current_zone(self) -> Optional[MapZone]:
        """Get the current active zone."""
        return self.map_manager.get_current_zone()
    
    def get_current_node(self) -> Optional[MapNode]:
        """Get the current player position node."""
        zone = self.get_current_zone()
        if zone and zone.current_node_id:
            return zone.get_node(zone.current_node_id)
        return None
    
    def complete_current_level(self, score: int, performance_bonus: int = 0):
        """Mark the current level as completed and award currency."""
        zone = self.get_current_zone()
        current_node = self.get_current_node()
        
        if zone and current_node:
            # Mark node as completed
            zone.complete_node(current_node.id)
            
            # Update player stats
            self.player_stats["levels_completed"] += 1
            self.player_stats["total_score"] += score
            
            # Award currency based on score
            currency_earned = self.calculate_currency_reward(score, performance_bonus)
            self.player_stats["currency"] += currency_earned
            
            # Save progress
            self.save_all_data()
            
            return currency_earned
        
        return 0
    
    def calculate_currency_reward(self, score: int, performance_bonus: int = 0) -> int:
        """Calculate currency reward based on level performance."""
        base_reward = max(10, score // 100)  # Minimum 10, scale with score
        bonus_reward = performance_bonus
        total_reward = base_reward + bonus_reward
        
        return total_reward
    
    def move_to_node(self, node_id: str) -> bool:
        """Move player to a specific node if accessible."""
        zone = self.get_current_zone()
        if zone:
            target_node = zone.get_node(node_id)
            if target_node and target_node.is_accessible:
                zone.set_current_node(node_id)
                self.save_all_data()
                return True
        return False
    
    def can_access_node(self, node_id: str) -> bool:
        """Check if a node is accessible to the player."""
        zone = self.get_current_zone()
        if zone:
            node = zone.get_node(node_id)
            return node and node.is_accessible and not node.is_completed
        return False
    
    def get_available_nodes(self) -> list:
        """Get all nodes the player can currently access."""
        zone = self.get_current_zone()
        if zone:
            return zone.get_available_nodes()
        return []
    
    def purchase_upgrade(self, upgrade_id: str, cost: int) -> bool:
        """Purchase an upgrade if player has enough currency."""
        if self.player_stats["currency"] >= cost:
            self.player_stats["currency"] -= cost
            if upgrade_id not in self.player_stats["upgrades_purchased"]:
                self.player_stats["upgrades_purchased"].append(upgrade_id)
            self.save_all_data()
            return True
        return False
    
    def get_player_currency(self) -> int:
        """Get player's current currency."""
        return self.player_stats["currency"]
    
    def get_player_stats(self) -> Dict[str, Any]:
        """Get complete player statistics."""
        return self.player_stats.copy()
    
    def has_upgrade(self, upgrade_id: str) -> bool:
        """Check if player has purchased a specific upgrade."""
        return upgrade_id in self.player_stats["upgrades_purchased"]
    
    def save_all_data(self):
        """Save both map progress and player stats."""
        self.map_manager.save_progress()
        self.save_player_stats()
    
    def save_player_stats(self):
        """Save player statistics to file."""
        try:
            with open(self.player_stats_file, 'w') as f:
                json.dump(self.player_stats, f, indent=2)
        except Exception as e:
            print(f"Error saving player stats: {e}")
    
    def load_player_stats(self) -> bool:
        """Load player statistics from file. Returns True if successful."""
        try:
            with open(self.player_stats_file, 'r') as f:
                self.player_stats = json.load(f)
            return True
        except FileNotFoundError:
            # No save file exists yet
            return False
        except Exception as e:
            print(f"Error loading player stats: {e}")
            return False
    
    def get_zone_progress(self) -> Dict[str, Any]:
        """Get detailed progress information for the current zone."""
        zone = self.get_current_zone()
        if not zone:
            return {}
        
        total_nodes = len(zone.nodes)
        completed_nodes = sum(1 for node in zone.nodes.values() if node.is_completed)
        accessible_nodes = sum(1 for node in zone.nodes.values() if node.is_accessible)
        
        return {
            "zone_name": zone.name,
            "total_nodes": total_nodes,
            "completed_nodes": completed_nodes,
            "accessible_nodes": accessible_nodes,
            "completion_percentage": (completed_nodes / total_nodes) * 100 if total_nodes > 0 else 0,
            "current_node_id": zone.current_node_id
        }
    
    def reset_run(self):
        """Reset the current run (for debugging or starting over)."""
        self.initialize_new_run()
    
    def export_progress_data(self) -> Dict[str, Any]:
        """Export all progress data for debugging or backup."""
        zone = self.get_current_zone()
        return {
            "player_stats": self.player_stats,
            "zone_data": zone.to_dict() if zone else None,
            "zone_progress": self.get_zone_progress()
        }

# Global instance for easy access throughout the game
_map_state_instance = None

def get_map_state() -> MapStateManager:
    """Get the global map state manager instance."""
    global _map_state_instance
    if _map_state_instance is None:
        _map_state_instance = MapStateManager()
    return _map_state_instance

def initialize_map_state(save_directory: str = "Ping/Game Parameters/") -> MapStateManager:
    """Initialize the global map state manager with a specific save directory."""
    global _map_state_instance
    _map_state_instance = MapStateManager(save_directory)
    return _map_state_instance