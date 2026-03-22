import enum
from typing import List, Optional
from sqlalchemy import (
    create_engine, Column, ForeignKey, Table, Text, Boolean, String, Date, 
    Time, DateTime, Float, Integer, Enum
)
from sqlalchemy.ext.declarative import AbstractConcreteBase
from sqlalchemy.orm import (
    column_property, DeclarativeBase, Mapped, mapped_column, relationship
)
from datetime import datetime as dt_datetime, time as dt_time, date as dt_date

class Base(DeclarativeBase):
    pass

# Definitions of Enumerations
class StatutReservation(enum.Enum):
    ANNULEE = "ANNULEE"
    TERMINEE = "TERMINEE"
    CONFIRMEE = "CONFIRMEE"
    EN_ATTENTE = "EN_ATTENTE"

class TypeElement(enum.Enum):
    SALLE_CONF = "SALLE_CONF"
    AUTRE = "AUTRE"
    RESTAURATION = "RESTAURATION"
    AMPHI = "AMPHI"

class Saison(enum.Enum):
    HAUTE = "HAUTE"
    BASSE = "BASSE"
    MOYENNE = "MOYENNE"


# Tables definition for many-to-many relationships
réserve = Table(
    "réserve",
    Base.metadata,
    Column("reservation_1", ForeignKey("reservation.id"), primary_key=True),
    Column("elementcentre_1", ForeignKey("elementcentre.id"), primary_key=True),
)

# Tables definition
class Evenement(Base):
    __tablename__ = "evenement"
    id: Mapped[int] = mapped_column(primary_key=True)
    emailReferent: Mapped[str] = mapped_column(String(100))
    dateDebut: Mapped[dt_date] = mapped_column(Date)
    dateFin: Mapped[dt_date] = mapped_column(Date)
    nom: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(100))
    nbParticipantsPrevus: Mapped[int] = mapped_column(Integer)

class PeriodeIndisponibilite(Base):
    __tablename__ = "periodeindisponibilite"
    id: Mapped[int] = mapped_column(primary_key=True)
    dateDebut: Mapped[dt_date] = mapped_column(Date)
    dateFin: Mapped[dt_date] = mapped_column(Date)
    motif: Mapped[str] = mapped_column(String(100))
    elementcentre_2_id: Mapped[int] = mapped_column(ForeignKey("elementcentre.id"))

class Reservation(Base):
    __tablename__ = "reservation"
    id: Mapped[int] = mapped_column(primary_key=True)
    dateDebut: Mapped[dt_date] = mapped_column(Date)
    dateFin: Mapped[dt_date] = mapped_column(Date)
    statut: Mapped[StatutReservation] = mapped_column(Enum(StatutReservation))
    heureMaxPaye: Mapped[dt_datetime] = mapped_column(DateTime)
    montantTotal: Mapped[float] = mapped_column(Float)
    gestionnaire_id: Mapped[int] = mapped_column(ForeignKey("gestionnaire.id"))
    evenement_id: Mapped[int] = mapped_column(ForeignKey("evenement.id"))

class ElementCentre(Base):
    __tablename__ = "elementcentre"
    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(100))
    type: Mapped[TypeElement] = mapped_column(Enum(TypeElement))
    dureeMinLocation: Mapped[int] = mapped_column(Integer)
    joursDisponibles: Mapped[str] = mapped_column(String(100))
    Saison: Mapped[Saison] = mapped_column(Enum(Saison))
    Prix: Mapped[float] = mapped_column(Float)
    centrecongres_id: Mapped[int] = mapped_column(ForeignKey("centrecongres.id"))
    type_spec: Mapped[str] = mapped_column(String(50))
    __mapper_args__ = {
        "polymorphic_identity": "elementcentre",
        "polymorphic_on": "type_spec",
    }

class Salle(ElementCentre):
    __tablename__ = "salle"
    id: Mapped[int] = mapped_column(ForeignKey("elementcentre.id"), primary_key=True)
    capaciteMax: Mapped[int] = mapped_column(Integer)
    superficie: Mapped[float] = mapped_column(Float)
    __mapper_args__ = {
        "polymorphic_identity": "salle",
    }

class Materiel(ElementCentre):
    __tablename__ = "materiel"
    id: Mapped[int] = mapped_column(ForeignKey("elementcentre.id"), primary_key=True)
    prixUnitaire: Mapped[float] = mapped_column(Float)
    quantiteDisponible: Mapped[int] = mapped_column(Integer)
    __mapper_args__ = {
        "polymorphic_identity": "materiel",
    }

class Prestation(ElementCentre):
    __tablename__ = "prestation"
    id: Mapped[int] = mapped_column(ForeignKey("elementcentre.id"), primary_key=True)
    prix: Mapped[float] = mapped_column(Float)
    nbMaxParticipants: Mapped[int] = mapped_column(Integer)
    nbMinParticipants: Mapped[int] = mapped_column(Integer)
    __mapper_args__ = {
        "polymorphic_identity": "prestation",
    }

class Gestionnaire(Base):
    __tablename__ = "gestionnaire"
    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100))

class CentreCongres(Base):
    __tablename__ = "centrecongres"
    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(100))
    adresse: Mapped[str] = mapped_column(String(100))


#--- Relationships of the evenement table
Evenement.reservation: Mapped[List["Reservation"]] = relationship("Reservation", back_populates="evenement", foreign_keys=[Reservation.evenement_id])

#--- Relationships of the periodeindisponibilite table
PeriodeIndisponibilite.elementcentre_2: Mapped["ElementCentre"] = relationship("ElementCentre", back_populates="periodeindisponibilite", foreign_keys=[PeriodeIndisponibilite.elementcentre_2_id])

#--- Relationships of the reservation table
Reservation.gestionnaire: Mapped["Gestionnaire"] = relationship("Gestionnaire", back_populates="reservation_2", foreign_keys=[Reservation.gestionnaire_id])
Reservation.evenement: Mapped["Evenement"] = relationship("Evenement", back_populates="reservation", foreign_keys=[Reservation.evenement_id])
Reservation.elementcentre_1: Mapped[List["ElementCentre"]] = relationship("ElementCentre", secondary=réserve, back_populates="reservation_1")

#--- Relationships of the elementcentre table
ElementCentre.centrecongres: Mapped["CentreCongres"] = relationship("CentreCongres", back_populates="elementcentre", foreign_keys=[ElementCentre.centrecongres_id])
ElementCentre.reservation_1: Mapped[List["Reservation"]] = relationship("Reservation", secondary=réserve, back_populates="elementcentre_1")
ElementCentre.periodeindisponibilite: Mapped[List["PeriodeIndisponibilite"]] = relationship("PeriodeIndisponibilite", back_populates="elementcentre_2", foreign_keys=[PeriodeIndisponibilite.elementcentre_2_id])

#--- Relationships of the gestionnaire table
Gestionnaire.reservation_2: Mapped[List["Reservation"]] = relationship("Reservation", back_populates="gestionnaire", foreign_keys=[Reservation.gestionnaire_id])

#--- Relationships of the centrecongres table
CentreCongres.elementcentre: Mapped[List["ElementCentre"]] = relationship("ElementCentre", back_populates="centrecongres", foreign_keys=[ElementCentre.centrecongres_id])

# Database connection
DATABASE_URL = "sqlite:///Class_Diagram.db"  # SQLite connection
engine = create_engine(DATABASE_URL, echo=True)

# Create tables in the database
Base.metadata.create_all(engine, checkfirst=True)