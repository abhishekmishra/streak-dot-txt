"""
Streak API endpoints
"""

import os
import glob
from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Path
from streak_api.schemas import (
    StreakResponse,
    StreakCreate,
    StreakUpdate,
    TickCreate,
    StatusResponse,
)
from streak_core.models import Streak, DailyTick
from streak_core.file_operations import StreakFileManager
from streak_core.constants import DEFAULT_STREAKS_DIR

router = APIRouter()

# Use the default streaks directory, but allow override via environment variable
STREAKS_DIRECTORY = os.getenv("STREAKS_DIR", DEFAULT_STREAKS_DIR)


def get_streak_files():
    """Get all streak files in the streaks directory"""
    return StreakFileManager.list_streak_files(STREAKS_DIRECTORY)


def load_streak_from_file(filename: str) -> Streak:
    """Load a streak from a file"""
    # If filename doesn't contain a path, construct the full path
    if not os.path.dirname(filename):
        full_path = os.path.join(STREAKS_DIRECTORY, f"streak-{filename}.txt")
    else:
        full_path = filename

    if not os.path.exists(full_path):
        raise HTTPException(
            status_code=404, detail=f"Streak file {full_path} not found"
        )

    try:
        streak = StreakFileManager.load_from_file(full_path)
        return streak
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading streak: {str(e)}")


def save_streak_to_file(streak: Streak, filename: str):
    """Save a streak to a file"""
    # If filename doesn't contain a path, construct the full path
    if not os.path.dirname(filename):
        full_path = os.path.join(STREAKS_DIRECTORY, f"streak-{filename}.txt")
    else:
        full_path = filename

    try:
        StreakFileManager.save_to_file(streak, full_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving streak: {str(e)}")


@router.get("/streaks", response_model=List[StreakResponse])
async def get_all_streaks():
    """Get all streaks from streak files in the streaks directory"""
    try:
        streak_files = get_streak_files()
        streaks = []

        for filepath in streak_files:
            try:
                streak = StreakFileManager.load_from_file(filepath)
                streaks.append(StreakResponse.from_streak(streak))
            except Exception as e:
                # Log error but continue with other files
                print(f"Error loading {filepath}: {e}")
                continue

        return streaks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/streaks/{streak_name}", response_model=StreakResponse)
async def get_streak(
    streak_name: str = Path(
        ..., description="Name of the streak (will look for streak-{name}.txt)"
    )
):
    """Get a specific streak by name"""
    streak = load_streak_from_file(streak_name)
    return StreakResponse.from_streak(streak)


@router.post("/streaks", response_model=StreakResponse)
async def create_streak(streak_data: StreakCreate):
    """Create a new streak"""
    try:
        # Use the StreakFileManager to create the file with proper naming
        created_file = StreakFileManager.create_new_streak_file(
            STREAKS_DIRECTORY, streak_data.name, streak_data.tick_type
        )

        # Load the created streak and update with additional metadata
        streak = StreakFileManager.load_from_file(created_file)
        if streak_data.description:
            streak.set_metadata("description", streak_data.description)
            StreakFileManager.save_to_file(streak, created_file)

        return StreakResponse.from_streak(streak)
    except FileExistsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/streaks/{streak_name}/tick", response_model=StatusResponse)
async def add_tick_today(
    streak_name: str = Path(..., description="Name of the streak")
):
    """Add a tick for today to the specified streak"""
    streak = load_streak_from_file(streak_name)

    try:
        success = streak.mark_today()
        if success:
            save_streak_to_file(streak, streak_name)
            return StatusResponse(message=f"Today's tick added to {streak_name}")
        else:
            return StatusResponse(
                message=f"Today already ticked for {streak_name}", success=False
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/streaks/{streak_name}/ticks", response_model=StatusResponse)
async def add_custom_tick(streak_name: str, tick_data: TickCreate):
    """Add a custom tick to the specified streak"""
    streak = load_streak_from_file(streak_name)

    try:
        streak.add_tick(tick_data.tick_datetime_str)
        save_streak_to_file(streak, streak_name)
        return StatusResponse(message=f"Tick added to {streak_name}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/streaks/{streak_name}", response_model=StreakResponse)
async def update_streak(streak_name: str, streak_update: StreakUpdate):
    """Update streak metadata"""
    streak = load_streak_from_file(streak_name)

    try:
        if streak_update.description is not None:
            streak.set_metadata("description", streak_update.description)
        if streak_update.tick_type is not None:
            streak.set_metadata("tick", streak_update.tick_type)

        save_streak_to_file(streak, streak_name)
        return StreakResponse.from_streak(streak)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/streaks/{streak_name}", response_model=StatusResponse)
async def delete_streak(streak_name: str):
    """Delete a streak file"""
    # Construct the full path to the streak file
    full_path = os.path.join(STREAKS_DIRECTORY, f"streak-{streak_name}.txt")

    if not os.path.exists(full_path):
        raise HTTPException(
            status_code=404, detail=f"Streak file not found for {streak_name}"
        )

    try:
        os.remove(full_path)
        return StatusResponse(message=f"Streak {streak_name} deleted")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting streak: {str(e)}")


@router.get("/streaks/{streak_name}/stats")
async def get_streak_stats(streak_name: str):
    """Get statistics for a specific streak"""
    streak = load_streak_from_file(streak_name)

    return {
        "name": streak.name,
        "stats": streak.stats,
        "years": streak.get_years(),
        "total_ticks": len(streak.ticks),
        "tick_type": streak.tick,
    }


@router.get("/config")
async def get_config():
    """Get API configuration including streaks directory"""
    return {
        "streaks_directory": STREAKS_DIRECTORY,
        "directory_exists": os.path.exists(STREAKS_DIRECTORY),
        "total_streak_files": (
            len(get_streak_files()) if os.path.exists(STREAKS_DIRECTORY) else 0
        ),
    }
