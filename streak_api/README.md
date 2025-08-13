# Streak API

A FastAPI-based REST API for managing streak.txt files.

## Features

- **GET /api/v1/streaks** - List all streaks from .txt files
- **GET /api/v1/streaks/{name}** - Get specific streak details
- **POST /api/v1/streaks** - Create a new streak
- **PUT /api/v1/streaks/{name}** - Update streak metadata
- **DELETE /api/v1/streaks/{name}** - Delete a streak
- **POST /api/v1/streaks/{name}/tick** - Add today's tick to a streak
- **POST /api/v1/streaks/{name}/ticks** - Add a custom tick to a streak
- **GET /api/v1/streaks/{name}/stats** - Get streak statistics

## Running the API

### Option 1: Using the startup script
```bash
python run_api.py
```

### Option 2: Using uvicorn directly
```bash
uvicorn streak_api.main:app --reload
```

The API will be available at:
- **Main API**: http://localhost:8000
- **Interactive Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Testing the API

Run the test script to verify basic functionality:
```bash
python test_api.py
```

## API Usage Examples

### Create a new streak
```bash
curl -X POST "http://localhost:8000/api/v1/streaks" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "exercise",
       "tick_type": "Daily",
       "description": "Daily exercise routine"
     }'
```

### Add today's tick
```bash
curl -X POST "http://localhost:8000/api/v1/streaks/exercise/tick"
```

### Get all streaks
```bash
curl "http://localhost:8000/api/v1/streaks"
```

### Get specific streak
```bash
curl "http://localhost:8000/api/v1/streaks/exercise"
```

## File Integration

The API works directly with .txt files in the current directory:
- Each streak is stored as `{name}.txt`
- Files are loaded/saved using the existing `streak_core.file_operations` module
- All existing streak.txt files are automatically accessible via the API

## Dependencies

The API uses your existing dependencies from `requirements.txt`:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `python-multipart` - For form data support

All streak logic is handled by your existing `streak_core` module.
