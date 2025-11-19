from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
from datetime import datetime, timedelta
import pytz

from cache import rd, update_cache
from classroom_availability import get_classroom_availability
from config import CACHE_EXPIRY, BUILDINGS, CLASSROOMS, REFRESH_COOLDOWN_MINUTES

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

def should_refresh_on_wake():
    try:
        last_refresh_key = 'classrooms:last_refresh'
        last_refresh_str = rd.get(last_refresh_key)
        
        if not last_refresh_str:
            return True  # No previous refresh, should refresh
        
        last_refresh = datetime.fromisoformat(last_refresh_str)
        now = datetime.now(pytz.timezone('America/New_York'))
        
        # Refresh if data not fetched today
        return last_refresh.date() < now.date()
        
    except Exception as e:
        print(f'Error checking if should refresh on wake: {str(e)}')
        return True  # Default to refreshing on error

@app.on_event('startup')
async def startup_event():
    # Wait for Redis to be ready
    for i in range(5):
        try:
            rd.ping()
            print('Redis connection established')
            break
        except Exception:
            print(f'Waiting for Redis to be ready... (attempt {i+1}/5)')
            await asyncio.sleep(1)

    try:
        print('App starting up - checking if refresh is needed')
        
        # Check if refresh needed
        if should_refresh_on_wake():
            print('App was sleeping or no recent data - fetching fresh data')
            await update_cache()
            
            # Set refresh timestamp
            now = datetime.now(pytz.timezone('America/New_York'))
            rd.set('classrooms:last_refresh', now.isoformat(), ex=CACHE_EXPIRY)
            print('Wake-up refresh completed successfully')
        else:
            print('Recent data available, skipping wake-up refresh')
            
    except Exception as e:
        print(f'Failed to handle wake-up refresh: {str(e)}')

@app.get('/')
async def root():
    return 'Hello World'

@app.post('/api/refresh')
async def refresh_data():
    try:
        # Check if in cooldown period
        last_refresh_key = 'classrooms:last_refresh'
        last_refresh_str = rd.get(last_refresh_key)
        
        if last_refresh_str:
            last_refresh = datetime.fromisoformat(last_refresh_str)
            now = datetime.now(pytz.timezone('America/New_York'))
            time_since_refresh = now - last_refresh
            
            if time_since_refresh < timedelta(minutes=REFRESH_COOLDOWN_MINUTES):
                remaining_minutes = REFRESH_COOLDOWN_MINUTES - (time_since_refresh.total_seconds() / 60)
                raise HTTPException(
                    status_code=429, 
                    detail=f"Refresh cooldown active. Please wait {remaining_minutes:.1f} more minutes."
                )
        
        # Update cache
        await update_cache()
        
        # Update last refresh timestamp
        now = datetime.now(pytz.timezone('America/New_York'))
        rd.set(last_refresh_key, now.isoformat(), ex=CACHE_EXPIRY)
        
        return {"message": "Data refreshed successfully", "timestamp": now.isoformat()}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f'Error refreshing data: {str(e)}')
        raise HTTPException(status_code=500, detail="Failed to refresh data")

@app.get('/api/last-updated')
async def get_last_updated():
    try:
        last_refresh_key = 'classrooms:last_refresh'
        last_refresh_str = rd.get(last_refresh_key)
        
        if last_refresh_str:
            last_refresh = datetime.fromisoformat(last_refresh_str)
            return {"last_updated": last_refresh.isoformat()}
        else:
            return {"last_updated": None}
            
    except Exception as e:
        print(f'Error getting last updated timestamp: {str(e)}')
        return {"last_updated": None}

@app.get('/api/cooldown-status')
async def get_cooldown_status():
    try:
        last_refresh_key = 'classrooms:last_refresh'
        last_refresh_str = rd.get(last_refresh_key)
        
        if last_refresh_str:
            last_refresh = datetime.fromisoformat(last_refresh_str)
            now = datetime.now(pytz.timezone('America/New_York'))
            time_since_refresh = now - last_refresh
            
            if time_since_refresh < timedelta(minutes=REFRESH_COOLDOWN_MINUTES):
                remaining_minutes = REFRESH_COOLDOWN_MINUTES - (time_since_refresh.total_seconds() / 60)
                return {"in_cooldown": True, "remaining_minutes": remaining_minutes}
            else:
                return {"in_cooldown": False, "remaining_minutes": 0}
        else:
            return {"in_cooldown": False, "remaining_minutes": 0}
            
    except Exception as e:
        print(f'Error getting cooldown status: {str(e)}')
        return {"in_cooldown": False, "remaining_minutes": 0}

@app.get('/api/open-classrooms')
async def get_classroom_availability_by_building():
    try:
        # Check cache first
        cache = rd.get('classrooms:availability')
        
        if cache:
            print('Cache hit')
            availability_data = json.loads(cache)
        else:
            print('Cache miss - fetching new data')
            availability_data = await get_classroom_availability()
            rd.set('classrooms:availability', json.dumps(availability_data), ex=CACHE_EXPIRY)
            
            # Update last refresh timestamp when fetching new data
            now = datetime.now(pytz.timezone('America/New_York'))
            rd.set('classrooms:last_refresh', now.isoformat(), ex=CACHE_EXPIRY)

        # Organize response by building
        res = {}
        for building_code, building_data in BUILDINGS.items():
            res[building_code] = {
                "code": building_data["code"],
                "name": building_data["name"],
                "classrooms": []
            }
        
        # Add classroom data to buildings
        for classroom_id, classroom_data in CLASSROOMS.items():
            building_code = classroom_data["building_code"]
            if building_code in res:
                res[building_code]["classrooms"].append({
                    "id": classroom_data["id"],
                    "name": classroom_data["name"],
                    "availability": availability_data.get(classroom_id, [])
                })
        
        # Add last updated timestamp
        last_refresh_key = 'classrooms:last_refresh'
        last_refresh_str = rd.get(last_refresh_key)
        last_updated = None
        if last_refresh_str:
            last_updated = datetime.fromisoformat(last_refresh_str).isoformat()
        
        return {
            "buildings": res,
            "last_updated": last_updated
        }

    except Exception as e:
        print(f'Error getting classroom availability: {str(e)}')
        return {}