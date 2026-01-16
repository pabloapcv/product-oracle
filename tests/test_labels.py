"""
Tests for label computation.
"""
import pytest
from datetime import date
from src.transform.build_labels import compute_amazon_winner_labels


def test_label_horizon():
    """Test that labels use correct look-ahead horizon."""
    week_start = date(2026, 1, 12)
    
    # TODO: Implement test
    # - Compute labels for week_start
    # - Verify labels check outcomes in week_start + 8 weeks
    pass


def test_labels_no_feature_leakage():
    """Test that labels don't leak into feature computation."""
    # TODO: Implement test
    # - Labels should only be used for training, not features
    pass


if __name__ == "__main__":
    pytest.main([__file__])

