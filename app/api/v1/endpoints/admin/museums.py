# from fastapi import APIRouter, Depends, Query
#
# from app.api.dependencies import CurrentUser, SuperAdmin, get_museum_service
# from app.schemas.museum import (
#     MuseumCreate,
#     MuseumListResponse,
#     MuseumResponse,
#     MuseumUpdate,
# )
# from app.services.museum import MuseumService
#
# router = APIRouter(prefix="/museums", tags=["museums"])
#
#
# @router.post("", response_model=MuseumResponse, status_code=201)
# async def create_museum(
#     data: MuseumCreate,
#     current_user: SuperAdmin,
#     service: MuseumService = Depends(get_museum_service),
# ) -> MuseumResponse:
#     museum = await service.create(data, current_user)
#     return MuseumResponse.model_validate(museum)
#
#
# @router.get("", response_model=MuseumListResponse)
# async def list_museums(
#     current_user: SuperAdmin,
#     service: MuseumService = Depends(get_museum_service),
#     offset: int = Query(0, ge=0),
#     limit: int = Query(20, ge=1, le=100),
# ) -> MuseumListResponse:
#     items, total = await service.list_all(offset=offset, limit=limit)
#     return MuseumListResponse(
#         items=[MuseumResponse.model_validate(m) for m in items],
#         total=total,
#     )
#
#
# @router.get("/{museum_id}", response_model=MuseumResponse)
# async def get_museum(
#     museum_id: int,
#     current_user: CurrentUser,
#     service: MuseumService = Depends(get_museum_service),
# ) -> MuseumResponse:
#     museum = await service.get(museum_id, current_user)
#     return MuseumResponse.model_validate(museum)
#
#
# @router.patch("/{museum_id}", response_model=MuseumResponse)
# async def update_museum(
#     museum_id: int,
#     data: MuseumUpdate,
#     current_user: CurrentUser,
#     service: MuseumService = Depends(get_museum_service),
# ) -> MuseumResponse:
#     museum = await service.update(museum_id, data, current_user)
#     return MuseumResponse.model_validate(museum)
#
#
# @router.delete("/{museum_id}", status_code=204)
# async def delete_museum(
#     museum_id: int,
#     current_user: SuperAdmin,
#     service: MuseumService = Depends(get_museum_service),
# ) -> None:
#     await service.delete(museum_id)
