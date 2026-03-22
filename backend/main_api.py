import uvicorn
import os, json
import time as time_module
import logging
from fastapi import Depends, FastAPI, HTTPException, Request, status, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic_classes import *
from sql_alchemy import *

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

############################################
#
#   Initialize the database
#
############################################

def init_db():
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/Class_Diagram.db")
    # Ensure local SQLite directory exists (safe no-op for other DBs)
    os.makedirs("data", exist_ok=True)
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=False
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return SessionLocal

app = FastAPI(
    title="Class_Diagram API",
    description="Auto-generated REST API with full CRUD operations, relationship management, and advanced features",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "System", "description": "System health and statistics"},
        {"name": "Evenement", "description": "Operations for Evenement entities"},
        {"name": "Evenement Relationships", "description": "Manage Evenement relationships"},
        {"name": "PeriodeIndisponibilite", "description": "Operations for PeriodeIndisponibilite entities"},
        {"name": "PeriodeIndisponibilite Relationships", "description": "Manage PeriodeIndisponibilite relationships"},
        {"name": "Reservation", "description": "Operations for Reservation entities"},
        {"name": "Reservation Relationships", "description": "Manage Reservation relationships"},
        {"name": "Reservation Methods", "description": "Execute Reservation methods"},
        {"name": "ElementCentre", "description": "Operations for ElementCentre entities"},
        {"name": "ElementCentre Relationships", "description": "Manage ElementCentre relationships"},
        {"name": "Salle", "description": "Operations for Salle entities"},
        {"name": "Materiel", "description": "Operations for Materiel entities"},
        {"name": "Prestation", "description": "Operations for Prestation entities"},
        {"name": "Gestionnaire", "description": "Operations for Gestionnaire entities"},
        {"name": "Gestionnaire Relationships", "description": "Manage Gestionnaire relationships"},
        {"name": "Gestionnaire Methods", "description": "Execute Gestionnaire methods"},
        {"name": "CentreCongres", "description": "Operations for CentreCongres entities"},
        {"name": "CentreCongres Relationships", "description": "Manage CentreCongres relationships"},
        {"name": "CentreCongres Methods", "description": "Execute CentreCongres methods"},
    ]
)

# Enable CORS for all origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

############################################
#
#   Middleware
#
############################################

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and responses."""
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to all responses."""
    start_time = time_module.time()
    response = await call_next(request)
    process_time = time_module.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

############################################
#
#   Exception Handlers
#
############################################

# Global exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Bad Request",
            "message": str(exc),
            "detail": "Invalid input data provided"
        }
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Handle database integrity errors."""
    logger.error(f"Database integrity error: {exc}")

    # Extract more detailed error information
    error_detail = str(exc.orig) if hasattr(exc, 'orig') else str(exc)

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": "Conflict",
            "message": "Data conflict occurred",
            "detail": error_detail
        }
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    """Handle general SQLAlchemy errors."""
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "Database operation failed",
            "detail": "An internal database error occurred"
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail if isinstance(exc.detail, str) else "HTTP Error",
            "message": exc.detail,
            "detail": f"HTTP {exc.status_code} error occurred"
        }
    )

# Initialize database session
SessionLocal = init_db()
# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        logger.error("Database session rollback due to exception")
        raise
    finally:
        db.close()

############################################
#
#   Global API endpoints
#
############################################

@app.get("/", tags=["System"])
def root():
    """Root endpoint - API information"""
    return {
        "name": "Class_Diagram API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint for monitoring"""
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected"
    }


@app.get("/statistics", tags=["System"])
def get_statistics(database: Session = Depends(get_db)):
    """Get database statistics for all entities"""
    stats = {}
    stats["evenement_count"] = database.query(Evenement).count()
    stats["periodeindisponibilite_count"] = database.query(PeriodeIndisponibilite).count()
    stats["reservation_count"] = database.query(Reservation).count()
    stats["elementcentre_count"] = database.query(ElementCentre).count()
    stats["salle_count"] = database.query(Salle).count()
    stats["materiel_count"] = database.query(Materiel).count()
    stats["prestation_count"] = database.query(Prestation).count()
    stats["gestionnaire_count"] = database.query(Gestionnaire).count()
    stats["centrecongres_count"] = database.query(CentreCongres).count()
    stats["total_entities"] = sum(stats.values())
    return stats


############################################
#
#   BESSER Action Language standard lib
#
############################################


async def BAL_size(sequence:list) -> int:
    return len(sequence)

async def BAL_is_empty(sequence:list) -> bool:
    return len(sequence) == 0

async def BAL_add(sequence:list, elem) -> None:
    sequence.append(elem)

async def BAL_remove(sequence:list, elem) -> None:
    sequence.remove(elem)

async def BAL_contains(sequence:list, elem) -> bool:
    return elem in sequence

async def BAL_filter(sequence:list, predicate) -> list:
    return [elem for elem in sequence if predicate(elem)]

async def BAL_forall(sequence:list, predicate) -> bool:
    for elem in sequence:
        if not predicate(elem):
            return False
    return True

async def BAL_exists(sequence:list, predicate) -> bool:
    for elem in sequence:
        if predicate(elem):
            return True
    return False

async def BAL_one(sequence:list, predicate) -> bool:
    found = False
    for elem in sequence:
        if predicate(elem):
            if found:
                return False
            found = True
    return found

async def BAL_is_unique(sequence:list, mapping) -> bool:
    mapped = [mapping(elem) for elem in sequence]
    return len(set(mapped)) == len(mapped)

async def BAL_map(sequence:list, mapping) -> list:
    return [mapping(elem) for elem in sequence]

async def BAL_reduce(sequence:list, reduce_fn, aggregator) -> any:
    for elem in sequence:
        aggregator = reduce_fn(aggregator, elem)
    return aggregator


############################################
#
#   Evenement functions
#
############################################

@app.get("/evenement/", response_model=None, tags=["Evenement"])
def get_all_evenement(detailed: bool = False, database: Session = Depends(get_db)) -> list:
    from sqlalchemy.orm import joinedload

    # Use detailed=true to get entities with eagerly loaded relationships (for tables with lookup columns)
    if detailed:
        # Eagerly load all relationships to avoid N+1 queries
        query = database.query(Evenement)
        evenement_list = query.all()

        # Serialize with relationships included
        result = []
        for evenement_item in evenement_list:
            item_dict = evenement_item.__dict__.copy()
            item_dict.pop('_sa_instance_state', None)

            # Add many-to-one relationships (foreign keys for lookup columns)

            # Add many-to-many and one-to-many relationship objects (full details)
            reservation_list = database.query(Reservation).filter(Reservation.evenement_id == evenement_item.id).all()
            item_dict['reservation'] = []
            for reservation_obj in reservation_list:
                reservation_dict = reservation_obj.__dict__.copy()
                reservation_dict.pop('_sa_instance_state', None)
                item_dict['reservation'].append(reservation_dict)

            result.append(item_dict)
        return result
    else:
        # Default: return flat entities (faster for charts/widgets without lookup columns)
        return database.query(Evenement).all()


@app.get("/evenement/count/", response_model=None, tags=["Evenement"])
def get_count_evenement(database: Session = Depends(get_db)) -> dict:
    """Get the total count of Evenement entities"""
    count = database.query(Evenement).count()
    return {"count": count}


@app.get("/evenement/paginated/", response_model=None, tags=["Evenement"])
def get_paginated_evenement(skip: int = 0, limit: int = 100, detailed: bool = False, database: Session = Depends(get_db)) -> dict:
    """Get paginated list of Evenement entities"""
    total = database.query(Evenement).count()
    evenement_list = database.query(Evenement).offset(skip).limit(limit).all()
    # By default, return flat entities (for charts/widgets)
    # Use detailed=true to get entities with relationships
    if not detailed:
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "data": evenement_list
        }

    result = []
    for evenement_item in evenement_list:
        reservation_ids = database.query(Reservation.id).filter(Reservation.evenement_id == evenement_item.id).all()
        item_data = {
            "evenement": evenement_item,
            "reservation_ids": [x[0] for x in reservation_ids]        }
        result.append(item_data)
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": result
    }


@app.get("/evenement/search/", response_model=None, tags=["Evenement"])
def search_evenement(
    database: Session = Depends(get_db)
) -> list:
    """Search Evenement entities by attributes"""
    query = database.query(Evenement)


    results = query.all()
    return results


@app.get("/evenement/{evenement_id}/", response_model=None, tags=["Evenement"])
async def get_evenement(evenement_id: int, database: Session = Depends(get_db)) -> Evenement:
    db_evenement = database.query(Evenement).filter(Evenement.id == evenement_id).first()
    if db_evenement is None:
        raise HTTPException(status_code=404, detail="Evenement not found")

    reservation_ids = database.query(Reservation.id).filter(Reservation.evenement_id == db_evenement.id).all()
    response_data = {
        "evenement": db_evenement,
        "reservation_ids": [x[0] for x in reservation_ids]}
    return response_data



@app.post("/evenement/", response_model=None, tags=["Evenement"])
async def create_evenement(evenement_data: EvenementCreate, database: Session = Depends(get_db)) -> Evenement:


    db_evenement = Evenement(
        description=evenement_data.description,        dateDebut=evenement_data.dateDebut,        dateFin=evenement_data.dateFin,        nom=evenement_data.nom,        emailReferent=evenement_data.emailReferent,        nbParticipantsPrevus=evenement_data.nbParticipantsPrevus        )

    database.add(db_evenement)
    database.commit()
    database.refresh(db_evenement)

    if evenement_data.reservation:
        # Validate that all Reservation IDs exist
        for reservation_id in evenement_data.reservation:
            db_reservation = database.query(Reservation).filter(Reservation.id == reservation_id).first()
            if not db_reservation:
                raise HTTPException(status_code=400, detail=f"Reservation with id {reservation_id} not found")

        # Update the related entities with the new foreign key
        database.query(Reservation).filter(Reservation.id.in_(evenement_data.reservation)).update(
            {Reservation.evenement_id: db_evenement.id}, synchronize_session=False
        )
        database.commit()



    reservation_ids = database.query(Reservation.id).filter(Reservation.evenement_id == db_evenement.id).all()
    response_data = {
        "evenement": db_evenement,
        "reservation_ids": [x[0] for x in reservation_ids]    }
    return response_data


@app.post("/evenement/bulk/", response_model=None, tags=["Evenement"])
async def bulk_create_evenement(items: list[EvenementCreate], database: Session = Depends(get_db)) -> dict:
    """Create multiple Evenement entities at once"""
    created_items = []
    errors = []

    for idx, item_data in enumerate(items):
        try:
            # Basic validation for each item

            db_evenement = Evenement(
                description=item_data.description,                dateDebut=item_data.dateDebut,                dateFin=item_data.dateFin,                nom=item_data.nom,                emailReferent=item_data.emailReferent,                nbParticipantsPrevus=item_data.nbParticipantsPrevus            )
            database.add(db_evenement)
            database.flush()  # Get ID without committing
            created_items.append(db_evenement.id)
        except Exception as e:
            errors.append({"index": idx, "error": str(e)})

    if errors:
        database.rollback()
        raise HTTPException(status_code=400, detail={"message": "Bulk creation failed", "errors": errors})

    database.commit()
    return {
        "created_count": len(created_items),
        "created_ids": created_items,
        "message": f"Successfully created {len(created_items)} Evenement entities"
    }


@app.delete("/evenement/bulk/", response_model=None, tags=["Evenement"])
async def bulk_delete_evenement(ids: list[int], database: Session = Depends(get_db)) -> dict:
    """Delete multiple Evenement entities at once"""
    deleted_count = 0
    not_found = []

    for item_id in ids:
        db_evenement = database.query(Evenement).filter(Evenement.id == item_id).first()
        if db_evenement:
            database.delete(db_evenement)
            deleted_count += 1
        else:
            not_found.append(item_id)

    database.commit()

    return {
        "deleted_count": deleted_count,
        "not_found": not_found,
        "message": f"Successfully deleted {deleted_count} Evenement entities"
    }

@app.put("/evenement/{evenement_id}/", response_model=None, tags=["Evenement"])
async def update_evenement(evenement_id: int, evenement_data: EvenementCreate, database: Session = Depends(get_db)) -> Evenement:
    db_evenement = database.query(Evenement).filter(Evenement.id == evenement_id).first()
    if db_evenement is None:
        raise HTTPException(status_code=404, detail="Evenement not found")

    setattr(db_evenement, 'description', evenement_data.description)
    setattr(db_evenement, 'dateDebut', evenement_data.dateDebut)
    setattr(db_evenement, 'dateFin', evenement_data.dateFin)
    setattr(db_evenement, 'nom', evenement_data.nom)
    setattr(db_evenement, 'emailReferent', evenement_data.emailReferent)
    setattr(db_evenement, 'nbParticipantsPrevus', evenement_data.nbParticipantsPrevus)
    if evenement_data.reservation is not None:
        # Clear all existing relationships (set foreign key to NULL)
        database.query(Reservation).filter(Reservation.evenement_id == db_evenement.id).update(
            {Reservation.evenement_id: None}, synchronize_session=False
        )

        # Set new relationships if list is not empty
        if evenement_data.reservation:
            # Validate that all IDs exist
            for reservation_id in evenement_data.reservation:
                db_reservation = database.query(Reservation).filter(Reservation.id == reservation_id).first()
                if not db_reservation:
                    raise HTTPException(status_code=400, detail=f"Reservation with id {reservation_id} not found")

            # Update the related entities with the new foreign key
            database.query(Reservation).filter(Reservation.id.in_(evenement_data.reservation)).update(
                {Reservation.evenement_id: db_evenement.id}, synchronize_session=False
            )
    database.commit()
    database.refresh(db_evenement)

    reservation_ids = database.query(Reservation.id).filter(Reservation.evenement_id == db_evenement.id).all()
    response_data = {
        "evenement": db_evenement,
        "reservation_ids": [x[0] for x in reservation_ids]    }
    return response_data


@app.delete("/evenement/{evenement_id}/", response_model=None, tags=["Evenement"])
async def delete_evenement(evenement_id: int, database: Session = Depends(get_db)):
    db_evenement = database.query(Evenement).filter(Evenement.id == evenement_id).first()
    if db_evenement is None:
        raise HTTPException(status_code=404, detail="Evenement not found")
    database.delete(db_evenement)
    database.commit()
    return db_evenement





############################################
#
#   PeriodeIndisponibilite functions
#
############################################

@app.get("/periodeindisponibilite/", response_model=None, tags=["PeriodeIndisponibilite"])
def get_all_periodeindisponibilite(detailed: bool = False, database: Session = Depends(get_db)) -> list:
    from sqlalchemy.orm import joinedload

    # Use detailed=true to get entities with eagerly loaded relationships (for tables with lookup columns)
    if detailed:
        # Eagerly load all relationships to avoid N+1 queries
        query = database.query(PeriodeIndisponibilite)
        query = query.options(joinedload(PeriodeIndisponibilite.elementcentre_2))
        periodeindisponibilite_list = query.all()

        # Serialize with relationships included
        result = []
        for periodeindisponibilite_item in periodeindisponibilite_list:
            item_dict = periodeindisponibilite_item.__dict__.copy()
            item_dict.pop('_sa_instance_state', None)

            # Add many-to-one relationships (foreign keys for lookup columns)
            if periodeindisponibilite_item.elementcentre_2:
                related_obj = periodeindisponibilite_item.elementcentre_2
                related_dict = related_obj.__dict__.copy()
                related_dict.pop('_sa_instance_state', None)
                item_dict['elementcentre_2'] = related_dict
            else:
                item_dict['elementcentre_2'] = None


            result.append(item_dict)
        return result
    else:
        # Default: return flat entities (faster for charts/widgets without lookup columns)
        return database.query(PeriodeIndisponibilite).all()


@app.get("/periodeindisponibilite/count/", response_model=None, tags=["PeriodeIndisponibilite"])
def get_count_periodeindisponibilite(database: Session = Depends(get_db)) -> dict:
    """Get the total count of PeriodeIndisponibilite entities"""
    count = database.query(PeriodeIndisponibilite).count()
    return {"count": count}


@app.get("/periodeindisponibilite/paginated/", response_model=None, tags=["PeriodeIndisponibilite"])
def get_paginated_periodeindisponibilite(skip: int = 0, limit: int = 100, detailed: bool = False, database: Session = Depends(get_db)) -> dict:
    """Get paginated list of PeriodeIndisponibilite entities"""
    total = database.query(PeriodeIndisponibilite).count()
    periodeindisponibilite_list = database.query(PeriodeIndisponibilite).offset(skip).limit(limit).all()
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": periodeindisponibilite_list
    }


@app.get("/periodeindisponibilite/search/", response_model=None, tags=["PeriodeIndisponibilite"])
def search_periodeindisponibilite(
    database: Session = Depends(get_db)
) -> list:
    """Search PeriodeIndisponibilite entities by attributes"""
    query = database.query(PeriodeIndisponibilite)


    results = query.all()
    return results


@app.get("/periodeindisponibilite/{periodeindisponibilite_id}/", response_model=None, tags=["PeriodeIndisponibilite"])
async def get_periodeindisponibilite(periodeindisponibilite_id: int, database: Session = Depends(get_db)) -> PeriodeIndisponibilite:
    db_periodeindisponibilite = database.query(PeriodeIndisponibilite).filter(PeriodeIndisponibilite.id == periodeindisponibilite_id).first()
    if db_periodeindisponibilite is None:
        raise HTTPException(status_code=404, detail="PeriodeIndisponibilite not found")

    response_data = {
        "periodeindisponibilite": db_periodeindisponibilite,
}
    return response_data



@app.post("/periodeindisponibilite/", response_model=None, tags=["PeriodeIndisponibilite"])
async def create_periodeindisponibilite(periodeindisponibilite_data: PeriodeIndisponibiliteCreate, database: Session = Depends(get_db)) -> PeriodeIndisponibilite:

    if periodeindisponibilite_data.elementcentre_2 is not None:
        db_elementcentre_2 = database.query(ElementCentre).filter(ElementCentre.id == periodeindisponibilite_data.elementcentre_2).first()
        if not db_elementcentre_2:
            raise HTTPException(status_code=400, detail="ElementCentre not found")
    else:
        raise HTTPException(status_code=400, detail="ElementCentre ID is required")

    db_periodeindisponibilite = PeriodeIndisponibilite(
        motif=periodeindisponibilite_data.motif,        dateDebut=periodeindisponibilite_data.dateDebut,        dateFin=periodeindisponibilite_data.dateFin,        elementcentre_2_id=periodeindisponibilite_data.elementcentre_2        )

    database.add(db_periodeindisponibilite)
    database.commit()
    database.refresh(db_periodeindisponibilite)




    return db_periodeindisponibilite


@app.post("/periodeindisponibilite/bulk/", response_model=None, tags=["PeriodeIndisponibilite"])
async def bulk_create_periodeindisponibilite(items: list[PeriodeIndisponibiliteCreate], database: Session = Depends(get_db)) -> dict:
    """Create multiple PeriodeIndisponibilite entities at once"""
    created_items = []
    errors = []

    for idx, item_data in enumerate(items):
        try:
            # Basic validation for each item
            if not item_data.elementcentre_2:
                raise ValueError("ElementCentre ID is required")

            db_periodeindisponibilite = PeriodeIndisponibilite(
                motif=item_data.motif,                dateDebut=item_data.dateDebut,                dateFin=item_data.dateFin,                elementcentre_2_id=item_data.elementcentre_2            )
            database.add(db_periodeindisponibilite)
            database.flush()  # Get ID without committing
            created_items.append(db_periodeindisponibilite.id)
        except Exception as e:
            errors.append({"index": idx, "error": str(e)})

    if errors:
        database.rollback()
        raise HTTPException(status_code=400, detail={"message": "Bulk creation failed", "errors": errors})

    database.commit()
    return {
        "created_count": len(created_items),
        "created_ids": created_items,
        "message": f"Successfully created {len(created_items)} PeriodeIndisponibilite entities"
    }


@app.delete("/periodeindisponibilite/bulk/", response_model=None, tags=["PeriodeIndisponibilite"])
async def bulk_delete_periodeindisponibilite(ids: list[int], database: Session = Depends(get_db)) -> dict:
    """Delete multiple PeriodeIndisponibilite entities at once"""
    deleted_count = 0
    not_found = []

    for item_id in ids:
        db_periodeindisponibilite = database.query(PeriodeIndisponibilite).filter(PeriodeIndisponibilite.id == item_id).first()
        if db_periodeindisponibilite:
            database.delete(db_periodeindisponibilite)
            deleted_count += 1
        else:
            not_found.append(item_id)

    database.commit()

    return {
        "deleted_count": deleted_count,
        "not_found": not_found,
        "message": f"Successfully deleted {deleted_count} PeriodeIndisponibilite entities"
    }

@app.put("/periodeindisponibilite/{periodeindisponibilite_id}/", response_model=None, tags=["PeriodeIndisponibilite"])
async def update_periodeindisponibilite(periodeindisponibilite_id: int, periodeindisponibilite_data: PeriodeIndisponibiliteCreate, database: Session = Depends(get_db)) -> PeriodeIndisponibilite:
    db_periodeindisponibilite = database.query(PeriodeIndisponibilite).filter(PeriodeIndisponibilite.id == periodeindisponibilite_id).first()
    if db_periodeindisponibilite is None:
        raise HTTPException(status_code=404, detail="PeriodeIndisponibilite not found")

    setattr(db_periodeindisponibilite, 'motif', periodeindisponibilite_data.motif)
    setattr(db_periodeindisponibilite, 'dateDebut', periodeindisponibilite_data.dateDebut)
    setattr(db_periodeindisponibilite, 'dateFin', periodeindisponibilite_data.dateFin)
    if periodeindisponibilite_data.elementcentre_2 is not None:
        db_elementcentre_2 = database.query(ElementCentre).filter(ElementCentre.id == periodeindisponibilite_data.elementcentre_2).first()
        if not db_elementcentre_2:
            raise HTTPException(status_code=400, detail="ElementCentre not found")
        setattr(db_periodeindisponibilite, 'elementcentre_2_id', periodeindisponibilite_data.elementcentre_2)
    database.commit()
    database.refresh(db_periodeindisponibilite)

    return db_periodeindisponibilite


@app.delete("/periodeindisponibilite/{periodeindisponibilite_id}/", response_model=None, tags=["PeriodeIndisponibilite"])
async def delete_periodeindisponibilite(periodeindisponibilite_id: int, database: Session = Depends(get_db)):
    db_periodeindisponibilite = database.query(PeriodeIndisponibilite).filter(PeriodeIndisponibilite.id == periodeindisponibilite_id).first()
    if db_periodeindisponibilite is None:
        raise HTTPException(status_code=404, detail="PeriodeIndisponibilite not found")
    database.delete(db_periodeindisponibilite)
    database.commit()
    return db_periodeindisponibilite





############################################
#
#   Reservation functions
#
############################################

@app.get("/reservation/", response_model=None, tags=["Reservation"])
def get_all_reservation(detailed: bool = False, database: Session = Depends(get_db)) -> list:
    from sqlalchemy.orm import joinedload

    # Use detailed=true to get entities with eagerly loaded relationships (for tables with lookup columns)
    if detailed:
        # Eagerly load all relationships to avoid N+1 queries
        query = database.query(Reservation)
        query = query.options(joinedload(Reservation.evenement))
        query = query.options(joinedload(Reservation.gestionnaire))
        reservation_list = query.all()

        # Serialize with relationships included
        result = []
        for reservation_item in reservation_list:
            item_dict = reservation_item.__dict__.copy()
            item_dict.pop('_sa_instance_state', None)

            # Add many-to-one relationships (foreign keys for lookup columns)
            if reservation_item.evenement:
                related_obj = reservation_item.evenement
                related_dict = related_obj.__dict__.copy()
                related_dict.pop('_sa_instance_state', None)
                item_dict['evenement'] = related_dict
            else:
                item_dict['evenement'] = None
            if reservation_item.gestionnaire:
                related_obj = reservation_item.gestionnaire
                related_dict = related_obj.__dict__.copy()
                related_dict.pop('_sa_instance_state', None)
                item_dict['gestionnaire'] = related_dict
            else:
                item_dict['gestionnaire'] = None

            # Add many-to-many and one-to-many relationship objects (full details)
            elementcentre_list = database.query(ElementCentre).join(réserve, ElementCentre.id == réserve.c.elementcentre_1).filter(réserve.c.reservation_1 == reservation_item.id).all()
            item_dict['elementcentre_1'] = []
            for elementcentre_obj in elementcentre_list:
                elementcentre_dict = elementcentre_obj.__dict__.copy()
                elementcentre_dict.pop('_sa_instance_state', None)
                item_dict['elementcentre_1'].append(elementcentre_dict)

            result.append(item_dict)
        return result
    else:
        # Default: return flat entities (faster for charts/widgets without lookup columns)
        return database.query(Reservation).all()


@app.get("/reservation/count/", response_model=None, tags=["Reservation"])
def get_count_reservation(database: Session = Depends(get_db)) -> dict:
    """Get the total count of Reservation entities"""
    count = database.query(Reservation).count()
    return {"count": count}


@app.get("/reservation/paginated/", response_model=None, tags=["Reservation"])
def get_paginated_reservation(skip: int = 0, limit: int = 100, detailed: bool = False, database: Session = Depends(get_db)) -> dict:
    """Get paginated list of Reservation entities"""
    total = database.query(Reservation).count()
    reservation_list = database.query(Reservation).offset(skip).limit(limit).all()
    # By default, return flat entities (for charts/widgets)
    # Use detailed=true to get entities with relationships
    if not detailed:
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "data": reservation_list
        }

    result = []
    for reservation_item in reservation_list:
        elementcentre_ids = database.query(réserve.c.elementcentre_1).filter(réserve.c.reservation_1 == reservation_item.id).all()
        item_data = {
            "reservation": reservation_item,
            "elementcentre_ids": [x[0] for x in elementcentre_ids],
        }
        result.append(item_data)
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": result
    }


@app.get("/reservation/search/", response_model=None, tags=["Reservation"])
def search_reservation(
    database: Session = Depends(get_db)
) -> list:
    """Search Reservation entities by attributes"""
    query = database.query(Reservation)


    results = query.all()
    return results


@app.get("/reservation/{reservation_id}/", response_model=None, tags=["Reservation"])
async def get_reservation(reservation_id: int, database: Session = Depends(get_db)) -> Reservation:
    db_reservation = database.query(Reservation).filter(Reservation.id == reservation_id).first()
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")

    elementcentre_ids = database.query(réserve.c.elementcentre_1).filter(réserve.c.reservation_1 == db_reservation.id).all()
    response_data = {
        "reservation": db_reservation,
        "elementcentre_ids": [x[0] for x in elementcentre_ids],
}
    return response_data



@app.post("/reservation/", response_model=None, tags=["Reservation"])
async def create_reservation(reservation_data: ReservationCreate, database: Session = Depends(get_db)) -> Reservation:

    if reservation_data.evenement is not None:
        db_evenement = database.query(Evenement).filter(Evenement.id == reservation_data.evenement).first()
        if not db_evenement:
            raise HTTPException(status_code=400, detail="Evenement not found")
    else:
        raise HTTPException(status_code=400, detail="Evenement ID is required")
    if reservation_data.gestionnaire is not None:
        db_gestionnaire = database.query(Gestionnaire).filter(Gestionnaire.id == reservation_data.gestionnaire).first()
        if not db_gestionnaire:
            raise HTTPException(status_code=400, detail="Gestionnaire not found")
    else:
        raise HTTPException(status_code=400, detail="Gestionnaire ID is required")
    if not reservation_data.elementcentre_1 or len(reservation_data.elementcentre_1) < 1:
        raise HTTPException(status_code=400, detail="At least 1 ElementCentre(s) required")
    if reservation_data.elementcentre_1:
        for id in reservation_data.elementcentre_1:
            # Entity already validated before creation
            db_elementcentre = database.query(ElementCentre).filter(ElementCentre.id == id).first()
            if not db_elementcentre:
                raise HTTPException(status_code=404, detail=f"ElementCentre with ID {id} not found")

    db_reservation = Reservation(
        statut=reservation_data.statut.value,        heureMaxPaye=reservation_data.heureMaxPaye,        montantTotal=reservation_data.montantTotal,        dateFin=reservation_data.dateFin,        dateDebut=reservation_data.dateDebut,        evenement_id=reservation_data.evenement,        gestionnaire_id=reservation_data.gestionnaire        )

    database.add(db_reservation)
    database.commit()
    database.refresh(db_reservation)


    if reservation_data.elementcentre_1:
        for id in reservation_data.elementcentre_1:
            # Entity already validated before creation
            db_elementcentre = database.query(ElementCentre).filter(ElementCentre.id == id).first()
            # Create the association
            association = réserve.insert().values(reservation_1=db_reservation.id, elementcentre_1=db_elementcentre.id)
            database.execute(association)
            database.commit()


    elementcentre_ids = database.query(réserve.c.elementcentre_1).filter(réserve.c.reservation_1 == db_reservation.id).all()
    response_data = {
        "reservation": db_reservation,
        "elementcentre_ids": [x[0] for x in elementcentre_ids],
    }
    return response_data


@app.post("/reservation/bulk/", response_model=None, tags=["Reservation"])
async def bulk_create_reservation(items: list[ReservationCreate], database: Session = Depends(get_db)) -> dict:
    """Create multiple Reservation entities at once"""
    created_items = []
    errors = []

    for idx, item_data in enumerate(items):
        try:
            # Basic validation for each item
            if not item_data.evenement:
                raise ValueError("Evenement ID is required")
            if not item_data.gestionnaire:
                raise ValueError("Gestionnaire ID is required")

            db_reservation = Reservation(
                statut=item_data.statut.value,                heureMaxPaye=item_data.heureMaxPaye,                montantTotal=item_data.montantTotal,                dateFin=item_data.dateFin,                dateDebut=item_data.dateDebut,                evenement_id=item_data.evenement,                gestionnaire_id=item_data.gestionnaire            )
            database.add(db_reservation)
            database.flush()  # Get ID without committing
            created_items.append(db_reservation.id)
        except Exception as e:
            errors.append({"index": idx, "error": str(e)})

    if errors:
        database.rollback()
        raise HTTPException(status_code=400, detail={"message": "Bulk creation failed", "errors": errors})

    database.commit()
    return {
        "created_count": len(created_items),
        "created_ids": created_items,
        "message": f"Successfully created {len(created_items)} Reservation entities"
    }


@app.delete("/reservation/bulk/", response_model=None, tags=["Reservation"])
async def bulk_delete_reservation(ids: list[int], database: Session = Depends(get_db)) -> dict:
    """Delete multiple Reservation entities at once"""
    deleted_count = 0
    not_found = []

    for item_id in ids:
        db_reservation = database.query(Reservation).filter(Reservation.id == item_id).first()
        if db_reservation:
            database.delete(db_reservation)
            deleted_count += 1
        else:
            not_found.append(item_id)

    database.commit()

    return {
        "deleted_count": deleted_count,
        "not_found": not_found,
        "message": f"Successfully deleted {deleted_count} Reservation entities"
    }

@app.put("/reservation/{reservation_id}/", response_model=None, tags=["Reservation"])
async def update_reservation(reservation_id: int, reservation_data: ReservationCreate, database: Session = Depends(get_db)) -> Reservation:
    db_reservation = database.query(Reservation).filter(Reservation.id == reservation_id).first()
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")

    setattr(db_reservation, 'statut', reservation_data.statut.value)
    setattr(db_reservation, 'heureMaxPaye', reservation_data.heureMaxPaye)
    setattr(db_reservation, 'montantTotal', reservation_data.montantTotal)
    setattr(db_reservation, 'dateFin', reservation_data.dateFin)
    setattr(db_reservation, 'dateDebut', reservation_data.dateDebut)
    if reservation_data.evenement is not None:
        db_evenement = database.query(Evenement).filter(Evenement.id == reservation_data.evenement).first()
        if not db_evenement:
            raise HTTPException(status_code=400, detail="Evenement not found")
        setattr(db_reservation, 'evenement_id', reservation_data.evenement)
    if reservation_data.gestionnaire is not None:
        db_gestionnaire = database.query(Gestionnaire).filter(Gestionnaire.id == reservation_data.gestionnaire).first()
        if not db_gestionnaire:
            raise HTTPException(status_code=400, detail="Gestionnaire not found")
        setattr(db_reservation, 'gestionnaire_id', reservation_data.gestionnaire)
    existing_elementcentre_ids = [assoc.elementcentre_1 for assoc in database.execute(
        réserve.select().where(réserve.c.reservation_1 == db_reservation.id))]

    elementcentres_to_remove = set(existing_elementcentre_ids) - set(reservation_data.elementcentre_1)
    for elementcentre_id in elementcentres_to_remove:
        association = réserve.delete().where(
            (réserve.c.reservation_1 == db_reservation.id) & (réserve.c.elementcentre_1 == elementcentre_id))
        database.execute(association)

    new_elementcentre_ids = set(reservation_data.elementcentre_1) - set(existing_elementcentre_ids)
    for elementcentre_id in new_elementcentre_ids:
        db_elementcentre = database.query(ElementCentre).filter(ElementCentre.id == elementcentre_id).first()
        if db_elementcentre is None:
            raise HTTPException(status_code=404, detail=f"ElementCentre with ID {elementcentre_id} not found")
        association = réserve.insert().values(elementcentre_1=db_elementcentre.id, reservation_1=db_reservation.id)
        database.execute(association)
    database.commit()
    database.refresh(db_reservation)

    elementcentre_ids = database.query(réserve.c.elementcentre_1).filter(réserve.c.reservation_1 == db_reservation.id).all()
    response_data = {
        "reservation": db_reservation,
        "elementcentre_ids": [x[0] for x in elementcentre_ids],
    }
    return response_data


@app.delete("/reservation/{reservation_id}/", response_model=None, tags=["Reservation"])
async def delete_reservation(reservation_id: int, database: Session = Depends(get_db)):
    db_reservation = database.query(Reservation).filter(Reservation.id == reservation_id).first()
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    database.delete(db_reservation)
    database.commit()
    return db_reservation

@app.post("/reservation/{reservation_id}/elementcentre_1/{elementcentre_id}/", response_model=None, tags=["Reservation Relationships"])
async def add_elementcentre_1_to_reservation(reservation_id: int, elementcentre_id: int, database: Session = Depends(get_db)):
    """Add a ElementCentre to this Reservation's elementcentre_1 relationship"""
    db_reservation = database.query(Reservation).filter(Reservation.id == reservation_id).first()
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")

    db_elementcentre = database.query(ElementCentre).filter(ElementCentre.id == elementcentre_id).first()
    if db_elementcentre is None:
        raise HTTPException(status_code=404, detail="ElementCentre not found")

    # Check if relationship already exists
    existing = database.query(réserve).filter(
        (réserve.c.reservation_1 == reservation_id) &
        (réserve.c.elementcentre_1 == elementcentre_id)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Relationship already exists")

    # Create the association
    association = réserve.insert().values(reservation_1=reservation_id, elementcentre_1=elementcentre_id)
    database.execute(association)
    database.commit()

    return {"message": "ElementCentre added to elementcentre_1 successfully"}


@app.delete("/reservation/{reservation_id}/elementcentre_1/{elementcentre_id}/", response_model=None, tags=["Reservation Relationships"])
async def remove_elementcentre_1_from_reservation(reservation_id: int, elementcentre_id: int, database: Session = Depends(get_db)):
    """Remove a ElementCentre from this Reservation's elementcentre_1 relationship"""
    db_reservation = database.query(Reservation).filter(Reservation.id == reservation_id).first()
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")

    # Check if relationship exists
    existing = database.query(réserve).filter(
        (réserve.c.reservation_1 == reservation_id) &
        (réserve.c.elementcentre_1 == elementcentre_id)
    ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Relationship not found")

    # Delete the association
    association = réserve.delete().where(
        (réserve.c.reservation_1 == reservation_id) &
        (réserve.c.elementcentre_1 == elementcentre_id)
    )
    database.execute(association)
    database.commit()

    return {"message": "ElementCentre removed from elementcentre_1 successfully"}


@app.get("/reservation/{reservation_id}/elementcentre_1/", response_model=None, tags=["Reservation Relationships"])
async def get_elementcentre_1_of_reservation(reservation_id: int, database: Session = Depends(get_db)):
    """Get all ElementCentre entities related to this Reservation through elementcentre_1"""
    db_reservation = database.query(Reservation).filter(Reservation.id == reservation_id).first()
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")

    elementcentre_ids = database.query(réserve.c.elementcentre_1).filter(réserve.c.reservation_1 == reservation_id).all()
    elementcentre_list = database.query(ElementCentre).filter(ElementCentre.id.in_([id[0] for id in elementcentre_ids])).all()

    return {
        "reservation_id": reservation_id,
        "elementcentre_1_count": len(elementcentre_list),
        "elementcentre_1": elementcentre_list
    }



############################################
#   Reservation Method Endpoints
############################################




@app.post("/reservation/{reservation_id}/methods/annuler/", response_model=None, tags=["Reservation Methods"])
async def execute_reservation_annuler(
    reservation_id: int,
    params: dict = Body(default=None, embed=True),
    database: Session = Depends(get_db)
):
    """
    Execute the annuler method on a Reservation instance.
    """
    # Retrieve the entity from the database
    _reservation_object = database.query(Reservation).filter(Reservation.id == reservation_id).first()
    if _reservation_object is None:
        raise HTTPException(status_code=404, detail="Reservation not found")

    # Prepare method parameters

    # Execute the method
    try:
        # Capture stdout to include print outputs in the response
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output

        async def wrapper(_reservation_object):
            if _reservation_object.statut in [StatutReservation.EN_ATTENTE, StatutReservation.CONFIRMEE]:
                _reservation_object.statut = StatutReservation.ANNULEE

        result = await wrapper(_reservation_object)
        # Commit DB
        database.commit()
        database.refresh(_reservation_object)

        # Restore stdout
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        return {
            "reservation_id": reservation_id,
            "method": "annuler",
            "status": "executed",
            "result": str(result) if result is not None else None,
            "output": output if output else None
        }
    except Exception as e:
        sys.stdout = sys.__stdout__
        raise HTTPException(status_code=500, detail=f"Method execution failed: {str(e)}")





@app.post("/reservation/{reservation_id}/methods/calculerMontant/", response_model=None, tags=["Reservation Methods"])
async def execute_reservation_calculerMontant(
    reservation_id: int,
    params: dict = Body(default=None, embed=True),
    database: Session = Depends(get_db)
):
    """
    Execute the calculerMontant method on a Reservation instance.
    """
    # Retrieve the entity from the database
    _reservation_object = database.query(Reservation).filter(Reservation.id == reservation_id).first()
    if _reservation_object is None:
        raise HTTPException(status_code=404, detail="Reservation not found")

    # Prepare method parameters

    # Execute the method
    try:
        # Capture stdout to include print outputs in the response
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output

        async def wrapper(_reservation_object):
            """Add your docstring here."""
            # Add your implementation here
            duree = (_reservation_object.dateFin - _reservation_object.dateDebut).days
            prix_total = 0.0
            for element in _reservation_object.elementcentre_1:
                prix = element.Prix
                if element.Saison == Saison.HAUTE:
                    prix = prix * 1.5
                elif element.Saison == Saison.BASSE:
                    prix = prix * 0.8
                prix_total += prix
            _reservation_object.montantTotal = duree * prix_total
            return _reservation_object.montantTotal


        result = await wrapper(_reservation_object)
        # Commit DB
        database.commit()
        database.refresh(_reservation_object)

        # Restore stdout
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        return {
            "reservation_id": reservation_id,
            "method": "calculerMontant",
            "status": "executed",
            "result": str(result) if result is not None else None,
            "output": output if output else None
        }
    except Exception as e:
        sys.stdout = sys.__stdout__
        raise HTTPException(status_code=500, detail=f"Method execution failed: {str(e)}")





@app.post("/reservation/{reservation_id}/methods/confirmer/", response_model=None, tags=["Reservation Methods"])
async def execute_reservation_confirmer(
    reservation_id: int,
    params: dict = Body(default=None, embed=True),
    database: Session = Depends(get_db)
):
    """
    Execute the confirmer method on a Reservation instance.
    """
    # Retrieve the entity from the database
    _reservation_object = database.query(Reservation).filter(Reservation.id == reservation_id).first()
    if _reservation_object is None:
        raise HTTPException(status_code=404, detail="Reservation not found")

    # Prepare method parameters

    # Execute the method
    try:
        # Capture stdout to include print outputs in the response
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output

        async def wrapper(_reservation_object):
            """Add your docstring here."""
            # Add your implementation here
            if _reservation_object.statut == StatutReservation.EN_ATTENTE:
                _reservation_object.statut = StatutReservation.CONFIRMEE 	


        result = await wrapper(_reservation_object)
        # Commit DB
        database.commit()
        database.refresh(_reservation_object)

        # Restore stdout
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        return {
            "reservation_id": reservation_id,
            "method": "confirmer",
            "status": "executed",
            "result": str(result) if result is not None else None,
            "output": output if output else None
        }
    except Exception as e:
        sys.stdout = sys.__stdout__
        raise HTTPException(status_code=500, detail=f"Method execution failed: {str(e)}")



############################################
#
#   ElementCentre functions
#
############################################

@app.get("/elementcentre/", response_model=None, tags=["ElementCentre"])
def get_all_elementcentre(detailed: bool = False, database: Session = Depends(get_db)) -> list:
    from sqlalchemy.orm import joinedload

    # Use detailed=true to get entities with eagerly loaded relationships (for tables with lookup columns)
    if detailed:
        # Eagerly load all relationships to avoid N+1 queries
        query = database.query(ElementCentre)
        query = query.options(joinedload(ElementCentre.centrecongres))
        elementcentre_list = query.all()

        # Serialize with relationships included
        result = []
        for elementcentre_item in elementcentre_list:
            item_dict = elementcentre_item.__dict__.copy()
            item_dict.pop('_sa_instance_state', None)

            # Add many-to-one relationships (foreign keys for lookup columns)
            if elementcentre_item.centrecongres:
                related_obj = elementcentre_item.centrecongres
                related_dict = related_obj.__dict__.copy()
                related_dict.pop('_sa_instance_state', None)
                item_dict['centrecongres'] = related_dict
            else:
                item_dict['centrecongres'] = None

            # Add many-to-many and one-to-many relationship objects (full details)
            reservation_list = database.query(Reservation).join(réserve, Reservation.id == réserve.c.reservation_1).filter(réserve.c.elementcentre_1 == elementcentre_item.id).all()
            item_dict['reservation_1'] = []
            for reservation_obj in reservation_list:
                reservation_dict = reservation_obj.__dict__.copy()
                reservation_dict.pop('_sa_instance_state', None)
                item_dict['reservation_1'].append(reservation_dict)
            periodeindisponibilite_list = database.query(PeriodeIndisponibilite).filter(PeriodeIndisponibilite.elementcentre_2_id == elementcentre_item.id).all()
            item_dict['periodeindisponibilite'] = []
            for periodeindisponibilite_obj in periodeindisponibilite_list:
                periodeindisponibilite_dict = periodeindisponibilite_obj.__dict__.copy()
                periodeindisponibilite_dict.pop('_sa_instance_state', None)
                item_dict['periodeindisponibilite'].append(periodeindisponibilite_dict)

            result.append(item_dict)
        return result
    else:
        # Default: return flat entities (faster for charts/widgets without lookup columns)
        return database.query(ElementCentre).all()


@app.get("/elementcentre/count/", response_model=None, tags=["ElementCentre"])
def get_count_elementcentre(database: Session = Depends(get_db)) -> dict:
    """Get the total count of ElementCentre entities"""
    count = database.query(ElementCentre).count()
    return {"count": count}


@app.get("/elementcentre/paginated/", response_model=None, tags=["ElementCentre"])
def get_paginated_elementcentre(skip: int = 0, limit: int = 100, detailed: bool = False, database: Session = Depends(get_db)) -> dict:
    """Get paginated list of ElementCentre entities"""
    total = database.query(ElementCentre).count()
    elementcentre_list = database.query(ElementCentre).offset(skip).limit(limit).all()
    # By default, return flat entities (for charts/widgets)
    # Use detailed=true to get entities with relationships
    if not detailed:
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "data": elementcentre_list
        }

    result = []
    for elementcentre_item in elementcentre_list:
        reservation_ids = database.query(réserve.c.reservation_1).filter(réserve.c.elementcentre_1 == elementcentre_item.id).all()
        periodeindisponibilite_ids = database.query(PeriodeIndisponibilite.id).filter(PeriodeIndisponibilite.elementcentre_2_id == elementcentre_item.id).all()
        item_data = {
            "elementcentre": elementcentre_item,
            "reservation_ids": [x[0] for x in reservation_ids],
            "periodeindisponibilite_ids": [x[0] for x in periodeindisponibilite_ids]        }
        result.append(item_data)
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": result
    }


@app.get("/elementcentre/search/", response_model=None, tags=["ElementCentre"])
def search_elementcentre(
    database: Session = Depends(get_db)
) -> list:
    """Search ElementCentre entities by attributes"""
    query = database.query(ElementCentre)


    results = query.all()
    return results


@app.get("/elementcentre/{elementcentre_id}/", response_model=None, tags=["ElementCentre"])
async def get_elementcentre(elementcentre_id: int, database: Session = Depends(get_db)) -> ElementCentre:
    db_elementcentre = database.query(ElementCentre).filter(ElementCentre.id == elementcentre_id).first()
    if db_elementcentre is None:
        raise HTTPException(status_code=404, detail="ElementCentre not found")

    reservation_ids = database.query(réserve.c.reservation_1).filter(réserve.c.elementcentre_1 == db_elementcentre.id).all()
    periodeindisponibilite_ids = database.query(PeriodeIndisponibilite.id).filter(PeriodeIndisponibilite.elementcentre_2_id == db_elementcentre.id).all()
    response_data = {
        "elementcentre": db_elementcentre,
        "reservation_ids": [x[0] for x in reservation_ids],
        "periodeindisponibilite_ids": [x[0] for x in periodeindisponibilite_ids]}
    return response_data



@app.post("/elementcentre/", response_model=None, tags=["ElementCentre"])
async def create_elementcentre(elementcentre_data: ElementCentreCreate, database: Session = Depends(get_db)) -> ElementCentre:

    if elementcentre_data.centrecongres is not None:
        db_centrecongres = database.query(CentreCongres).filter(CentreCongres.id == elementcentre_data.centrecongres).first()
        if not db_centrecongres:
            raise HTTPException(status_code=400, detail="CentreCongres not found")
    else:
        raise HTTPException(status_code=400, detail="CentreCongres ID is required")
    if elementcentre_data.reservation_1:
        for id in elementcentre_data.reservation_1:
            # Entity already validated before creation
            db_reservation = database.query(Reservation).filter(Reservation.id == id).first()
            if not db_reservation:
                raise HTTPException(status_code=404, detail=f"Reservation with ID {id} not found")

    db_elementcentre = ElementCentre(
        Prix=elementcentre_data.Prix,        type=elementcentre_data.type.value,        dureeMinLocation=elementcentre_data.dureeMinLocation,        Saison=elementcentre_data.Saison.value,        description=elementcentre_data.description,        joursDisponibles=elementcentre_data.joursDisponibles,        nom=elementcentre_data.nom,        centrecongres_id=elementcentre_data.centrecongres        )

    database.add(db_elementcentre)
    database.commit()
    database.refresh(db_elementcentre)

    if elementcentre_data.periodeindisponibilite:
        # Validate that all PeriodeIndisponibilite IDs exist
        for periodeindisponibilite_id in elementcentre_data.periodeindisponibilite:
            db_periodeindisponibilite = database.query(PeriodeIndisponibilite).filter(PeriodeIndisponibilite.id == periodeindisponibilite_id).first()
            if not db_periodeindisponibilite:
                raise HTTPException(status_code=400, detail=f"PeriodeIndisponibilite with id {periodeindisponibilite_id} not found")

        # Update the related entities with the new foreign key
        database.query(PeriodeIndisponibilite).filter(PeriodeIndisponibilite.id.in_(elementcentre_data.periodeindisponibilite)).update(
            {PeriodeIndisponibilite.elementcentre_2_id: db_elementcentre.id}, synchronize_session=False
        )
        database.commit()

    if elementcentre_data.reservation_1:
        for id in elementcentre_data.reservation_1:
            # Entity already validated before creation
            db_reservation = database.query(Reservation).filter(Reservation.id == id).first()
            # Create the association
            association = réserve.insert().values(elementcentre_1=db_elementcentre.id, reservation_1=db_reservation.id)
            database.execute(association)
            database.commit()


    reservation_ids = database.query(réserve.c.reservation_1).filter(réserve.c.elementcentre_1 == db_elementcentre.id).all()
    periodeindisponibilite_ids = database.query(PeriodeIndisponibilite.id).filter(PeriodeIndisponibilite.elementcentre_2_id == db_elementcentre.id).all()
    response_data = {
        "elementcentre": db_elementcentre,
        "reservation_ids": [x[0] for x in reservation_ids],
        "periodeindisponibilite_ids": [x[0] for x in periodeindisponibilite_ids]    }
    return response_data


@app.post("/elementcentre/bulk/", response_model=None, tags=["ElementCentre"])
async def bulk_create_elementcentre(items: list[ElementCentreCreate], database: Session = Depends(get_db)) -> dict:
    """Create multiple ElementCentre entities at once"""
    created_items = []
    errors = []

    for idx, item_data in enumerate(items):
        try:
            # Basic validation for each item
            if not item_data.centrecongres:
                raise ValueError("CentreCongres ID is required")

            db_elementcentre = ElementCentre(
                Prix=item_data.Prix,                type=item_data.type.value,                dureeMinLocation=item_data.dureeMinLocation,                Saison=item_data.Saison.value,                description=item_data.description,                joursDisponibles=item_data.joursDisponibles,                nom=item_data.nom,                centrecongres_id=item_data.centrecongres            )
            database.add(db_elementcentre)
            database.flush()  # Get ID without committing
            created_items.append(db_elementcentre.id)
        except Exception as e:
            errors.append({"index": idx, "error": str(e)})

    if errors:
        database.rollback()
        raise HTTPException(status_code=400, detail={"message": "Bulk creation failed", "errors": errors})

    database.commit()
    return {
        "created_count": len(created_items),
        "created_ids": created_items,
        "message": f"Successfully created {len(created_items)} ElementCentre entities"
    }


@app.delete("/elementcentre/bulk/", response_model=None, tags=["ElementCentre"])
async def bulk_delete_elementcentre(ids: list[int], database: Session = Depends(get_db)) -> dict:
    """Delete multiple ElementCentre entities at once"""
    deleted_count = 0
    not_found = []

    for item_id in ids:
        db_elementcentre = database.query(ElementCentre).filter(ElementCentre.id == item_id).first()
        if db_elementcentre:
            database.delete(db_elementcentre)
            deleted_count += 1
        else:
            not_found.append(item_id)

    database.commit()

    return {
        "deleted_count": deleted_count,
        "not_found": not_found,
        "message": f"Successfully deleted {deleted_count} ElementCentre entities"
    }

@app.put("/elementcentre/{elementcentre_id}/", response_model=None, tags=["ElementCentre"])
async def update_elementcentre(elementcentre_id: int, elementcentre_data: ElementCentreCreate, database: Session = Depends(get_db)) -> ElementCentre:
    db_elementcentre = database.query(ElementCentre).filter(ElementCentre.id == elementcentre_id).first()
    if db_elementcentre is None:
        raise HTTPException(status_code=404, detail="ElementCentre not found")

    setattr(db_elementcentre, 'Prix', elementcentre_data.Prix)
    setattr(db_elementcentre, 'type', elementcentre_data.type.value)
    setattr(db_elementcentre, 'dureeMinLocation', elementcentre_data.dureeMinLocation)
    setattr(db_elementcentre, 'Saison', elementcentre_data.Saison.value)
    setattr(db_elementcentre, 'description', elementcentre_data.description)
    setattr(db_elementcentre, 'joursDisponibles', elementcentre_data.joursDisponibles)
    setattr(db_elementcentre, 'nom', elementcentre_data.nom)
    if elementcentre_data.centrecongres is not None:
        db_centrecongres = database.query(CentreCongres).filter(CentreCongres.id == elementcentre_data.centrecongres).first()
        if not db_centrecongres:
            raise HTTPException(status_code=400, detail="CentreCongres not found")
        setattr(db_elementcentre, 'centrecongres_id', elementcentre_data.centrecongres)
    if elementcentre_data.periodeindisponibilite is not None:
        # Clear all existing relationships (set foreign key to NULL)
        database.query(PeriodeIndisponibilite).filter(PeriodeIndisponibilite.elementcentre_2_id == db_elementcentre.id).update(
            {PeriodeIndisponibilite.elementcentre_2_id: None}, synchronize_session=False
        )

        # Set new relationships if list is not empty
        if elementcentre_data.periodeindisponibilite:
            # Validate that all IDs exist
            for periodeindisponibilite_id in elementcentre_data.periodeindisponibilite:
                db_periodeindisponibilite = database.query(PeriodeIndisponibilite).filter(PeriodeIndisponibilite.id == periodeindisponibilite_id).first()
                if not db_periodeindisponibilite:
                    raise HTTPException(status_code=400, detail=f"PeriodeIndisponibilite with id {periodeindisponibilite_id} not found")

            # Update the related entities with the new foreign key
            database.query(PeriodeIndisponibilite).filter(PeriodeIndisponibilite.id.in_(elementcentre_data.periodeindisponibilite)).update(
                {PeriodeIndisponibilite.elementcentre_2_id: db_elementcentre.id}, synchronize_session=False
            )
    existing_reservation_ids = [assoc.reservation_1 for assoc in database.execute(
        réserve.select().where(réserve.c.elementcentre_1 == db_elementcentre.id))]

    reservations_to_remove = set(existing_reservation_ids) - set(elementcentre_data.reservation_1)
    for reservation_id in reservations_to_remove:
        association = réserve.delete().where(
            (réserve.c.elementcentre_1 == db_elementcentre.id) & (réserve.c.reservation_1 == reservation_id))
        database.execute(association)

    new_reservation_ids = set(elementcentre_data.reservation_1) - set(existing_reservation_ids)
    for reservation_id in new_reservation_ids:
        db_reservation = database.query(Reservation).filter(Reservation.id == reservation_id).first()
        if db_reservation is None:
            raise HTTPException(status_code=404, detail=f"Reservation with ID {reservation_id} not found")
        association = réserve.insert().values(reservation_1=db_reservation.id, elementcentre_1=db_elementcentre.id)
        database.execute(association)
    database.commit()
    database.refresh(db_elementcentre)

    reservation_ids = database.query(réserve.c.reservation_1).filter(réserve.c.elementcentre_1 == db_elementcentre.id).all()
    periodeindisponibilite_ids = database.query(PeriodeIndisponibilite.id).filter(PeriodeIndisponibilite.elementcentre_2_id == db_elementcentre.id).all()
    response_data = {
        "elementcentre": db_elementcentre,
        "reservation_ids": [x[0] for x in reservation_ids],
        "periodeindisponibilite_ids": [x[0] for x in periodeindisponibilite_ids]    }
    return response_data


@app.delete("/elementcentre/{elementcentre_id}/", response_model=None, tags=["ElementCentre"])
async def delete_elementcentre(elementcentre_id: int, database: Session = Depends(get_db)):
    db_elementcentre = database.query(ElementCentre).filter(ElementCentre.id == elementcentre_id).first()
    if db_elementcentre is None:
        raise HTTPException(status_code=404, detail="ElementCentre not found")
    database.delete(db_elementcentre)
    database.commit()
    return db_elementcentre

@app.post("/elementcentre/{elementcentre_id}/reservation_1/{reservation_id}/", response_model=None, tags=["ElementCentre Relationships"])
async def add_reservation_1_to_elementcentre(elementcentre_id: int, reservation_id: int, database: Session = Depends(get_db)):
    """Add a Reservation to this ElementCentre's reservation_1 relationship"""
    db_elementcentre = database.query(ElementCentre).filter(ElementCentre.id == elementcentre_id).first()
    if db_elementcentre is None:
        raise HTTPException(status_code=404, detail="ElementCentre not found")

    db_reservation = database.query(Reservation).filter(Reservation.id == reservation_id).first()
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")

    # Check if relationship already exists
    existing = database.query(réserve).filter(
        (réserve.c.elementcentre_1 == elementcentre_id) &
        (réserve.c.reservation_1 == reservation_id)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Relationship already exists")

    # Create the association
    association = réserve.insert().values(elementcentre_1=elementcentre_id, reservation_1=reservation_id)
    database.execute(association)
    database.commit()

    return {"message": "Reservation added to reservation_1 successfully"}


@app.delete("/elementcentre/{elementcentre_id}/reservation_1/{reservation_id}/", response_model=None, tags=["ElementCentre Relationships"])
async def remove_reservation_1_from_elementcentre(elementcentre_id: int, reservation_id: int, database: Session = Depends(get_db)):
    """Remove a Reservation from this ElementCentre's reservation_1 relationship"""
    db_elementcentre = database.query(ElementCentre).filter(ElementCentre.id == elementcentre_id).first()
    if db_elementcentre is None:
        raise HTTPException(status_code=404, detail="ElementCentre not found")

    # Check if relationship exists
    existing = database.query(réserve).filter(
        (réserve.c.elementcentre_1 == elementcentre_id) &
        (réserve.c.reservation_1 == reservation_id)
    ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Relationship not found")

    # Delete the association
    association = réserve.delete().where(
        (réserve.c.elementcentre_1 == elementcentre_id) &
        (réserve.c.reservation_1 == reservation_id)
    )
    database.execute(association)
    database.commit()

    return {"message": "Reservation removed from reservation_1 successfully"}


@app.get("/elementcentre/{elementcentre_id}/reservation_1/", response_model=None, tags=["ElementCentre Relationships"])
async def get_reservation_1_of_elementcentre(elementcentre_id: int, database: Session = Depends(get_db)):
    """Get all Reservation entities related to this ElementCentre through reservation_1"""
    db_elementcentre = database.query(ElementCentre).filter(ElementCentre.id == elementcentre_id).first()
    if db_elementcentre is None:
        raise HTTPException(status_code=404, detail="ElementCentre not found")

    reservation_ids = database.query(réserve.c.reservation_1).filter(réserve.c.elementcentre_1 == elementcentre_id).all()
    reservation_list = database.query(Reservation).filter(Reservation.id.in_([id[0] for id in reservation_ids])).all()

    return {
        "elementcentre_id": elementcentre_id,
        "reservation_1_count": len(reservation_list),
        "reservation_1": reservation_list
    }





############################################
#
#   Salle functions
#
############################################

@app.get("/salle/", response_model=None, tags=["Salle"])
def get_all_salle(detailed: bool = False, database: Session = Depends(get_db)) -> list:
    from sqlalchemy.orm import joinedload

    # Use detailed=true to get entities with eagerly loaded relationships (for tables with lookup columns)
    if detailed:
        # Eagerly load all relationships to avoid N+1 queries
        query = database.query(Salle)
        query = query.options(joinedload(Salle.centrecongres))
        salle_list = query.all()

        # Serialize with relationships included
        result = []
        for salle_item in salle_list:
            item_dict = salle_item.__dict__.copy()
            item_dict.pop('_sa_instance_state', None)

            # Add many-to-one relationships (foreign keys for lookup columns)
            if salle_item.centrecongres:
                related_obj = salle_item.centrecongres
                related_dict = related_obj.__dict__.copy()
                related_dict.pop('_sa_instance_state', None)
                item_dict['centrecongres'] = related_dict
            else:
                item_dict['centrecongres'] = None

            # Add many-to-many and one-to-many relationship objects (full details)
            reservation_list = database.query(Reservation).join(réserve, Reservation.id == réserve.c.reservation_1).filter(réserve.c.elementcentre_1 == salle_item.id).all()
            item_dict['reservation_1'] = []
            for reservation_obj in reservation_list:
                reservation_dict = reservation_obj.__dict__.copy()
                reservation_dict.pop('_sa_instance_state', None)
                item_dict['reservation_1'].append(reservation_dict)
            periodeindisponibilite_list = database.query(PeriodeIndisponibilite).filter(PeriodeIndisponibilite.elementcentre_2_id == salle_item.id).all()
            item_dict['periodeindisponibilite'] = []
            for periodeindisponibilite_obj in periodeindisponibilite_list:
                periodeindisponibilite_dict = periodeindisponibilite_obj.__dict__.copy()
                periodeindisponibilite_dict.pop('_sa_instance_state', None)
                item_dict['periodeindisponibilite'].append(periodeindisponibilite_dict)

            result.append(item_dict)
        return result
    else:
        # Default: return flat entities (faster for charts/widgets without lookup columns)
        return database.query(Salle).all()


@app.get("/salle/count/", response_model=None, tags=["Salle"])
def get_count_salle(database: Session = Depends(get_db)) -> dict:
    """Get the total count of Salle entities"""
    count = database.query(Salle).count()
    return {"count": count}


@app.get("/salle/paginated/", response_model=None, tags=["Salle"])
def get_paginated_salle(skip: int = 0, limit: int = 100, detailed: bool = False, database: Session = Depends(get_db)) -> dict:
    """Get paginated list of Salle entities"""
    total = database.query(Salle).count()
    salle_list = database.query(Salle).offset(skip).limit(limit).all()
    # By default, return flat entities (for charts/widgets)
    # Use detailed=true to get entities with relationships
    if not detailed:
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "data": salle_list
        }

    result = []
    for salle_item in salle_list:
        reservation_ids = database.query(réserve.c.reservation_1).filter(réserve.c.elementcentre_1 == salle_item.id).all()
        periodeindisponibilite_ids = database.query(PeriodeIndisponibilite.id).filter(PeriodeIndisponibilite.elementcentre_2_id == salle_item.id).all()
        item_data = {
            "salle": salle_item,
            "reservation_ids": [x[0] for x in reservation_ids],
            "periodeindisponibilite_ids": [x[0] for x in periodeindisponibilite_ids]        }
        result.append(item_data)
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": result
    }


@app.get("/salle/search/", response_model=None, tags=["Salle"])
def search_salle(
    database: Session = Depends(get_db)
) -> list:
    """Search Salle entities by attributes"""
    query = database.query(Salle)


    results = query.all()
    return results


@app.get("/salle/{salle_id}/", response_model=None, tags=["Salle"])
async def get_salle(salle_id: int, database: Session = Depends(get_db)) -> Salle:
    db_salle = database.query(Salle).filter(Salle.id == salle_id).first()
    if db_salle is None:
        raise HTTPException(status_code=404, detail="Salle not found")

    reservation_ids = database.query(réserve.c.reservation_1).filter(réserve.c.elementcentre_1 == db_salle.id).all()
    periodeindisponibilite_ids = database.query(PeriodeIndisponibilite.id).filter(PeriodeIndisponibilite.elementcentre_2_id == db_salle.id).all()
    response_data = {
        "salle": db_salle,
        "reservation_ids": [x[0] for x in reservation_ids],
        "periodeindisponibilite_ids": [x[0] for x in periodeindisponibilite_ids]}
    return response_data



@app.post("/salle/", response_model=None, tags=["Salle"])
async def create_salle(salle_data: SalleCreate, database: Session = Depends(get_db)) -> Salle:

    if salle_data.centrecongres is not None:
        db_centrecongres = database.query(CentreCongres).filter(CentreCongres.id == salle_data.centrecongres).first()
        if not db_centrecongres:
            raise HTTPException(status_code=400, detail="CentreCongres not found")
    else:
        raise HTTPException(status_code=400, detail="CentreCongres ID is required")
    if salle_data.reservation_1:
        for id in salle_data.reservation_1:
            # Entity already validated before creation
            db_reservation = database.query(Reservation).filter(Reservation.id == id).first()
            if not db_reservation:
                raise HTTPException(status_code=404, detail=f"Reservation with ID {id} not found")

    db_salle = Salle(
        Prix=salle_data.Prix,        type=salle_data.type.value,        dureeMinLocation=salle_data.dureeMinLocation,        Saison=salle_data.Saison.value,        description=salle_data.description,        joursDisponibles=salle_data.joursDisponibles,        nom=salle_data.nom,        capaciteMax=salle_data.capaciteMax,        superficie=salle_data.superficie,        centrecongres_id=salle_data.centrecongres        )

    database.add(db_salle)
    database.commit()
    database.refresh(db_salle)

    if salle_data.periodeindisponibilite:
        # Validate that all PeriodeIndisponibilite IDs exist
        for periodeindisponibilite_id in salle_data.periodeindisponibilite:
            db_periodeindisponibilite = database.query(PeriodeIndisponibilite).filter(PeriodeIndisponibilite.id == periodeindisponibilite_id).first()
            if not db_periodeindisponibilite:
                raise HTTPException(status_code=400, detail=f"PeriodeIndisponibilite with id {periodeindisponibilite_id} not found")

        # Update the related entities with the new foreign key
        database.query(PeriodeIndisponibilite).filter(PeriodeIndisponibilite.id.in_(salle_data.periodeindisponibilite)).update(
            {PeriodeIndisponibilite.elementcentre_2_id: db_salle.id}, synchronize_session=False
        )
        database.commit()

    if salle_data.reservation_1:
        for id in salle_data.reservation_1:
            # Entity already validated before creation
            db_reservation = database.query(Reservation).filter(Reservation.id == id).first()
            # Create the association
            association = réserve.insert().values(elementcentre_1=db_salle.id, reservation_1=db_reservation.id)
            database.execute(association)
            database.commit()


    reservation_ids = database.query(réserve.c.reservation_1).filter(réserve.c.elementcentre_1 == db_salle.id).all()
    periodeindisponibilite_ids = database.query(PeriodeIndisponibilite.id).filter(PeriodeIndisponibilite.elementcentre_2_id == db_salle.id).all()
    response_data = {
        "salle": db_salle,
        "reservation_ids": [x[0] for x in reservation_ids],
        "periodeindisponibilite_ids": [x[0] for x in periodeindisponibilite_ids]    }
    return response_data


@app.post("/salle/bulk/", response_model=None, tags=["Salle"])
async def bulk_create_salle(items: list[SalleCreate], database: Session = Depends(get_db)) -> dict:
    """Create multiple Salle entities at once"""
    created_items = []
    errors = []

    for idx, item_data in enumerate(items):
        try:
            # Basic validation for each item
            if not item_data.centrecongres:
                raise ValueError("CentreCongres ID is required")

            db_salle = Salle(
                Prix=item_data.Prix,                type=item_data.type.value,                dureeMinLocation=item_data.dureeMinLocation,                Saison=item_data.Saison.value,                description=item_data.description,                joursDisponibles=item_data.joursDisponibles,                nom=item_data.nom,                capaciteMax=item_data.capaciteMax,                superficie=item_data.superficie,                centrecongres_id=item_data.centrecongres            )
            database.add(db_salle)
            database.flush()  # Get ID without committing
            created_items.append(db_salle.id)
        except Exception as e:
            errors.append({"index": idx, "error": str(e)})

    if errors:
        database.rollback()
        raise HTTPException(status_code=400, detail={"message": "Bulk creation failed", "errors": errors})

    database.commit()
    return {
        "created_count": len(created_items),
        "created_ids": created_items,
        "message": f"Successfully created {len(created_items)} Salle entities"
    }


@app.delete("/salle/bulk/", response_model=None, tags=["Salle"])
async def bulk_delete_salle(ids: list[int], database: Session = Depends(get_db)) -> dict:
    """Delete multiple Salle entities at once"""
    deleted_count = 0
    not_found = []

    for item_id in ids:
        db_salle = database.query(Salle).filter(Salle.id == item_id).first()
        if db_salle:
            database.delete(db_salle)
            deleted_count += 1
        else:
            not_found.append(item_id)

    database.commit()

    return {
        "deleted_count": deleted_count,
        "not_found": not_found,
        "message": f"Successfully deleted {deleted_count} Salle entities"
    }

@app.put("/salle/{salle_id}/", response_model=None, tags=["Salle"])
async def update_salle(salle_id: int, salle_data: SalleCreate, database: Session = Depends(get_db)) -> Salle:
    db_salle = database.query(Salle).filter(Salle.id == salle_id).first()
    if db_salle is None:
        raise HTTPException(status_code=404, detail="Salle not found")

    setattr(db_salle, 'capaciteMax', salle_data.capaciteMax)
    setattr(db_salle, 'superficie', salle_data.superficie)
    if salle_data.periodeindisponibilite is not None:
        # Clear all existing relationships (set foreign key to NULL)
        database.query(PeriodeIndisponibilite).filter(PeriodeIndisponibilite.elementcentre_2_id == db_salle.id).update(
            {PeriodeIndisponibilite.elementcentre_2_id: None}, synchronize_session=False
        )

        # Set new relationships if list is not empty
        if salle_data.periodeindisponibilite:
            # Validate that all IDs exist
            for periodeindisponibilite_id in salle_data.periodeindisponibilite:
                db_periodeindisponibilite = database.query(PeriodeIndisponibilite).filter(PeriodeIndisponibilite.id == periodeindisponibilite_id).first()
                if not db_periodeindisponibilite:
                    raise HTTPException(status_code=400, detail=f"PeriodeIndisponibilite with id {periodeindisponibilite_id} not found")

            # Update the related entities with the new foreign key
            database.query(PeriodeIndisponibilite).filter(PeriodeIndisponibilite.id.in_(salle_data.periodeindisponibilite)).update(
                {PeriodeIndisponibilite.elementcentre_2_id: db_salle.id}, synchronize_session=False
            )
    existing_reservation_ids = [assoc.reservation_1 for assoc in database.execute(
        réserve.select().where(réserve.c.elementcentre_1 == db_salle.id))]

    reservations_to_remove = set(existing_reservation_ids) - set(salle_data.reservation_1)
    for reservation_id in reservations_to_remove:
        association = réserve.delete().where(
            (réserve.c.elementcentre_1 == db_salle.id) & (réserve.c.reservation_1 == reservation_id))
        database.execute(association)

    new_reservation_ids = set(salle_data.reservation_1) - set(existing_reservation_ids)
    for reservation_id in new_reservation_ids:
        db_reservation = database.query(Reservation).filter(Reservation.id == reservation_id).first()
        if db_reservation is None:
            raise HTTPException(status_code=404, detail=f"Reservation with ID {reservation_id} not found")
        association = réserve.insert().values(reservation_1=db_reservation.id, elementcentre_1=db_salle.id)
        database.execute(association)
    database.commit()
    database.refresh(db_salle)

    reservation_ids = database.query(réserve.c.reservation_1).filter(réserve.c.elementcentre_1 == db_salle.id).all()
    periodeindisponibilite_ids = database.query(PeriodeIndisponibilite.id).filter(PeriodeIndisponibilite.elementcentre_2_id == db_salle.id).all()
    response_data = {
        "salle": db_salle,
        "reservation_ids": [x[0] for x in reservation_ids],
        "periodeindisponibilite_ids": [x[0] for x in periodeindisponibilite_ids]    }
    return response_data


@app.delete("/salle/{salle_id}/", response_model=None, tags=["Salle"])
async def delete_salle(salle_id: int, database: Session = Depends(get_db)):
    db_salle = database.query(Salle).filter(Salle.id == salle_id).first()
    if db_salle is None:
        raise HTTPException(status_code=404, detail="Salle not found")
    database.delete(db_salle)
    database.commit()
    return db_salle

@app.post("/salle/{salle_id}/reservation_1/{reservation_id}/", response_model=None, tags=["Salle Relationships"])
async def add_reservation_1_to_salle(salle_id: int, reservation_id: int, database: Session = Depends(get_db)):
    """Add a Reservation to this Salle's reservation_1 relationship"""
    db_salle = database.query(Salle).filter(Salle.id == salle_id).first()
    if db_salle is None:
        raise HTTPException(status_code=404, detail="Salle not found")

    db_reservation = database.query(Reservation).filter(Reservation.id == reservation_id).first()
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")

    # Check if relationship already exists
    existing = database.query(réserve).filter(
        (réserve.c.elementcentre_1 == salle_id) &
        (réserve.c.reservation_1 == reservation_id)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Relationship already exists")

    # Create the association
    association = réserve.insert().values(elementcentre_1=salle_id, reservation_1=reservation_id)
    database.execute(association)
    database.commit()

    return {"message": "Reservation added to reservation_1 successfully"}


@app.delete("/salle/{salle_id}/reservation_1/{reservation_id}/", response_model=None, tags=["Salle Relationships"])
async def remove_reservation_1_from_salle(salle_id: int, reservation_id: int, database: Session = Depends(get_db)):
    """Remove a Reservation from this Salle's reservation_1 relationship"""
    db_salle = database.query(Salle).filter(Salle.id == salle_id).first()
    if db_salle is None:
        raise HTTPException(status_code=404, detail="Salle not found")

    # Check if relationship exists
    existing = database.query(réserve).filter(
        (réserve.c.elementcentre_1 == salle_id) &
        (réserve.c.reservation_1 == reservation_id)
    ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Relationship not found")

    # Delete the association
    association = réserve.delete().where(
        (réserve.c.elementcentre_1 == salle_id) &
        (réserve.c.reservation_1 == reservation_id)
    )
    database.execute(association)
    database.commit()

    return {"message": "Reservation removed from reservation_1 successfully"}


@app.get("/salle/{salle_id}/reservation_1/", response_model=None, tags=["Salle Relationships"])
async def get_reservation_1_of_salle(salle_id: int, database: Session = Depends(get_db)):
    """Get all Reservation entities related to this Salle through reservation_1"""
    db_salle = database.query(Salle).filter(Salle.id == salle_id).first()
    if db_salle is None:
        raise HTTPException(status_code=404, detail="Salle not found")

    reservation_ids = database.query(réserve.c.reservation_1).filter(réserve.c.elementcentre_1 == salle_id).all()
    reservation_list = database.query(Reservation).filter(Reservation.id.in_([id[0] for id in reservation_ids])).all()

    return {
        "salle_id": salle_id,
        "reservation_1_count": len(reservation_list),
        "reservation_1": reservation_list
    }





############################################
#
#   Materiel functions
#
############################################

@app.get("/materiel/", response_model=None, tags=["Materiel"])
def get_all_materiel(detailed: bool = False, database: Session = Depends(get_db)) -> list:
    from sqlalchemy.orm import joinedload

    # Use detailed=true to get entities with eagerly loaded relationships (for tables with lookup columns)
    if detailed:
        # Eagerly load all relationships to avoid N+1 queries
        query = database.query(Materiel)
        query = query.options(joinedload(Materiel.centrecongres))
        materiel_list = query.all()

        # Serialize with relationships included
        result = []
        for materiel_item in materiel_list:
            item_dict = materiel_item.__dict__.copy()
            item_dict.pop('_sa_instance_state', None)

            # Add many-to-one relationships (foreign keys for lookup columns)
            if materiel_item.centrecongres:
                related_obj = materiel_item.centrecongres
                related_dict = related_obj.__dict__.copy()
                related_dict.pop('_sa_instance_state', None)
                item_dict['centrecongres'] = related_dict
            else:
                item_dict['centrecongres'] = None

            # Add many-to-many and one-to-many relationship objects (full details)
            reservation_list = database.query(Reservation).join(réserve, Reservation.id == réserve.c.reservation_1).filter(réserve.c.elementcentre_1 == materiel_item.id).all()
            item_dict['reservation_1'] = []
            for reservation_obj in reservation_list:
                reservation_dict = reservation_obj.__dict__.copy()
                reservation_dict.pop('_sa_instance_state', None)
                item_dict['reservation_1'].append(reservation_dict)
            periodeindisponibilite_list = database.query(PeriodeIndisponibilite).filter(PeriodeIndisponibilite.elementcentre_2_id == materiel_item.id).all()
            item_dict['periodeindisponibilite'] = []
            for periodeindisponibilite_obj in periodeindisponibilite_list:
                periodeindisponibilite_dict = periodeindisponibilite_obj.__dict__.copy()
                periodeindisponibilite_dict.pop('_sa_instance_state', None)
                item_dict['periodeindisponibilite'].append(periodeindisponibilite_dict)

            result.append(item_dict)
        return result
    else:
        # Default: return flat entities (faster for charts/widgets without lookup columns)
        return database.query(Materiel).all()


@app.get("/materiel/count/", response_model=None, tags=["Materiel"])
def get_count_materiel(database: Session = Depends(get_db)) -> dict:
    """Get the total count of Materiel entities"""
    count = database.query(Materiel).count()
    return {"count": count}


@app.get("/materiel/paginated/", response_model=None, tags=["Materiel"])
def get_paginated_materiel(skip: int = 0, limit: int = 100, detailed: bool = False, database: Session = Depends(get_db)) -> dict:
    """Get paginated list of Materiel entities"""
    total = database.query(Materiel).count()
    materiel_list = database.query(Materiel).offset(skip).limit(limit).all()
    # By default, return flat entities (for charts/widgets)
    # Use detailed=true to get entities with relationships
    if not detailed:
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "data": materiel_list
        }

    result = []
    for materiel_item in materiel_list:
        reservation_ids = database.query(réserve.c.reservation_1).filter(réserve.c.elementcentre_1 == materiel_item.id).all()
        periodeindisponibilite_ids = database.query(PeriodeIndisponibilite.id).filter(PeriodeIndisponibilite.elementcentre_2_id == materiel_item.id).all()
        item_data = {
            "materiel": materiel_item,
            "reservation_ids": [x[0] for x in reservation_ids],
            "periodeindisponibilite_ids": [x[0] for x in periodeindisponibilite_ids]        }
        result.append(item_data)
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": result
    }


@app.get("/materiel/search/", response_model=None, tags=["Materiel"])
def search_materiel(
    database: Session = Depends(get_db)
) -> list:
    """Search Materiel entities by attributes"""
    query = database.query(Materiel)


    results = query.all()
    return results


@app.get("/materiel/{materiel_id}/", response_model=None, tags=["Materiel"])
async def get_materiel(materiel_id: int, database: Session = Depends(get_db)) -> Materiel:
    db_materiel = database.query(Materiel).filter(Materiel.id == materiel_id).first()
    if db_materiel is None:
        raise HTTPException(status_code=404, detail="Materiel not found")

    reservation_ids = database.query(réserve.c.reservation_1).filter(réserve.c.elementcentre_1 == db_materiel.id).all()
    periodeindisponibilite_ids = database.query(PeriodeIndisponibilite.id).filter(PeriodeIndisponibilite.elementcentre_2_id == db_materiel.id).all()
    response_data = {
        "materiel": db_materiel,
        "reservation_ids": [x[0] for x in reservation_ids],
        "periodeindisponibilite_ids": [x[0] for x in periodeindisponibilite_ids]}
    return response_data



@app.post("/materiel/", response_model=None, tags=["Materiel"])
async def create_materiel(materiel_data: MaterielCreate, database: Session = Depends(get_db)) -> Materiel:

    if materiel_data.centrecongres is not None:
        db_centrecongres = database.query(CentreCongres).filter(CentreCongres.id == materiel_data.centrecongres).first()
        if not db_centrecongres:
            raise HTTPException(status_code=400, detail="CentreCongres not found")
    else:
        raise HTTPException(status_code=400, detail="CentreCongres ID is required")
    if materiel_data.reservation_1:
        for id in materiel_data.reservation_1:
            # Entity already validated before creation
            db_reservation = database.query(Reservation).filter(Reservation.id == id).first()
            if not db_reservation:
                raise HTTPException(status_code=404, detail=f"Reservation with ID {id} not found")

    db_materiel = Materiel(
        Prix=materiel_data.Prix,        type=materiel_data.type.value,        dureeMinLocation=materiel_data.dureeMinLocation,        Saison=materiel_data.Saison.value,        description=materiel_data.description,        joursDisponibles=materiel_data.joursDisponibles,        nom=materiel_data.nom,        quantiteDisponible=materiel_data.quantiteDisponible,        prixUnitaire=materiel_data.prixUnitaire,        centrecongres_id=materiel_data.centrecongres        )

    database.add(db_materiel)
    database.commit()
    database.refresh(db_materiel)

    if materiel_data.periodeindisponibilite:
        # Validate that all PeriodeIndisponibilite IDs exist
        for periodeindisponibilite_id in materiel_data.periodeindisponibilite:
            db_periodeindisponibilite = database.query(PeriodeIndisponibilite).filter(PeriodeIndisponibilite.id == periodeindisponibilite_id).first()
            if not db_periodeindisponibilite:
                raise HTTPException(status_code=400, detail=f"PeriodeIndisponibilite with id {periodeindisponibilite_id} not found")

        # Update the related entities with the new foreign key
        database.query(PeriodeIndisponibilite).filter(PeriodeIndisponibilite.id.in_(materiel_data.periodeindisponibilite)).update(
            {PeriodeIndisponibilite.elementcentre_2_id: db_materiel.id}, synchronize_session=False
        )
        database.commit()

    if materiel_data.reservation_1:
        for id in materiel_data.reservation_1:
            # Entity already validated before creation
            db_reservation = database.query(Reservation).filter(Reservation.id == id).first()
            # Create the association
            association = réserve.insert().values(elementcentre_1=db_materiel.id, reservation_1=db_reservation.id)
            database.execute(association)
            database.commit()


    reservation_ids = database.query(réserve.c.reservation_1).filter(réserve.c.elementcentre_1 == db_materiel.id).all()
    periodeindisponibilite_ids = database.query(PeriodeIndisponibilite.id).filter(PeriodeIndisponibilite.elementcentre_2_id == db_materiel.id).all()
    response_data = {
        "materiel": db_materiel,
        "reservation_ids": [x[0] for x in reservation_ids],
        "periodeindisponibilite_ids": [x[0] for x in periodeindisponibilite_ids]    }
    return response_data


@app.post("/materiel/bulk/", response_model=None, tags=["Materiel"])
async def bulk_create_materiel(items: list[MaterielCreate], database: Session = Depends(get_db)) -> dict:
    """Create multiple Materiel entities at once"""
    created_items = []
    errors = []

    for idx, item_data in enumerate(items):
        try:
            # Basic validation for each item
            if not item_data.centrecongres:
                raise ValueError("CentreCongres ID is required")

            db_materiel = Materiel(
                Prix=item_data.Prix,                type=item_data.type.value,                dureeMinLocation=item_data.dureeMinLocation,                Saison=item_data.Saison.value,                description=item_data.description,                joursDisponibles=item_data.joursDisponibles,                nom=item_data.nom,                quantiteDisponible=item_data.quantiteDisponible,                prixUnitaire=item_data.prixUnitaire,                centrecongres_id=item_data.centrecongres            )
            database.add(db_materiel)
            database.flush()  # Get ID without committing
            created_items.append(db_materiel.id)
        except Exception as e:
            errors.append({"index": idx, "error": str(e)})

    if errors:
        database.rollback()
        raise HTTPException(status_code=400, detail={"message": "Bulk creation failed", "errors": errors})

    database.commit()
    return {
        "created_count": len(created_items),
        "created_ids": created_items,
        "message": f"Successfully created {len(created_items)} Materiel entities"
    }


@app.delete("/materiel/bulk/", response_model=None, tags=["Materiel"])
async def bulk_delete_materiel(ids: list[int], database: Session = Depends(get_db)) -> dict:
    """Delete multiple Materiel entities at once"""
    deleted_count = 0
    not_found = []

    for item_id in ids:
        db_materiel = database.query(Materiel).filter(Materiel.id == item_id).first()
        if db_materiel:
            database.delete(db_materiel)
            deleted_count += 1
        else:
            not_found.append(item_id)

    database.commit()

    return {
        "deleted_count": deleted_count,
        "not_found": not_found,
        "message": f"Successfully deleted {deleted_count} Materiel entities"
    }

@app.put("/materiel/{materiel_id}/", response_model=None, tags=["Materiel"])
async def update_materiel(materiel_id: int, materiel_data: MaterielCreate, database: Session = Depends(get_db)) -> Materiel:
    db_materiel = database.query(Materiel).filter(Materiel.id == materiel_id).first()
    if db_materiel is None:
        raise HTTPException(status_code=404, detail="Materiel not found")

    setattr(db_materiel, 'quantiteDisponible', materiel_data.quantiteDisponible)
    setattr(db_materiel, 'prixUnitaire', materiel_data.prixUnitaire)
    if materiel_data.periodeindisponibilite is not None:
        # Clear all existing relationships (set foreign key to NULL)
        database.query(PeriodeIndisponibilite).filter(PeriodeIndisponibilite.elementcentre_2_id == db_materiel.id).update(
            {PeriodeIndisponibilite.elementcentre_2_id: None}, synchronize_session=False
        )

        # Set new relationships if list is not empty
        if materiel_data.periodeindisponibilite:
            # Validate that all IDs exist
            for periodeindisponibilite_id in materiel_data.periodeindisponibilite:
                db_periodeindisponibilite = database.query(PeriodeIndisponibilite).filter(PeriodeIndisponibilite.id == periodeindisponibilite_id).first()
                if not db_periodeindisponibilite:
                    raise HTTPException(status_code=400, detail=f"PeriodeIndisponibilite with id {periodeindisponibilite_id} not found")

            # Update the related entities with the new foreign key
            database.query(PeriodeIndisponibilite).filter(PeriodeIndisponibilite.id.in_(materiel_data.periodeindisponibilite)).update(
                {PeriodeIndisponibilite.elementcentre_2_id: db_materiel.id}, synchronize_session=False
            )
    existing_reservation_ids = [assoc.reservation_1 for assoc in database.execute(
        réserve.select().where(réserve.c.elementcentre_1 == db_materiel.id))]

    reservations_to_remove = set(existing_reservation_ids) - set(materiel_data.reservation_1)
    for reservation_id in reservations_to_remove:
        association = réserve.delete().where(
            (réserve.c.elementcentre_1 == db_materiel.id) & (réserve.c.reservation_1 == reservation_id))
        database.execute(association)

    new_reservation_ids = set(materiel_data.reservation_1) - set(existing_reservation_ids)
    for reservation_id in new_reservation_ids:
        db_reservation = database.query(Reservation).filter(Reservation.id == reservation_id).first()
        if db_reservation is None:
            raise HTTPException(status_code=404, detail=f"Reservation with ID {reservation_id} not found")
        association = réserve.insert().values(reservation_1=db_reservation.id, elementcentre_1=db_materiel.id)
        database.execute(association)
    database.commit()
    database.refresh(db_materiel)

    reservation_ids = database.query(réserve.c.reservation_1).filter(réserve.c.elementcentre_1 == db_materiel.id).all()
    periodeindisponibilite_ids = database.query(PeriodeIndisponibilite.id).filter(PeriodeIndisponibilite.elementcentre_2_id == db_materiel.id).all()
    response_data = {
        "materiel": db_materiel,
        "reservation_ids": [x[0] for x in reservation_ids],
        "periodeindisponibilite_ids": [x[0] for x in periodeindisponibilite_ids]    }
    return response_data


@app.delete("/materiel/{materiel_id}/", response_model=None, tags=["Materiel"])
async def delete_materiel(materiel_id: int, database: Session = Depends(get_db)):
    db_materiel = database.query(Materiel).filter(Materiel.id == materiel_id).first()
    if db_materiel is None:
        raise HTTPException(status_code=404, detail="Materiel not found")
    database.delete(db_materiel)
    database.commit()
    return db_materiel

@app.post("/materiel/{materiel_id}/reservation_1/{reservation_id}/", response_model=None, tags=["Materiel Relationships"])
async def add_reservation_1_to_materiel(materiel_id: int, reservation_id: int, database: Session = Depends(get_db)):
    """Add a Reservation to this Materiel's reservation_1 relationship"""
    db_materiel = database.query(Materiel).filter(Materiel.id == materiel_id).first()
    if db_materiel is None:
        raise HTTPException(status_code=404, detail="Materiel not found")

    db_reservation = database.query(Reservation).filter(Reservation.id == reservation_id).first()
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")

    # Check if relationship already exists
    existing = database.query(réserve).filter(
        (réserve.c.elementcentre_1 == materiel_id) &
        (réserve.c.reservation_1 == reservation_id)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Relationship already exists")

    # Create the association
    association = réserve.insert().values(elementcentre_1=materiel_id, reservation_1=reservation_id)
    database.execute(association)
    database.commit()

    return {"message": "Reservation added to reservation_1 successfully"}


@app.delete("/materiel/{materiel_id}/reservation_1/{reservation_id}/", response_model=None, tags=["Materiel Relationships"])
async def remove_reservation_1_from_materiel(materiel_id: int, reservation_id: int, database: Session = Depends(get_db)):
    """Remove a Reservation from this Materiel's reservation_1 relationship"""
    db_materiel = database.query(Materiel).filter(Materiel.id == materiel_id).first()
    if db_materiel is None:
        raise HTTPException(status_code=404, detail="Materiel not found")

    # Check if relationship exists
    existing = database.query(réserve).filter(
        (réserve.c.elementcentre_1 == materiel_id) &
        (réserve.c.reservation_1 == reservation_id)
    ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Relationship not found")

    # Delete the association
    association = réserve.delete().where(
        (réserve.c.elementcentre_1 == materiel_id) &
        (réserve.c.reservation_1 == reservation_id)
    )
    database.execute(association)
    database.commit()

    return {"message": "Reservation removed from reservation_1 successfully"}


@app.get("/materiel/{materiel_id}/reservation_1/", response_model=None, tags=["Materiel Relationships"])
async def get_reservation_1_of_materiel(materiel_id: int, database: Session = Depends(get_db)):
    """Get all Reservation entities related to this Materiel through reservation_1"""
    db_materiel = database.query(Materiel).filter(Materiel.id == materiel_id).first()
    if db_materiel is None:
        raise HTTPException(status_code=404, detail="Materiel not found")

    reservation_ids = database.query(réserve.c.reservation_1).filter(réserve.c.elementcentre_1 == materiel_id).all()
    reservation_list = database.query(Reservation).filter(Reservation.id.in_([id[0] for id in reservation_ids])).all()

    return {
        "materiel_id": materiel_id,
        "reservation_1_count": len(reservation_list),
        "reservation_1": reservation_list
    }





############################################
#
#   Prestation functions
#
############################################

@app.get("/prestation/", response_model=None, tags=["Prestation"])
def get_all_prestation(detailed: bool = False, database: Session = Depends(get_db)) -> list:
    from sqlalchemy.orm import joinedload

    # Use detailed=true to get entities with eagerly loaded relationships (for tables with lookup columns)
    if detailed:
        # Eagerly load all relationships to avoid N+1 queries
        query = database.query(Prestation)
        query = query.options(joinedload(Prestation.centrecongres))
        prestation_list = query.all()

        # Serialize with relationships included
        result = []
        for prestation_item in prestation_list:
            item_dict = prestation_item.__dict__.copy()
            item_dict.pop('_sa_instance_state', None)

            # Add many-to-one relationships (foreign keys for lookup columns)
            if prestation_item.centrecongres:
                related_obj = prestation_item.centrecongres
                related_dict = related_obj.__dict__.copy()
                related_dict.pop('_sa_instance_state', None)
                item_dict['centrecongres'] = related_dict
            else:
                item_dict['centrecongres'] = None

            # Add many-to-many and one-to-many relationship objects (full details)
            reservation_list = database.query(Reservation).join(réserve, Reservation.id == réserve.c.reservation_1).filter(réserve.c.elementcentre_1 == prestation_item.id).all()
            item_dict['reservation_1'] = []
            for reservation_obj in reservation_list:
                reservation_dict = reservation_obj.__dict__.copy()
                reservation_dict.pop('_sa_instance_state', None)
                item_dict['reservation_1'].append(reservation_dict)
            periodeindisponibilite_list = database.query(PeriodeIndisponibilite).filter(PeriodeIndisponibilite.elementcentre_2_id == prestation_item.id).all()
            item_dict['periodeindisponibilite'] = []
            for periodeindisponibilite_obj in periodeindisponibilite_list:
                periodeindisponibilite_dict = periodeindisponibilite_obj.__dict__.copy()
                periodeindisponibilite_dict.pop('_sa_instance_state', None)
                item_dict['periodeindisponibilite'].append(periodeindisponibilite_dict)

            result.append(item_dict)
        return result
    else:
        # Default: return flat entities (faster for charts/widgets without lookup columns)
        return database.query(Prestation).all()


@app.get("/prestation/count/", response_model=None, tags=["Prestation"])
def get_count_prestation(database: Session = Depends(get_db)) -> dict:
    """Get the total count of Prestation entities"""
    count = database.query(Prestation).count()
    return {"count": count}


@app.get("/prestation/paginated/", response_model=None, tags=["Prestation"])
def get_paginated_prestation(skip: int = 0, limit: int = 100, detailed: bool = False, database: Session = Depends(get_db)) -> dict:
    """Get paginated list of Prestation entities"""
    total = database.query(Prestation).count()
    prestation_list = database.query(Prestation).offset(skip).limit(limit).all()
    # By default, return flat entities (for charts/widgets)
    # Use detailed=true to get entities with relationships
    if not detailed:
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "data": prestation_list
        }

    result = []
    for prestation_item in prestation_list:
        reservation_ids = database.query(réserve.c.reservation_1).filter(réserve.c.elementcentre_1 == prestation_item.id).all()
        periodeindisponibilite_ids = database.query(PeriodeIndisponibilite.id).filter(PeriodeIndisponibilite.elementcentre_2_id == prestation_item.id).all()
        item_data = {
            "prestation": prestation_item,
            "reservation_ids": [x[0] for x in reservation_ids],
            "periodeindisponibilite_ids": [x[0] for x in periodeindisponibilite_ids]        }
        result.append(item_data)
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": result
    }


@app.get("/prestation/search/", response_model=None, tags=["Prestation"])
def search_prestation(
    database: Session = Depends(get_db)
) -> list:
    """Search Prestation entities by attributes"""
    query = database.query(Prestation)


    results = query.all()
    return results


@app.get("/prestation/{prestation_id}/", response_model=None, tags=["Prestation"])
async def get_prestation(prestation_id: int, database: Session = Depends(get_db)) -> Prestation:
    db_prestation = database.query(Prestation).filter(Prestation.id == prestation_id).first()
    if db_prestation is None:
        raise HTTPException(status_code=404, detail="Prestation not found")

    reservation_ids = database.query(réserve.c.reservation_1).filter(réserve.c.elementcentre_1 == db_prestation.id).all()
    periodeindisponibilite_ids = database.query(PeriodeIndisponibilite.id).filter(PeriodeIndisponibilite.elementcentre_2_id == db_prestation.id).all()
    response_data = {
        "prestation": db_prestation,
        "reservation_ids": [x[0] for x in reservation_ids],
        "periodeindisponibilite_ids": [x[0] for x in periodeindisponibilite_ids]}
    return response_data



@app.post("/prestation/", response_model=None, tags=["Prestation"])
async def create_prestation(prestation_data: PrestationCreate, database: Session = Depends(get_db)) -> Prestation:

    if prestation_data.centrecongres is not None:
        db_centrecongres = database.query(CentreCongres).filter(CentreCongres.id == prestation_data.centrecongres).first()
        if not db_centrecongres:
            raise HTTPException(status_code=400, detail="CentreCongres not found")
    else:
        raise HTTPException(status_code=400, detail="CentreCongres ID is required")
    if prestation_data.reservation_1:
        for id in prestation_data.reservation_1:
            # Entity already validated before creation
            db_reservation = database.query(Reservation).filter(Reservation.id == id).first()
            if not db_reservation:
                raise HTTPException(status_code=404, detail=f"Reservation with ID {id} not found")

    db_prestation = Prestation(
        Prix=prestation_data.Prix,        type=prestation_data.type.value,        dureeMinLocation=prestation_data.dureeMinLocation,        Saison=prestation_data.Saison.value,        description=prestation_data.description,        joursDisponibles=prestation_data.joursDisponibles,        nom=prestation_data.nom,        prix=prestation_data.prix,        nbMinParticipants=prestation_data.nbMinParticipants,        nbMaxParticipants=prestation_data.nbMaxParticipants,        centrecongres_id=prestation_data.centrecongres        )

    database.add(db_prestation)
    database.commit()
    database.refresh(db_prestation)

    if prestation_data.periodeindisponibilite:
        # Validate that all PeriodeIndisponibilite IDs exist
        for periodeindisponibilite_id in prestation_data.periodeindisponibilite:
            db_periodeindisponibilite = database.query(PeriodeIndisponibilite).filter(PeriodeIndisponibilite.id == periodeindisponibilite_id).first()
            if not db_periodeindisponibilite:
                raise HTTPException(status_code=400, detail=f"PeriodeIndisponibilite with id {periodeindisponibilite_id} not found")

        # Update the related entities with the new foreign key
        database.query(PeriodeIndisponibilite).filter(PeriodeIndisponibilite.id.in_(prestation_data.periodeindisponibilite)).update(
            {PeriodeIndisponibilite.elementcentre_2_id: db_prestation.id}, synchronize_session=False
        )
        database.commit()

    if prestation_data.reservation_1:
        for id in prestation_data.reservation_1:
            # Entity already validated before creation
            db_reservation = database.query(Reservation).filter(Reservation.id == id).first()
            # Create the association
            association = réserve.insert().values(elementcentre_1=db_prestation.id, reservation_1=db_reservation.id)
            database.execute(association)
            database.commit()


    reservation_ids = database.query(réserve.c.reservation_1).filter(réserve.c.elementcentre_1 == db_prestation.id).all()
    periodeindisponibilite_ids = database.query(PeriodeIndisponibilite.id).filter(PeriodeIndisponibilite.elementcentre_2_id == db_prestation.id).all()
    response_data = {
        "prestation": db_prestation,
        "reservation_ids": [x[0] for x in reservation_ids],
        "periodeindisponibilite_ids": [x[0] for x in periodeindisponibilite_ids]    }
    return response_data


@app.post("/prestation/bulk/", response_model=None, tags=["Prestation"])
async def bulk_create_prestation(items: list[PrestationCreate], database: Session = Depends(get_db)) -> dict:
    """Create multiple Prestation entities at once"""
    created_items = []
    errors = []

    for idx, item_data in enumerate(items):
        try:
            # Basic validation for each item
            if not item_data.centrecongres:
                raise ValueError("CentreCongres ID is required")

            db_prestation = Prestation(
                Prix=item_data.Prix,                type=item_data.type.value,                dureeMinLocation=item_data.dureeMinLocation,                Saison=item_data.Saison.value,                description=item_data.description,                joursDisponibles=item_data.joursDisponibles,                nom=item_data.nom,                prix=item_data.prix,                nbMinParticipants=item_data.nbMinParticipants,                nbMaxParticipants=item_data.nbMaxParticipants,                centrecongres_id=item_data.centrecongres            )
            database.add(db_prestation)
            database.flush()  # Get ID without committing
            created_items.append(db_prestation.id)
        except Exception as e:
            errors.append({"index": idx, "error": str(e)})

    if errors:
        database.rollback()
        raise HTTPException(status_code=400, detail={"message": "Bulk creation failed", "errors": errors})

    database.commit()
    return {
        "created_count": len(created_items),
        "created_ids": created_items,
        "message": f"Successfully created {len(created_items)} Prestation entities"
    }


@app.delete("/prestation/bulk/", response_model=None, tags=["Prestation"])
async def bulk_delete_prestation(ids: list[int], database: Session = Depends(get_db)) -> dict:
    """Delete multiple Prestation entities at once"""
    deleted_count = 0
    not_found = []

    for item_id in ids:
        db_prestation = database.query(Prestation).filter(Prestation.id == item_id).first()
        if db_prestation:
            database.delete(db_prestation)
            deleted_count += 1
        else:
            not_found.append(item_id)

    database.commit()

    return {
        "deleted_count": deleted_count,
        "not_found": not_found,
        "message": f"Successfully deleted {deleted_count} Prestation entities"
    }

@app.put("/prestation/{prestation_id}/", response_model=None, tags=["Prestation"])
async def update_prestation(prestation_id: int, prestation_data: PrestationCreate, database: Session = Depends(get_db)) -> Prestation:
    db_prestation = database.query(Prestation).filter(Prestation.id == prestation_id).first()
    if db_prestation is None:
        raise HTTPException(status_code=404, detail="Prestation not found")

    setattr(db_prestation, 'prix', prestation_data.prix)
    setattr(db_prestation, 'nbMinParticipants', prestation_data.nbMinParticipants)
    setattr(db_prestation, 'nbMaxParticipants', prestation_data.nbMaxParticipants)
    if prestation_data.periodeindisponibilite is not None:
        # Clear all existing relationships (set foreign key to NULL)
        database.query(PeriodeIndisponibilite).filter(PeriodeIndisponibilite.elementcentre_2_id == db_prestation.id).update(
            {PeriodeIndisponibilite.elementcentre_2_id: None}, synchronize_session=False
        )

        # Set new relationships if list is not empty
        if prestation_data.periodeindisponibilite:
            # Validate that all IDs exist
            for periodeindisponibilite_id in prestation_data.periodeindisponibilite:
                db_periodeindisponibilite = database.query(PeriodeIndisponibilite).filter(PeriodeIndisponibilite.id == periodeindisponibilite_id).first()
                if not db_periodeindisponibilite:
                    raise HTTPException(status_code=400, detail=f"PeriodeIndisponibilite with id {periodeindisponibilite_id} not found")

            # Update the related entities with the new foreign key
            database.query(PeriodeIndisponibilite).filter(PeriodeIndisponibilite.id.in_(prestation_data.periodeindisponibilite)).update(
                {PeriodeIndisponibilite.elementcentre_2_id: db_prestation.id}, synchronize_session=False
            )
    existing_reservation_ids = [assoc.reservation_1 for assoc in database.execute(
        réserve.select().where(réserve.c.elementcentre_1 == db_prestation.id))]

    reservations_to_remove = set(existing_reservation_ids) - set(prestation_data.reservation_1)
    for reservation_id in reservations_to_remove:
        association = réserve.delete().where(
            (réserve.c.elementcentre_1 == db_prestation.id) & (réserve.c.reservation_1 == reservation_id))
        database.execute(association)

    new_reservation_ids = set(prestation_data.reservation_1) - set(existing_reservation_ids)
    for reservation_id in new_reservation_ids:
        db_reservation = database.query(Reservation).filter(Reservation.id == reservation_id).first()
        if db_reservation is None:
            raise HTTPException(status_code=404, detail=f"Reservation with ID {reservation_id} not found")
        association = réserve.insert().values(reservation_1=db_reservation.id, elementcentre_1=db_prestation.id)
        database.execute(association)
    database.commit()
    database.refresh(db_prestation)

    reservation_ids = database.query(réserve.c.reservation_1).filter(réserve.c.elementcentre_1 == db_prestation.id).all()
    periodeindisponibilite_ids = database.query(PeriodeIndisponibilite.id).filter(PeriodeIndisponibilite.elementcentre_2_id == db_prestation.id).all()
    response_data = {
        "prestation": db_prestation,
        "reservation_ids": [x[0] for x in reservation_ids],
        "periodeindisponibilite_ids": [x[0] for x in periodeindisponibilite_ids]    }
    return response_data


@app.delete("/prestation/{prestation_id}/", response_model=None, tags=["Prestation"])
async def delete_prestation(prestation_id: int, database: Session = Depends(get_db)):
    db_prestation = database.query(Prestation).filter(Prestation.id == prestation_id).first()
    if db_prestation is None:
        raise HTTPException(status_code=404, detail="Prestation not found")
    database.delete(db_prestation)
    database.commit()
    return db_prestation

@app.post("/prestation/{prestation_id}/reservation_1/{reservation_id}/", response_model=None, tags=["Prestation Relationships"])
async def add_reservation_1_to_prestation(prestation_id: int, reservation_id: int, database: Session = Depends(get_db)):
    """Add a Reservation to this Prestation's reservation_1 relationship"""
    db_prestation = database.query(Prestation).filter(Prestation.id == prestation_id).first()
    if db_prestation is None:
        raise HTTPException(status_code=404, detail="Prestation not found")

    db_reservation = database.query(Reservation).filter(Reservation.id == reservation_id).first()
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")

    # Check if relationship already exists
    existing = database.query(réserve).filter(
        (réserve.c.elementcentre_1 == prestation_id) &
        (réserve.c.reservation_1 == reservation_id)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Relationship already exists")

    # Create the association
    association = réserve.insert().values(elementcentre_1=prestation_id, reservation_1=reservation_id)
    database.execute(association)
    database.commit()

    return {"message": "Reservation added to reservation_1 successfully"}


@app.delete("/prestation/{prestation_id}/reservation_1/{reservation_id}/", response_model=None, tags=["Prestation Relationships"])
async def remove_reservation_1_from_prestation(prestation_id: int, reservation_id: int, database: Session = Depends(get_db)):
    """Remove a Reservation from this Prestation's reservation_1 relationship"""
    db_prestation = database.query(Prestation).filter(Prestation.id == prestation_id).first()
    if db_prestation is None:
        raise HTTPException(status_code=404, detail="Prestation not found")

    # Check if relationship exists
    existing = database.query(réserve).filter(
        (réserve.c.elementcentre_1 == prestation_id) &
        (réserve.c.reservation_1 == reservation_id)
    ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Relationship not found")

    # Delete the association
    association = réserve.delete().where(
        (réserve.c.elementcentre_1 == prestation_id) &
        (réserve.c.reservation_1 == reservation_id)
    )
    database.execute(association)
    database.commit()

    return {"message": "Reservation removed from reservation_1 successfully"}


@app.get("/prestation/{prestation_id}/reservation_1/", response_model=None, tags=["Prestation Relationships"])
async def get_reservation_1_of_prestation(prestation_id: int, database: Session = Depends(get_db)):
    """Get all Reservation entities related to this Prestation through reservation_1"""
    db_prestation = database.query(Prestation).filter(Prestation.id == prestation_id).first()
    if db_prestation is None:
        raise HTTPException(status_code=404, detail="Prestation not found")

    reservation_ids = database.query(réserve.c.reservation_1).filter(réserve.c.elementcentre_1 == prestation_id).all()
    reservation_list = database.query(Reservation).filter(Reservation.id.in_([id[0] for id in reservation_ids])).all()

    return {
        "prestation_id": prestation_id,
        "reservation_1_count": len(reservation_list),
        "reservation_1": reservation_list
    }





############################################
#
#   Gestionnaire functions
#
############################################

@app.get("/gestionnaire/", response_model=None, tags=["Gestionnaire"])
def get_all_gestionnaire(detailed: bool = False, database: Session = Depends(get_db)) -> list:
    from sqlalchemy.orm import joinedload

    # Use detailed=true to get entities with eagerly loaded relationships (for tables with lookup columns)
    if detailed:
        # Eagerly load all relationships to avoid N+1 queries
        query = database.query(Gestionnaire)
        gestionnaire_list = query.all()

        # Serialize with relationships included
        result = []
        for gestionnaire_item in gestionnaire_list:
            item_dict = gestionnaire_item.__dict__.copy()
            item_dict.pop('_sa_instance_state', None)

            # Add many-to-one relationships (foreign keys for lookup columns)

            # Add many-to-many and one-to-many relationship objects (full details)
            reservation_list = database.query(Reservation).filter(Reservation.gestionnaire_id == gestionnaire_item.id).all()
            item_dict['reservation_2'] = []
            for reservation_obj in reservation_list:
                reservation_dict = reservation_obj.__dict__.copy()
                reservation_dict.pop('_sa_instance_state', None)
                item_dict['reservation_2'].append(reservation_dict)

            result.append(item_dict)
        return result
    else:
        # Default: return flat entities (faster for charts/widgets without lookup columns)
        return database.query(Gestionnaire).all()


@app.get("/gestionnaire/count/", response_model=None, tags=["Gestionnaire"])
def get_count_gestionnaire(database: Session = Depends(get_db)) -> dict:
    """Get the total count of Gestionnaire entities"""
    count = database.query(Gestionnaire).count()
    return {"count": count}


@app.get("/gestionnaire/paginated/", response_model=None, tags=["Gestionnaire"])
def get_paginated_gestionnaire(skip: int = 0, limit: int = 100, detailed: bool = False, database: Session = Depends(get_db)) -> dict:
    """Get paginated list of Gestionnaire entities"""
    total = database.query(Gestionnaire).count()
    gestionnaire_list = database.query(Gestionnaire).offset(skip).limit(limit).all()
    # By default, return flat entities (for charts/widgets)
    # Use detailed=true to get entities with relationships
    if not detailed:
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "data": gestionnaire_list
        }

    result = []
    for gestionnaire_item in gestionnaire_list:
        reservation_2_ids = database.query(Reservation.id).filter(Reservation.gestionnaire_id == gestionnaire_item.id).all()
        item_data = {
            "gestionnaire": gestionnaire_item,
            "reservation_2_ids": [x[0] for x in reservation_2_ids]        }
        result.append(item_data)
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": result
    }


@app.get("/gestionnaire/search/", response_model=None, tags=["Gestionnaire"])
def search_gestionnaire(
    database: Session = Depends(get_db)
) -> list:
    """Search Gestionnaire entities by attributes"""
    query = database.query(Gestionnaire)


    results = query.all()
    return results


@app.get("/gestionnaire/{gestionnaire_id}/", response_model=None, tags=["Gestionnaire"])
async def get_gestionnaire(gestionnaire_id: int, database: Session = Depends(get_db)) -> Gestionnaire:
    db_gestionnaire = database.query(Gestionnaire).filter(Gestionnaire.id == gestionnaire_id).first()
    if db_gestionnaire is None:
        raise HTTPException(status_code=404, detail="Gestionnaire not found")

    reservation_2_ids = database.query(Reservation.id).filter(Reservation.gestionnaire_id == db_gestionnaire.id).all()
    response_data = {
        "gestionnaire": db_gestionnaire,
        "reservation_2_ids": [x[0] for x in reservation_2_ids]}
    return response_data



@app.post("/gestionnaire/", response_model=None, tags=["Gestionnaire"])
async def create_gestionnaire(gestionnaire_data: GestionnaireCreate, database: Session = Depends(get_db)) -> Gestionnaire:


    db_gestionnaire = Gestionnaire(
        nom=gestionnaire_data.nom,        email=gestionnaire_data.email        )

    database.add(db_gestionnaire)
    database.commit()
    database.refresh(db_gestionnaire)

    if gestionnaire_data.reservation_2:
        # Validate that all Reservation IDs exist
        for reservation_id in gestionnaire_data.reservation_2:
            db_reservation = database.query(Reservation).filter(Reservation.id == reservation_id).first()
            if not db_reservation:
                raise HTTPException(status_code=400, detail=f"Reservation with id {reservation_id} not found")

        # Update the related entities with the new foreign key
        database.query(Reservation).filter(Reservation.id.in_(gestionnaire_data.reservation_2)).update(
            {Reservation.gestionnaire_id: db_gestionnaire.id}, synchronize_session=False
        )
        database.commit()



    reservation_2_ids = database.query(Reservation.id).filter(Reservation.gestionnaire_id == db_gestionnaire.id).all()
    response_data = {
        "gestionnaire": db_gestionnaire,
        "reservation_2_ids": [x[0] for x in reservation_2_ids]    }
    return response_data


@app.post("/gestionnaire/bulk/", response_model=None, tags=["Gestionnaire"])
async def bulk_create_gestionnaire(items: list[GestionnaireCreate], database: Session = Depends(get_db)) -> dict:
    """Create multiple Gestionnaire entities at once"""
    created_items = []
    errors = []

    for idx, item_data in enumerate(items):
        try:
            # Basic validation for each item

            db_gestionnaire = Gestionnaire(
                nom=item_data.nom,                email=item_data.email            )
            database.add(db_gestionnaire)
            database.flush()  # Get ID without committing
            created_items.append(db_gestionnaire.id)
        except Exception as e:
            errors.append({"index": idx, "error": str(e)})

    if errors:
        database.rollback()
        raise HTTPException(status_code=400, detail={"message": "Bulk creation failed", "errors": errors})

    database.commit()
    return {
        "created_count": len(created_items),
        "created_ids": created_items,
        "message": f"Successfully created {len(created_items)} Gestionnaire entities"
    }


@app.delete("/gestionnaire/bulk/", response_model=None, tags=["Gestionnaire"])
async def bulk_delete_gestionnaire(ids: list[int], database: Session = Depends(get_db)) -> dict:
    """Delete multiple Gestionnaire entities at once"""
    deleted_count = 0
    not_found = []

    for item_id in ids:
        db_gestionnaire = database.query(Gestionnaire).filter(Gestionnaire.id == item_id).first()
        if db_gestionnaire:
            database.delete(db_gestionnaire)
            deleted_count += 1
        else:
            not_found.append(item_id)

    database.commit()

    return {
        "deleted_count": deleted_count,
        "not_found": not_found,
        "message": f"Successfully deleted {deleted_count} Gestionnaire entities"
    }

@app.put("/gestionnaire/{gestionnaire_id}/", response_model=None, tags=["Gestionnaire"])
async def update_gestionnaire(gestionnaire_id: int, gestionnaire_data: GestionnaireCreate, database: Session = Depends(get_db)) -> Gestionnaire:
    db_gestionnaire = database.query(Gestionnaire).filter(Gestionnaire.id == gestionnaire_id).first()
    if db_gestionnaire is None:
        raise HTTPException(status_code=404, detail="Gestionnaire not found")

    setattr(db_gestionnaire, 'nom', gestionnaire_data.nom)
    setattr(db_gestionnaire, 'email', gestionnaire_data.email)
    if gestionnaire_data.reservation_2 is not None:
        # Clear all existing relationships (set foreign key to NULL)
        database.query(Reservation).filter(Reservation.gestionnaire_id == db_gestionnaire.id).update(
            {Reservation.gestionnaire_id: None}, synchronize_session=False
        )

        # Set new relationships if list is not empty
        if gestionnaire_data.reservation_2:
            # Validate that all IDs exist
            for reservation_id in gestionnaire_data.reservation_2:
                db_reservation = database.query(Reservation).filter(Reservation.id == reservation_id).first()
                if not db_reservation:
                    raise HTTPException(status_code=400, detail=f"Reservation with id {reservation_id} not found")

            # Update the related entities with the new foreign key
            database.query(Reservation).filter(Reservation.id.in_(gestionnaire_data.reservation_2)).update(
                {Reservation.gestionnaire_id: db_gestionnaire.id}, synchronize_session=False
            )
    database.commit()
    database.refresh(db_gestionnaire)

    reservation_2_ids = database.query(Reservation.id).filter(Reservation.gestionnaire_id == db_gestionnaire.id).all()
    response_data = {
        "gestionnaire": db_gestionnaire,
        "reservation_2_ids": [x[0] for x in reservation_2_ids]    }
    return response_data


@app.delete("/gestionnaire/{gestionnaire_id}/", response_model=None, tags=["Gestionnaire"])
async def delete_gestionnaire(gestionnaire_id: int, database: Session = Depends(get_db)):
    db_gestionnaire = database.query(Gestionnaire).filter(Gestionnaire.id == gestionnaire_id).first()
    if db_gestionnaire is None:
        raise HTTPException(status_code=404, detail="Gestionnaire not found")
    database.delete(db_gestionnaire)
    database.commit()
    return db_gestionnaire



############################################
#   Gestionnaire Method Endpoints
############################################




@app.post("/gestionnaire/{gestionnaire_id}/methods/annulerReservation/", response_model=None, tags=["Gestionnaire Methods"])
async def execute_gestionnaire_annulerReservation(
    gestionnaire_id: int,
    params: dict = Body(default=None, embed=True),
    database: Session = Depends(get_db)
):
    """
    Execute the annulerReservation method on a Gestionnaire instance.
    """
    # Retrieve the entity from the database
    _gestionnaire_object = database.query(Gestionnaire).filter(Gestionnaire.id == gestionnaire_id).first()
    if _gestionnaire_object is None:
        raise HTTPException(status_code=404, detail="Gestionnaire not found")

    # Prepare method parameters

    # Execute the method
    try:
        # Capture stdout to include print outputs in the response
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output

        async def wrapper(_gestionnaire_object):
            """Add your docstring here."""
            # Add your implementation here
            if date.today() < reservation.dateDebut:
                reservation.statut = StatutReservation.ANNULEE

        result = await wrapper(_gestionnaire_object)
        # Commit DB
        database.commit()
        database.refresh(_gestionnaire_object)

        # Restore stdout
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        return {
            "gestionnaire_id": gestionnaire_id,
            "method": "annulerReservation",
            "status": "executed",
            "result": str(result) if result is not None else None,
            "output": output if output else None
        }
    except Exception as e:
        sys.stdout = sys.__stdout__
        raise HTTPException(status_code=500, detail=f"Method execution failed: {str(e)}")





@app.post("/gestionnaire/{gestionnaire_id}/methods/getStatistiques/", response_model=None, tags=["Gestionnaire Methods"])
async def execute_gestionnaire_getStatistiques(
    gestionnaire_id: int,
    params: dict = Body(default=None, embed=True),
    database: Session = Depends(get_db)
):
    """
    Execute the getStatistiques method on a Gestionnaire instance.
    """
    # Retrieve the entity from the database
    _gestionnaire_object = database.query(Gestionnaire).filter(Gestionnaire.id == gestionnaire_id).first()
    if _gestionnaire_object is None:
        raise HTTPException(status_code=404, detail="Gestionnaire not found")

    # Prepare method parameters

    # Execute the method
    try:
        # Capture stdout to include print outputs in the response
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output

        async def wrapper(_gestionnaire_object):
            """Add your docstring here."""
            # Add your implementation here
            total = len(_gestionnaire_object.reservations)
        confirmees = sum(1 for r in _gestionnaire_object.reservations if r.statut == StatutReservation.CONFIRMEE)
        annulees = sum(1 for r in _gestionnaire_object.reservations if r.statut == StatutReservation.ANNULEE)
        chiffre_affaires = sum(r.montantTotal for r in _gestionnaire_object.reservations if r.statut == StatutReservation.CONFIRMEE)
        return {
            "total": total,
            "confirmees": confirmees,
            "annulees": annulees,
            "chiffre_affaires": chiffre_affaires
        }


        result = await wrapper(_gestionnaire_object)
        # Commit DB
        database.commit()
        database.refresh(_gestionnaire_object)

        # Restore stdout
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        return {
            "gestionnaire_id": gestionnaire_id,
            "method": "getStatistiques",
            "status": "executed",
            "result": str(result) if result is not None else None,
            "output": output if output else None
        }
    except Exception as e:
        sys.stdout = sys.__stdout__
        raise HTTPException(status_code=500, detail=f"Method execution failed: {str(e)}")





@app.post("/gestionnaire/methods/creerReservation/", response_model=None, tags=["Gestionnaire Methods"])
async def gestionnaire_creerReservation(
    database: Session = Depends(get_db)
):
    """
    Execute the creerReservation class method on Gestionnaire.
    This method operates on all Gestionnaire entities or performs class-level operations.
    """
    try:
        # Capture stdout to include print outputs in the response
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output


        # Method body not defined
        result = None

        # Restore stdout
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        # Handle result serialization
        if hasattr(result, '__iter__') and not isinstance(result, (str, dict)):
            # It's a list of entities
            result_data = []
            for item in result:
                if hasattr(item, '__dict__'):
                    item_dict = {k: v for k, v in item.__dict__.items() if not k.startswith('_')}
                    result_data.append(item_dict)
                else:
                    result_data.append(str(item))
            result = result_data
        elif hasattr(result, '__dict__'):
            result = {k: v for k, v in result.__dict__.items() if not k.startswith('_')}

        return {
            "class": "Gestionnaire",
            "method": "creerReservation",
            "status": "executed",
            "result": result,
            "output": output if output else None
        }
    except Exception as e:
        sys.stdout = sys.__stdout__
        raise HTTPException(status_code=500, detail=f"Method execution failed: {str(e)}")






@app.post("/gestionnaire/{gestionnaire_id}/methods/modifierReservation/", response_model=None, tags=["Gestionnaire Methods"])
async def execute_gestionnaire_modifierReservation(
    gestionnaire_id: int,
    params: dict = Body(default=None, embed=True),
    database: Session = Depends(get_db)
):
    """
    Execute the modifierReservation method on a Gestionnaire instance.
    """
    # Retrieve the entity from the database
    _gestionnaire_object = database.query(Gestionnaire).filter(Gestionnaire.id == gestionnaire_id).first()
    if _gestionnaire_object is None:
        raise HTTPException(status_code=404, detail="Gestionnaire not found")

    # Prepare method parameters

    # Execute the method
    try:
        # Capture stdout to include print outputs in the response
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output

        async def wrapper(_gestionnaire_object):
            """Add your docstring here."""
            # Add your implementation here
            pass


        result = await wrapper(_gestionnaire_object)
        # Commit DB
        database.commit()
        database.refresh(_gestionnaire_object)

        # Restore stdout
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        return {
            "gestionnaire_id": gestionnaire_id,
            "method": "modifierReservation",
            "status": "executed",
            "result": str(result) if result is not None else None,
            "output": output if output else None
        }
    except Exception as e:
        sys.stdout = sys.__stdout__
        raise HTTPException(status_code=500, detail=f"Method execution failed: {str(e)}")



############################################
#
#   CentreCongres functions
#
############################################

@app.get("/centrecongres/", response_model=None, tags=["CentreCongres"])
def get_all_centrecongres(detailed: bool = False, database: Session = Depends(get_db)) -> list:
    from sqlalchemy.orm import joinedload

    # Use detailed=true to get entities with eagerly loaded relationships (for tables with lookup columns)
    if detailed:
        # Eagerly load all relationships to avoid N+1 queries
        query = database.query(CentreCongres)
        centrecongres_list = query.all()

        # Serialize with relationships included
        result = []
        for centrecongres_item in centrecongres_list:
            item_dict = centrecongres_item.__dict__.copy()
            item_dict.pop('_sa_instance_state', None)

            # Add many-to-one relationships (foreign keys for lookup columns)

            # Add many-to-many and one-to-many relationship objects (full details)
            elementcentre_list = database.query(ElementCentre).filter(ElementCentre.centrecongres_id == centrecongres_item.id).all()
            item_dict['elementcentre'] = []
            for elementcentre_obj in elementcentre_list:
                elementcentre_dict = elementcentre_obj.__dict__.copy()
                elementcentre_dict.pop('_sa_instance_state', None)
                item_dict['elementcentre'].append(elementcentre_dict)

            result.append(item_dict)
        return result
    else:
        # Default: return flat entities (faster for charts/widgets without lookup columns)
        return database.query(CentreCongres).all()


@app.get("/centrecongres/count/", response_model=None, tags=["CentreCongres"])
def get_count_centrecongres(database: Session = Depends(get_db)) -> dict:
    """Get the total count of CentreCongres entities"""
    count = database.query(CentreCongres).count()
    return {"count": count}


@app.get("/centrecongres/paginated/", response_model=None, tags=["CentreCongres"])
def get_paginated_centrecongres(skip: int = 0, limit: int = 100, detailed: bool = False, database: Session = Depends(get_db)) -> dict:
    """Get paginated list of CentreCongres entities"""
    total = database.query(CentreCongres).count()
    centrecongres_list = database.query(CentreCongres).offset(skip).limit(limit).all()
    # By default, return flat entities (for charts/widgets)
    # Use detailed=true to get entities with relationships
    if not detailed:
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "data": centrecongres_list
        }

    result = []
    for centrecongres_item in centrecongres_list:
        elementcentre_ids = database.query(ElementCentre.id).filter(ElementCentre.centrecongres_id == centrecongres_item.id).all()
        item_data = {
            "centrecongres": centrecongres_item,
            "elementcentre_ids": [x[0] for x in elementcentre_ids]        }
        result.append(item_data)
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": result
    }


@app.get("/centrecongres/search/", response_model=None, tags=["CentreCongres"])
def search_centrecongres(
    database: Session = Depends(get_db)
) -> list:
    """Search CentreCongres entities by attributes"""
    query = database.query(CentreCongres)


    results = query.all()
    return results


@app.get("/centrecongres/{centrecongres_id}/", response_model=None, tags=["CentreCongres"])
async def get_centrecongres(centrecongres_id: int, database: Session = Depends(get_db)) -> CentreCongres:
    db_centrecongres = database.query(CentreCongres).filter(CentreCongres.id == centrecongres_id).first()
    if db_centrecongres is None:
        raise HTTPException(status_code=404, detail="CentreCongres not found")

    elementcentre_ids = database.query(ElementCentre.id).filter(ElementCentre.centrecongres_id == db_centrecongres.id).all()
    response_data = {
        "centrecongres": db_centrecongres,
        "elementcentre_ids": [x[0] for x in elementcentre_ids]}
    return response_data



@app.post("/centrecongres/", response_model=None, tags=["CentreCongres"])
async def create_centrecongres(centrecongres_data: CentreCongresCreate, database: Session = Depends(get_db)) -> CentreCongres:


    db_centrecongres = CentreCongres(
        adresse=centrecongres_data.adresse,        nom=centrecongres_data.nom        )

    database.add(db_centrecongres)
    database.commit()
    database.refresh(db_centrecongres)

    if centrecongres_data.elementcentre:
        # Validate that all ElementCentre IDs exist
        for elementcentre_id in centrecongres_data.elementcentre:
            db_elementcentre = database.query(ElementCentre).filter(ElementCentre.id == elementcentre_id).first()
            if not db_elementcentre:
                raise HTTPException(status_code=400, detail=f"ElementCentre with id {elementcentre_id} not found")

        # Update the related entities with the new foreign key
        database.query(ElementCentre).filter(ElementCentre.id.in_(centrecongres_data.elementcentre)).update(
            {ElementCentre.centrecongres_id: db_centrecongres.id}, synchronize_session=False
        )
        database.commit()



    elementcentre_ids = database.query(ElementCentre.id).filter(ElementCentre.centrecongres_id == db_centrecongres.id).all()
    response_data = {
        "centrecongres": db_centrecongres,
        "elementcentre_ids": [x[0] for x in elementcentre_ids]    }
    return response_data


@app.post("/centrecongres/bulk/", response_model=None, tags=["CentreCongres"])
async def bulk_create_centrecongres(items: list[CentreCongresCreate], database: Session = Depends(get_db)) -> dict:
    """Create multiple CentreCongres entities at once"""
    created_items = []
    errors = []

    for idx, item_data in enumerate(items):
        try:
            # Basic validation for each item

            db_centrecongres = CentreCongres(
                adresse=item_data.adresse,                nom=item_data.nom            )
            database.add(db_centrecongres)
            database.flush()  # Get ID without committing
            created_items.append(db_centrecongres.id)
        except Exception as e:
            errors.append({"index": idx, "error": str(e)})

    if errors:
        database.rollback()
        raise HTTPException(status_code=400, detail={"message": "Bulk creation failed", "errors": errors})

    database.commit()
    return {
        "created_count": len(created_items),
        "created_ids": created_items,
        "message": f"Successfully created {len(created_items)} CentreCongres entities"
    }


@app.delete("/centrecongres/bulk/", response_model=None, tags=["CentreCongres"])
async def bulk_delete_centrecongres(ids: list[int], database: Session = Depends(get_db)) -> dict:
    """Delete multiple CentreCongres entities at once"""
    deleted_count = 0
    not_found = []

    for item_id in ids:
        db_centrecongres = database.query(CentreCongres).filter(CentreCongres.id == item_id).first()
        if db_centrecongres:
            database.delete(db_centrecongres)
            deleted_count += 1
        else:
            not_found.append(item_id)

    database.commit()

    return {
        "deleted_count": deleted_count,
        "not_found": not_found,
        "message": f"Successfully deleted {deleted_count} CentreCongres entities"
    }

@app.put("/centrecongres/{centrecongres_id}/", response_model=None, tags=["CentreCongres"])
async def update_centrecongres(centrecongres_id: int, centrecongres_data: CentreCongresCreate, database: Session = Depends(get_db)) -> CentreCongres:
    db_centrecongres = database.query(CentreCongres).filter(CentreCongres.id == centrecongres_id).first()
    if db_centrecongres is None:
        raise HTTPException(status_code=404, detail="CentreCongres not found")

    setattr(db_centrecongres, 'adresse', centrecongres_data.adresse)
    setattr(db_centrecongres, 'nom', centrecongres_data.nom)
    if centrecongres_data.elementcentre is not None:
        # Clear all existing relationships (set foreign key to NULL)
        database.query(ElementCentre).filter(ElementCentre.centrecongres_id == db_centrecongres.id).update(
            {ElementCentre.centrecongres_id: None}, synchronize_session=False
        )

        # Set new relationships if list is not empty
        if centrecongres_data.elementcentre:
            # Validate that all IDs exist
            for elementcentre_id in centrecongres_data.elementcentre:
                db_elementcentre = database.query(ElementCentre).filter(ElementCentre.id == elementcentre_id).first()
                if not db_elementcentre:
                    raise HTTPException(status_code=400, detail=f"ElementCentre with id {elementcentre_id} not found")

            # Update the related entities with the new foreign key
            database.query(ElementCentre).filter(ElementCentre.id.in_(centrecongres_data.elementcentre)).update(
                {ElementCentre.centrecongres_id: db_centrecongres.id}, synchronize_session=False
            )
    database.commit()
    database.refresh(db_centrecongres)

    elementcentre_ids = database.query(ElementCentre.id).filter(ElementCentre.centrecongres_id == db_centrecongres.id).all()
    response_data = {
        "centrecongres": db_centrecongres,
        "elementcentre_ids": [x[0] for x in elementcentre_ids]    }
    return response_data


@app.delete("/centrecongres/{centrecongres_id}/", response_model=None, tags=["CentreCongres"])
async def delete_centrecongres(centrecongres_id: int, database: Session = Depends(get_db)):
    db_centrecongres = database.query(CentreCongres).filter(CentreCongres.id == centrecongres_id).first()
    if db_centrecongres is None:
        raise HTTPException(status_code=404, detail="CentreCongres not found")
    database.delete(db_centrecongres)
    database.commit()
    return db_centrecongres



############################################
#   CentreCongres Method Endpoints
############################################




@app.post("/centrecongres/methods/getDisponibilites/", response_model=None, tags=["CentreCongres Methods"])
async def centrecongres_getDisponibilites(
    database: Session = Depends(get_db)
):
    """
    Execute the getDisponibilites class method on CentreCongres.
    This method operates on all CentreCongres entities or performs class-level operations.
    """
    try:
        # Capture stdout to include print outputs in the response
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output


        # Method body not defined
        result = None

        # Restore stdout
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        # Handle result serialization
        if hasattr(result, '__iter__') and not isinstance(result, (str, dict)):
            # It's a list of entities
            result_data = []
            for item in result:
                if hasattr(item, '__dict__'):
                    item_dict = {k: v for k, v in item.__dict__.items() if not k.startswith('_')}
                    result_data.append(item_dict)
                else:
                    result_data.append(str(item))
            result = result_data
        elif hasattr(result, '__dict__'):
            result = {k: v for k, v in result.__dict__.items() if not k.startswith('_')}

        return {
            "class": "CentreCongres",
            "method": "getDisponibilites",
            "status": "executed",
            "result": result,
            "output": output if output else None
        }
    except Exception as e:
        sys.stdout = sys.__stdout__
        raise HTTPException(status_code=500, detail=f"Method execution failed: {str(e)}")






############################################
# Maintaining the server
############################################
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



