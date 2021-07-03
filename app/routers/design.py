import aiofiles
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, Response, UploadFile, status
import json
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from tempfile import TemporaryDirectory
from typing import List, Optional
import os
from zipfile import ZipFile, BadZipFile

from ..database import get_db
from ..schemas.user import User
from ..schemas.design import Design, DesignAnalysis, DesignsResponse
from ..models.design import Design as DesignModel
from ..dependencies import fastapi_users

from ..analysis.cost import get_cost_analysis
from ..analysis.value import get_value_analysis
from ..analysis.requirements import get_requirements_analysis
from ..analysis.dsm import get_dsm_analysis
from ..analysis.utils import crop_image, get_design_id, get_design_name, get_thumbnail, get_bricks

# instantiate the router
router = APIRouter()

# route to list designs (conforming to datatable's server-side api)
@router.get("/", status_code=200)
async def list_designs(
    draw: int = 0,
    start: int = 0,
    length: int = 10,
    valid_only: str = Query(None, alias="columns[4][search][value]"),
    order_column: int = Query(None, alias="order[0][column]"),
    order_direction: str = Query("asc", alias="order[0][dir]"),
    search: str = Query(None, alias="search[value]"),
    user: User = Depends(fastapi_users.current_user(active=True)),
    db: Session = Depends(get_db)
):
    total_designs = db.query(DesignModel)
    if valid_only and valid_only=='true':
        total_designs = total_designs.filter(
            DesignModel.is_valid
        )
    filtered_designs = total_designs
    if search is not None:
        filtered_designs = filtered_designs.filter(
            or_(
                DesignModel.name.contains(search),
                DesignModel.design_id.contains(search),
                DesignModel.designer.contains(search)
            )
        )
    sortable_columns = {
        1: DesignModel.timestamp,
        2: DesignModel.designer,
        3: DesignModel.name,
        4: DesignModel.is_valid,
        5: DesignModel.total_cost,
        6: DesignModel.total_revenue,
        7: DesignModel.total_profit,
        8: DesignModel.total_roi
    }
    if order_column is not None and order_column in sortable_columns:
        if order_direction == 'desc':
            filtered_designs = filtered_designs.order_by(
                desc(sortable_columns.get(order_column))
            )
        else:
            filtered_designs = filtered_designs.order_by(
                sortable_columns.get(order_column)
            )
    returned_designs = filtered_designs.offset(start).limit(length)
    return DesignsResponse(
        draw = draw,
        records_total = total_designs.count(),
        records_filtered = filtered_designs.count(),
        designs = [
            DesignAnalysis(
                **db_design.__dict__,
                dsm = json.loads(db_design.dsm_json),
                requirements = json.loads(db_design.requirements_json),
                cost = json.loads(db_design.cost_json),
                value = json.loads(db_design.value_json)
            )
            for db_design in returned_designs.all()
        ]
    )

# route to get information for a design by id
@router.get("/{design_id}", response_model=DesignAnalysis, status_code=200)
async def get_design(
    design_id: str,
    user: User = Depends(fastapi_users.current_user(active=True)),
    db: Session = Depends(get_db)
):
    try:
        db_design = db.query(DesignModel).filter(DesignModel.design_id==design_id).one()
        return DesignAnalysis(
            **db_design.__dict__,
            dsm = json.loads(db_design.dsm_json),
            requirements = json.loads(db_design.requirements_json),
            cost = json.loads(db_design.cost_json),
            value = json.loads(db_design.value_json)
        )
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Design not found."
        )

# route to delete a design by id
@router.delete("/{design_id}", response_model=DesignAnalysis, status_code=200)
async def delete_design(
    design_id: str,
    user: User = Depends(fastapi_users.current_user(active=True, superuser=True)),
    db: Session = Depends(get_db)
):
    try:
        db_design = db.query(DesignModel).filter(DesignModel.design_id==design_id).one()
        db.delete(db_design)
        db.commit()
        return DesignAnalysis(
            **db_design.__dict__,
            dsm = json.loads(db_design.dsm_json),
            requirements = json.loads(db_design.requirements_json),
            cost = json.loads(db_design.cost_json),
            value = json.loads(db_design.value_json)
        )
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Design not found."
        )

# route to create a new design
@router.post("/", response_model=DesignAnalysis, status_code=201)
async def create_design(
    file: UploadFile = File(...),
    user: User = Depends(fastapi_users.current_user(active=True)),
    db: Session = Depends(get_db)
):
    # verify the POST request has file extension `.io`
    if (file.filename.rsplit('.', 1)[1].lower() not in {'io'}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must upload a `.io` file."
        )
    # create a temporary working directory
    with TemporaryDirectory() as tempdir:
        io_path = os.path.join(tempdir, 'design.io')
        ldr_path = os.path.join(tempdir, 'model.ldr')
        thumb_path = os.path.join(tempdir, 'thumbnail.png')
        # write io file to temporary directory
        async with aiofiles.open(io_path, 'wb') as io_file:
            content = await file.read()
            await io_file.write(content)
        # extract key files from the .io file
        try:
            zip_key = b'\x73\x6f\x68\x6f\x30\x39\x30\x39'
            with ZipFile(io_path, 'r') as zip:
                zip.extract('thumbnail.png', tempdir, zip_key)
                zip.extract('model.ldr', tempdir, zip_key)
        except BadZipFile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract design files."
            )
        # crop the thumbnail image
        crop_image(thumb_path)
        # parse the design
        design = Design(
            design_id=get_design_id(ldr_path),
            name=get_design_name(ldr_path),
            designer=user.name,
            timestamp=datetime.now(timezone.utc),
            bricks=get_bricks(ldr_path)
        )
        # perform requirements analysis
        requirements_analysis = get_requirements_analysis(design)
        # perform cost analysis
        cost_analysis = get_cost_analysis(design)
        # perform market analysis
        value_analysis = get_value_analysis(design)
        # assemble the design analysis
        design_analysis = DesignAnalysis(
            **design.dict(),
            mass=design.get_mass(),
            width=design.get_width()*0.4,
            length=design.get_length()*0.4,
            height=design.get_height()*0.4,
            wheelbase=design.get_wheelbase()*0.4,
            track=design.get_track()*0.4,
            volume=design.get_volume()/1000*0.4**3,
            number_seats=design.get_num_seats(),
            cargo_volume=design.get_cargo_volume()/1000*0.4**3,
            thumbnail=get_thumbnail(thumb_path),
            dsm=get_dsm_analysis(design),
            requirements=requirements_analysis,
            cost=cost_analysis,
            value=value_analysis,
            is_valid=requirements_analysis.is_valid,
            total_cost=cost_analysis.total,
            total_revenue=value_analysis.price,
            total_profit=value_analysis.price - cost_analysis.total,
            total_roi=(value_analysis.price - cost_analysis.total)/cost_analysis.total
        )
    try:
        # try to update an existing design
        db_design = db.query(DesignModel).filter(DesignModel.design_id==design_analysis.design_id).one()
        for field in design_analysis.dict(exclude={"dsm","requirements","cost","value"}):
            if hasattr(db_design, field):
                setattr(db_design, field, design_analysis.dict()[field])
        setattr(db_design, "dsm_json", design_analysis.dsm.json())
        setattr(db_design, "requirements_json", design_analysis.requirements.json())
        setattr(db_design, "cost_json", design_analysis.cost.json())
        setattr(db_design, "value_json", design_analysis.value.json())
    except NoResultFound:
        # otherwise, create a new design
        db_design = DesignModel(
            **design_analysis.dict(exclude={"dsm","requirements","cost","value"}),
            dsm_json = design_analysis.dsm.json(),
            requirements_json = design_analysis.requirements.json(),
            cost_json = design_analysis.cost.json(),
            value_json = design_analysis.value.json()
        )
        db.add(db_design)
    # commit the transactions and refresh the database model to get id (if new)
    db.commit()
    db.refresh(db_design)
    # return resulting design analysis
    return DesignAnalysis(
        **db_design.__dict__,
        dsm = json.loads(db_design.dsm_json),
        requirements = json.loads(db_design.requirements_json),
        cost = json.loads(db_design.cost_json),
        value = json.loads(db_design.value_json)
    )
