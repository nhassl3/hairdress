from datetime import time, date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.exceptions import NotFoundElement, NoFieldsToUpdate, AlreadyExistsElement, UserHasBookings
from app.hairdresser_work_patterns.dao import HairdresserWorkPatternsDao
from app.hairdresser_work_patterns.models import HairdresserWorkPatterns
from app.hairdresser_work_patterns.schemas import AdminHairdresserWorkPatterns, CreateHairdresserWorkPatterns, \
    UpdateHairdresserWorkPatterns


router = APIRouter(
    prefix="/admin",
    tags=["HairdresserWorkPatterns"]
)

@router.get( "/HairdresserWorkPatterns", response_model=list[AdminHairdresserWorkPatterns])
async def get_all_hairdressers_work_patterns(skip: int = 0, limit: int = 100):
    return await HairdresserWorkPatternsDao.find_all(skip=skip, limit=limit)

@router.get('/HairdresserWorkPatterns_filter/', response_model=list[AdminHairdresserWorkPatterns])
async def get_filter_hairdressers_work_patterns(id:Optional[int]=None,
                                                hairdresser_id: UUID | None = None,
                                                salon_id:Optional[int]=None,
                                                weekday:Optional[int]=None,
                                                shift_start:Optional[time]=None,
                                                shift_end:Optional[time]=None,
                                                effective_from:Optional[date]=None,
                                                effective_to:Optional[date]=None,
                                                skip: int = 0, limit: int = 100
                                                ):

    filters = {}
    if id:
        filters['id'] = id
    if hairdresser_id:
        filters['hairdresser_id'] = hairdresser_id
    if salon_id:
        filters['salon_id'] = salon_id
    if weekday:
        filters['weekday'] = weekday
    if shift_start:
        filters['shift_start'] = shift_start
    if shift_end:
        filters['shift_end'] = shift_end
    if effective_from:
        filters['effective_from'] = effective_from
    if effective_to:
        filters['effective_to'] = effective_to

    if filters:
        HairdresserWorkPatterns = await HairdresserWorkPatternsDao.find_by_filter(skip=skip, limit=limit, **filters)
    else:
        HairdresserWorkPatterns = await HairdresserWorkPatternsDao.find_all(skip=skip, limit=limit)

    return HairdresserWorkPatterns


@router.post('/HairdresserWorkPatterns/' , response_model=AdminHairdresserWorkPatterns, status_code=201)
async def create_hairdresser_work_pattern(HairdresserWorkPatterns: CreateHairdresserWorkPatterns):
    try:
        new_hairdresserworkpatterns = await HairdresserWorkPatternsDao.add(**HairdresserWorkPatterns.model_dump())
        return new_hairdresserworkpatterns
    except IntegrityError:
        raise AlreadyExistsElement

@router.patch('/HairdresserWorkPatterns/{pattern_id}', response_model=AdminHairdresserWorkPatterns)
async def partial_update_work_pattern(
    pattern_id: int,
    data: UpdateHairdresserWorkPatterns,
):
    existing = await HairdresserWorkPatternsDao.find_by_id(pattern_id)
    if not existing:
        raise NotFoundElement

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise NoFieldsToUpdate

    merged_data = {
        "hairdresser_id": existing.hairdresser_id,
        "salon_id": update_data.get("salon_id", existing.salon_id),
        "weekday": update_data.get("weekday", existing.weekday),
        "shift_start": update_data.get("shift_start", existing.shift_start),
        "shift_end": update_data.get("shift_end", existing.shift_end),
        "effective_from": update_data.get("effective_from", existing.effective_from),
        "effective_to": update_data.get("effective_to", existing.effective_to),
    }

    try:
        CreateHairdresserWorkPatterns(**merged_data)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    try:
        return await HairdresserWorkPatternsDao.update(
            filters={"id": pattern_id},
            data=update_data,
        )
    except IntegrityError:
        raise AlreadyExistsElement


@router.delete('/HairdresserWorkPatterns/{pattern_id}')
async def delete_work_pattern(pattern_id: int):
    existing = await HairdresserWorkPatternsDao.find_by_id(pattern_id)
    if not existing:
        raise NotFoundElement

    try:
        await HairdresserWorkPatternsDao.delete_by_id(pattern_id)
        return {"detail": "Deleted successfully"}
    except IntegrityError:
        raise AlreadyExistsElement
