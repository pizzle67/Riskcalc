"""
SQLAlchemy models for the Open FAIR Calculator.
"""

from datetime import datetime
from webapp.database import db


class Scenario(db.Model):
    """Model for storing risk scenarios."""
    __tablename__ = 'scenarios'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    lef_config = db.Column(db.JSON, nullable=False)
    lm_config = db.Column(db.JSON, nullable=False)
    iterations = db.Column(db.Integer, default=10000)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to simulation results
    results = db.relationship('SimulationResult', backref='scenario', lazy=True,
                              cascade='all, delete-orphan')

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'lef_config': self.lef_config,
            'lm_config': self.lm_config,
            'iterations': self.iterations,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data):
        """Create model from dictionary."""
        return cls(
            name=data.get('name', 'Unnamed Scenario'),
            description=data.get('description'),
            lef_config=data.get('lef_config', {}),
            lm_config=data.get('lm_config', {}),
            iterations=data.get('iterations', 10000),
        )


class SimulationResult(db.Model):
    """Model for storing simulation results."""
    __tablename__ = 'simulation_results'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey('scenarios.id'), nullable=False)
    executed_at = db.Column(db.DateTime, default=datetime.utcnow)
    iterations = db.Column(db.Integer, nullable=False)
    seed = db.Column(db.Integer, nullable=True)
    summary_stats = db.Column(db.JSON, nullable=False)
    histogram_data = db.Column(db.JSON, nullable=True)
    exceedance_data = db.Column(db.JSON, nullable=True)

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'scenario_id': self.scenario_id,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'iterations': self.iterations,
            'seed': self.seed,
            'summary_stats': self.summary_stats,
            'histogram_data': self.histogram_data,
            'exceedance_data': self.exceedance_data,
        }

    @classmethod
    def from_dict(cls, data):
        """Create model from dictionary."""
        return cls(
            scenario_id=data.get('scenario_id'),
            iterations=data.get('iterations', 10000),
            seed=data.get('seed'),
            summary_stats=data.get('summary_stats', {}),
            histogram_data=data.get('histogram_data'),
            exceedance_data=data.get('exceedance_data'),
        )
