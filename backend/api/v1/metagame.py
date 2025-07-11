from fastapi import APIRouter, Depends, HTTPException

from services.metagame_service import MetagameService, get_metagame_service

router = APIRouter()


@router.post("/populate-database")
async def populate_database(service: MetagameService = Depends(get_metagame_service)):
    # This endpoint now correctly starts the background task
    return service.start_metagame_update()


@router.get("/status")
async def get_status(service: MetagameService = Depends(get_metagame_service)):
    return service.get_task_status()


@router.get("/formats")
async def get_formats(service: MetagameService = Depends(get_metagame_service)):
    """
    Returns a list of all distinct game formats available in the database.
    """
    try:
        formats = await service.get_available_formats()
        return {"formats": formats}
    except Exception as e:
        # In a real app, you'd have more specific error handling
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{format_name}")
async def get_metagame_analysis(format_name: str, service: MetagameService = Depends(get_metagame_service)):
    """
    Returns a full metagame analysis for a given format.
    """
    try:
        analysis = await service.get_metagame_analysis(format_name)
        if not analysis:
            raise HTTPException(status_code=404, detail=f"No data found for format: {format_name}")
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 