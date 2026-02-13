"""
Save and load EDA analysis results.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class ResultsSaver:
    """Saves and loads EDA analysis results."""

    @staticmethod
    def _convert_to_serializable(obj: Any) -> Any:
        """
        Convert non-JSON-serializable objects to serializable format.

        Args:
            obj: Object to convert

        Returns:
            JSON-serializable version of the object
        """
        if isinstance(obj, dict):
            return {str(k): ResultsSaver._convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [ResultsSaver._convert_to_serializable(item) for item in obj]
        elif hasattr(obj, 'isoformat'):  # DateTime objects
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):  # Custom objects
            return str(obj)
        else:
            return obj

    @staticmethod
    def save_analysis_results(
        results: Dict[str, Dict],
        config: Dict,
        output_dir: str = ".",
        filename: Optional[str] = None
    ) -> str:
        """
        Save analysis results to a JSON file.
        
        Args:
            results: Dictionary of {label: {property: analysis}} from EDA
            config: Configuration used for the analysis
            output_dir: Directory to save results
            filename: Optional filename, auto-generated if None
            
        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"eda_results_{timestamp}.json"
        
        output_path = Path(output_dir) / filename

        # Prepare data structure and convert to serializable format
        data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "config": config
            },
            "results": results
        }

        # Convert to serializable format
        serializable_data = ResultsSaver._convert_to_serializable(data)

        # Save to JSON
        with open(output_path, 'w') as f:
            json.dump(serializable_data, f, indent=2)
        
        print(f"\nEDA results saved to: {output_path}")
        return str(output_path)
    
    @staticmethod
    def load_analysis_results(filepath: str) -> Dict:
        """
        Load analysis results from a JSON file.
        
        Args:
            filepath: Path to the results file
            
        Returns:
            Dictionary with metadata and results
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        return data
    
    @staticmethod
    def get_identifiers(
        results: Dict[str, Dict],
        node_label: str,
        include_semi_unique: bool = True
    ) -> List[str]:
        """
        Extract identifier properties (UNIQUE or SEMI_UNIQUE) for a node label.
        
        Args:
            results: EDA results dictionary
            node_label: Node label to get identifiers for
            include_semi_unique: Whether to include SEMI_UNIQUE properties
            
        Returns:
            List of property names that are identifiers
        """
        if node_label not in results:
            return []
        
        identifiers = []
        properties = results[node_label]
        
        for prop_name, prop_info in properties.items():
            prop_type = prop_info.get('type', '')
            
            if prop_type == 'UNIQUE':
                identifiers.append(prop_name)
            elif include_semi_unique and prop_type == 'SEMI_UNIQUE':
                identifiers.append(prop_name)
        
        return identifiers
    
    @staticmethod
    def get_categorical_properties(
        results: Dict[str, Dict],
        node_label: str,
        include_highly_categorical: bool = True
    ) -> List[str]:
        """
        Extract categorical properties for a node label.
        
        Args:
            results: EDA results dictionary
            node_label: Node label to get categorical properties for
            include_highly_categorical: Whether to include HIGHLY_CATEGORICAL
            
        Returns:
            List of property names that are categorical
        """
        if node_label not in results:
            return []
        
        categorical = []
        properties = results[node_label]
        
        for prop_name, prop_info in properties.items():
            prop_type = prop_info.get('type', '')
            
            if prop_type == 'CATEGORICAL':
                categorical.append(prop_name)
            elif include_highly_categorical and prop_type == 'HIGHLY_CATEGORICAL':
                categorical.append(prop_name)
        
        return categorical
    
    @staticmethod
    def find_latest_results(directory: str = ".") -> Optional[str]:
        """
        Find the most recent EDA results file in a directory.
        
        Args:
            directory: Directory to search
            
        Returns:
            Path to latest results file, or None if not found
        """
        results_dir = Path(directory)
        results_files = list(results_dir.glob("eda_results_*.json"))
        
        if not results_files:
            return None
        
        # Sort by modification time, most recent first
        latest = max(results_files, key=lambda p: p.stat().st_mtime)
        return str(latest)

