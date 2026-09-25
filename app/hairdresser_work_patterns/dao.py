from app.hairdresser_work_patterns.models import HairdresserWorkPatterns
from app.dao.base import BaseDao
from sqlalchemy.orm import selectinload

class HairdresserWorkPatternsDao(BaseDao):
    model = HairdresserWorkPatterns
    _load_options = [
        selectinload(HairdresserWorkPatterns.hairdresser),
        selectinload(HairdresserWorkPatterns.salon),
        selectinload(HairdresserWorkPatterns.schedules),
    ]
