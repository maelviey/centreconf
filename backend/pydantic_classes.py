from datetime import datetime, date, time
from typing import Any, List, Optional, Union, Set
from enum import Enum
from pydantic import BaseModel, field_validator

from abc import ABC, abstractmethod

############################################
# Enumerations are defined here
############################################

class StatutReservation(Enum):
    ANNULEE = "ANNULEE"
    TERMINEE = "TERMINEE"
    CONFIRMEE = "CONFIRMEE"
    EN_ATTENTE = "EN_ATTENTE"

class TypeElement(Enum):
    SALLE_CONF = "SALLE_CONF"
    AUTRE = "AUTRE"
    RESTAURATION = "RESTAURATION"
    AMPHI = "AMPHI"

class Saison(Enum):
    HAUTE = "HAUTE"
    BASSE = "BASSE"
    MOYENNE = "MOYENNE"

############################################
# Classes are defined here
############################################
class EvenementCreate(BaseModel):
    description: str
    dateDebut: date
    dateFin: date
    nom: str
    emailReferent: str
    nbParticipantsPrevus: int
    reservation: Optional[List[int]] = None  # 1:N Relationship

    @field_validator('nbParticipantsPrevus')
    @classmethod
    def validate_nbParticipantsPrevus_1(cls, v):
        """OCL Constraint: constraint_Evenement_1_1"""
        if not (v > 0):
            raise ValueError('nbParticipantsPrevus must be > 0')
        return v

class PeriodeIndisponibiliteCreate(BaseModel):
    motif: str
    dateDebut: date
    dateFin: date
    elementcentre_2: int  # N:1 Relationship (mandatory)


class ReservationCreate(BaseModel):
    statut: StatutReservation
    heureMaxPaye: datetime
    montantTotal: float
    dateFin: date
    dateDebut: date
    elementcentre_1: List[int]  # N:M Relationship
    evenement: int  # N:1 Relationship (mandatory)
    gestionnaire: int  # N:1 Relationship (mandatory)


class ElementCentreCreate(ABC, BaseModel):
    Prix: float
    type: TypeElement
    dureeMinLocation: int
    Saison: Saison
    description: str
    joursDisponibles: str
    nom: str
    reservation_1: List[int]  # N:M Relationship
    periodeindisponibilite: Optional[List[int]] = None  # 1:N Relationship
    centrecongres: int  # N:1 Relationship (mandatory)


class SalleCreate(ElementCentreCreate):
    capaciteMax: int
    superficie: float

    @field_validator('capaciteMax')
    @classmethod
    def validate_capaciteMax_1(cls, v):
        """OCL Constraint: constraint_Salle_0_1"""
        if not (v > 0):
            raise ValueError('capaciteMax must be > 0')
        return v

class MaterielCreate(ElementCentreCreate):
    quantiteDisponible: int
    prixUnitaire: float


class PrestationCreate(ElementCentreCreate):
    prix: float
    nbMinParticipants: int
    nbMaxParticipants: int

    @field_validator('prix')
    @classmethod
    def validate_prix_1(cls, v):
        """OCL Constraint: constraint_Prestation_2_1"""
        if not (v >= 0.0):
            raise ValueError('prix must be >= 0.0')
        return v

class GestionnaireCreate(BaseModel):
    nom: str
    email: str
    reservation_2: Optional[List[int]] = None  # 1:N Relationship


class CentreCongresCreate(BaseModel):
    adresse: str
    nom: str
    elementcentre: Optional[List[int]] = None  # 1:N Relationship


