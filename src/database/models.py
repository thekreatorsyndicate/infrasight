from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, Boolean,
    ForeignKey, Index, UniqueConstraint, JSON, Date
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone

Base = declarative_base()


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(64), unique=True, nullable=False, index=True)
    pipeline_version = Column(String(32), nullable=False)
    scoring_version = Column(String(32), nullable=True)
    source_snapshot_id = Column(String(64), nullable=True)
    status = Column(String(32), default="running")
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    run_metadata = Column(JSON, nullable=True)

    projects = relationship("Project", back_populates="pipeline_run")
    expenditures = relationship("Expenditure", back_populates="pipeline_run")
    risk_scores = relationship("RiskScore", back_populates="pipeline_run")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(64), ForeignKey("pipeline_runs.run_id"), nullable=False, index=True)
    work_id = Column(String(64), nullable=False, index=True)
    state = Column(String(128), nullable=True)
    district = Column(String(128), nullable=True)
    constituency = Column(String(128), nullable=True)
    mp_name = Column(String(128), nullable=True)
    work_name = Column(String(512), nullable=True)
    work_category = Column(String(128), nullable=True)
    sub_category = Column(String(128), nullable=True)
    agency_name = Column(String(256), nullable=True)
    recommended_amount = Column(Float, nullable=True)
    sanction_amount = Column(Float, nullable=True)
    recommended_date = Column(Date, nullable=True)
    sanction_date = Column(Date, nullable=True)
    completion_date = Column(Date, nullable=True)
    work_status = Column(String(64), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    raw_data = Column(JSON, nullable=True)

    pipeline_run = relationship("PipelineRun", back_populates="projects")
    expenditures = relationship("Expenditure", back_populates="project")
    risk_score = relationship("RiskScore", back_populates="project", uselist=False)

    __table_args__ = (
        UniqueConstraint("run_id", "work_id", name="uq_run_work_id"),
        Index("ix_projects_district_category", "district", "work_category"),
    )


class Expenditure(Base):
    __tablename__ = "expenditures"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(64), ForeignKey("pipeline_runs.run_id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    work_id = Column(String(64), nullable=False, index=True)
    expenditure_amount = Column(Float, nullable=True)
    expenditure_date = Column(Date, nullable=True)
    expenditure_year = Column(Integer, nullable=True, index=True)
    raw_data = Column(JSON, nullable=True)

    pipeline_run = relationship("PipelineRun", back_populates="expenditures")
    project = relationship("Project", back_populates="expenditures")

    __table_args__ = (
        Index("ix_expenditures_work_year", "work_id", "expenditure_year"),
    )


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(64), ForeignKey("pipeline_runs.run_id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    work_id = Column(String(64), nullable=False, index=True)

    cost_anomaly_score = Column(Float, nullable=True)
    expenditure_anomaly_score = Column(Float, nullable=True)
    duration_anomaly_score = Column(Float, nullable=True)
    composite_score = Column(Float, nullable=True)

    confidence_score = Column(Float, nullable=True)
    data_coverage = Column(Float, nullable=True)
    peer_count = Column(Integer, nullable=True)
    scoring_version = Column(String(32), nullable=True)

    peer_group_level = Column(String(32), nullable=True)
    peer_group_definition = Column(JSON, nullable=True)

    integrity_flags = Column(JSON, nullable=True)
    evidence = Column(JSON, nullable=True)

    calculated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    pipeline_run = relationship("PipelineRun", back_populates="risk_scores")
    project = relationship("Project", back_populates="risk_score")

    __table_args__ = (
        UniqueConstraint("run_id", "work_id", name="uq_risk_run_work_id"),
    )