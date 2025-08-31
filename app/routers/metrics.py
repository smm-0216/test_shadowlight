
from fastapi import APIRouter, HTTPException, Depends

from utils.database import Database
from utils.queries import get_metrics
from schemas.metrics import MetricsParams, MetricsResponse

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/dates", response_model=MetricsResponse)
def get_metrics_by_date(params: MetricsParams = Depends()) -> MetricsResponse:
    try:
        db = Database()
        base_query = get_metrics.format(
            start_date=params.start,
            end_date=params.end,
        )
        count_query = f"SELECT COUNT(*) AS total FROM ({base_query}) AS subq"
        total_data = db.read_sql(count_query)
        if total_data is None:
            raise HTTPException(
                status_code=500,
                detail="Database error while counting rows."
            )

        data_query = f"{base_query} LIMIT {params.page_size} OFFSET {params.offset}"
        df = db.read_sql(data_query)
        if df is None:
            raise HTTPException(
                status_code=500,
                detail="Database error while fetching rows."
            )

        total = int(total_data.iloc[0]["total"]) if not total_data.empty else 0
        if df.empty:
            return MetricsResponse(
                count=0,
                page=params.page,
                page_size=params.page_size,
                total=total,
                has_prev=params.page > 1,
                has_next=(params.page * params.page_size) < total,
                data=[],
                message=f"No data found for {params.start} to {params.end}.",
            )

        records = df.to_dict(orient="records")
        return MetricsResponse(
            count=len(records),
            page=params.page,
            page_size=params.page_size,
            total=total,
            has_prev=params.page > 1,
            has_next=(params.page * params.page_size) < total,
            data=records,
        )
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected server error while fetching metrics."
        )
