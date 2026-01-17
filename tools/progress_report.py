"""
Progress report generation tool.

Generates a CSV file with exercise progress data for tracking
user's fitness improvements over time.
"""

import os
import csv
from datetime import datetime, timedelta
from typing import Dict, Any


def generate_progress_report() -> Dict[str, Any]:
    """
    Generate a progress report CSV file with sample exercise data.
    
    Returns:
        Dictionary with status and message about the generated report
    """
    # Create outputs directory if it doesn't exist
    os.makedirs("outputs", exist_ok=True)
    
    # Generate sample progress data
    progress_data = _create_sample_progress_data()
    
    # Write to CSV file with simple format
    output_path = "outputs/progress_report.csv"
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Exercise", "Value"])
        writer.writeheader()
        writer.writerows(progress_data)
    
    return {
        "status": "success",
        "message": f"Progress report generated successfully and saved to {output_path}",
        "file_path": output_path,
        "records": len(progress_data)
    }


def _create_sample_progress_data() -> list:
    """
    Create sample progress data in simple format: Exercise, Value.
    Format matches user requirements: pushups, 25, leg raises, 7, cardio, 45 min, etc.
    
    Returns:
        List of dictionaries containing exercise progress records
    """
    # Simple format: Exercise name and current progress value
    # Based on user example: "pushups, 25, leg raises, 7, cardio, 45 min"
    data = [
        {"Exercise": "Push-ups", "Value": "25"},
        {"Exercise": "Leg Raises", "Value": "7"},
        {"Exercise": "Cardio", "Value": "45 min"},
        {"Exercise": "Squats", "Value": "20"},
        {"Exercise": "Pull-ups", "Value": "8"},
        {"Exercise": "Plank", "Value": "60 sec"},
    ]
    
    return data
