from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import paginate
from sqlalchemy.orm import Session

from app import crud, models, models
from app.api import deps
from app.middleware.pagination import JsonApiPage

router = APIRouter()


@router.get("/", response_model=JsonApiPage[models.CourseRead])
def read_courses(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    organization_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieves coures created under a user's organization
    Returns all courses if user is a superuser
    """
    if crud.user.is_superuser(current_user):
        courses = crud.course.get_multi(db, skip=skip, limit=limit)
    else:
        courses = crud.course.get_multi_by_owner(
            db=db, user_id=current_user.uuid, skip=skip, limit=limit,
            organization_id=organization_id,
        )
    return paginate(courses)


@router.post("/", response_model=models.CourseRead)
def create_course(
    *,
    db: Session = Depends(deps.get_db),
    course_in: models.CourseCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new course.
    """
    organization = deps.get_organization(organization_id=course_in.organization_id, db=db)
    course = crud.course.create_with_owner(db=db, obj_in=course_in, user=current_user, organization=organization)
    return course


@router.put("/{course_id}", response_model=models.CourseRead)
def update_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: str,
    course_in: models.CourseUpdate,
    organization: models.Organization = Depends(deps.get_organization),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a course.
    """
    course = crud.course.get(db=db, uuid=course_id, user_id=current_user.uuid, organization_id=organization.uuid)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if not crud.user.is_superuser(current_user) and (course.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    course = crud.course.update(db=db, db_obj=course, obj_in=course_in)
    return course


@router.get("/{course_id}", response_model=models.CourseRead)
def read_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: int,
    organization_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get course by ID.
    """
    course = crud.course.get(db=db, uuid=course_id, user_id=current_user.uuid, organization_id=organization_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if not crud.user.is_superuser(current_user) and (course.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return course


@router.delete("/{course_id}", response_model=models.CourseRead)
def delete_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: int,
    organization_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Removes a course from the commercial space (soft delete)
    """
    course = crud.course.get(db=db, uuid=course_id, user_id=current_user.uuid, organization_id=organization_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if not crud.user.is_superuser(current_user) and (course.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    course = crud.course.remove(db=db, id=id)
    return course
