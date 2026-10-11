from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import ApplicationStatus, Job
from .schemas import JobStats, MonthCount

MONTHS_SHOWN = 6


def month_start(day: date, offset: int) -> date:
    index = day.year * 12 + day.month - 1 + offset
    return date(index // 12, index % 12 + 1, 1)


def build_stats(db: Session, user_id: int, today: date | None = None) -> JobStats:
    today = today or date.today()
    first_month = month_start(today, -(MONTHS_SHOWN - 1))
    after_last_month = month_start(today, 1)

    status_rows = db.execute(
        select(Job.status, func.count()).where(Job.user_id == user_id).group_by(Job.status)
    ).all()
    by_status = {status.value: 0 for status in ApplicationStatus}
    for status, count in status_rows:
        by_status[status.value] = count

    month_label = func.to_char(Job.application_date, "YYYY-MM")
    month_rows = db.execute(
        select(month_label, func.count())
        .where(
            Job.user_id == user_id,
            Job.application_date >= first_month,
            Job.application_date < after_last_month,
        )
        .group_by(month_label)
    ).all()
    per_month = {label: count for label, count in month_rows}

    monthly = []
    for offset in range(-(MONTHS_SHOWN - 1), 1):
        label = month_start(today, offset).strftime("%Y-%m")
        monthly.append(MonthCount(month=label, count=per_month.get(label, 0)))

    return JobStats(total=sum(by_status.values()), by_status=by_status, monthly=monthly)
