"""
Tests for feature engineering pipeline.
"""
import pytest
from datetime import date, timedelta
from src.features.build_features import (
    compute_demand_features,
    compute_competition_features,
    compute_economics_features,
    compute_risk_features,
)


def test_demand_features_no_leakage():
    """Test that demand features don't use future data."""
    week_start = date(2026, 1, 12)
    entity_id = "test-entity"
    
    features = compute_demand_features(entity_id, week_start)
    
    # TODO: Add assertions
    assert isinstance(features, dict)


def test_features_as_of_date():
    """Test that all features are computed 'as of' week_start."""
    # TODO: Implement test
    # - Verify no features use data after week_start
    pass


if __name__ == "__main__":
    pytest.main([__file__])

