"""
Unit tests for alert generation system.

Tests cover:
- Single alert conditions
- Multiple simultaneous alerts
- Boundary values
- No alerts scenario

Requirements: 3.1, 3.2, 3.3
"""

import pytest
from alerts import generate_alerts
from models_schema import Alert


class TestSingleAlertConditions:
    """Tests for individual alert conditions."""
    
    def test_low_moisture_alert(self):
        """Test low soil moisture alert generation (forecast < 30%)."""
        forecast = 25.0
        rain = 5.0
        
        alerts = generate_alerts(forecast, rain)
        
        assert len(alerts) == 1
        assert alerts[0].message == "Low soil moisture — irrigation needed soon."
        assert alerts[0].severity == "WARNING"
        assert alerts[0].notify is True
    
    def test_flooding_risk_alert(self):
        """Test flooding risk alert generation (forecast > 70%)."""
        forecast = 75.0
        rain = 5.0
        
        alerts = generate_alerts(forecast, rain)
        
        assert len(alerts) == 1
        assert alerts[0].message == "Risk of flooding — irrigation paused."
        assert alerts[0].severity == "WARNING"
        assert alerts[0].notify is True
    
    def test_heavy_rainfall_alert(self):
        """Test heavy rainfall alert generation (rain > 20mm)."""
        forecast = 50.0
        rain = 25.0
        
        alerts = generate_alerts(forecast, rain)
        
        assert len(alerts) == 1
        assert alerts[0].message == "Heavy rainfall expected — flooding alert."
        assert alerts[0].severity == "CRITICAL"
        assert alerts[0].notify is True


class TestMultipleSimultaneousAlerts:
    """Tests for multiple alerts triggered at once."""
    
    def test_low_moisture_and_heavy_rain(self):
        """Test low moisture and heavy rainfall alerts together."""
        forecast = 25.0
        rain = 30.0
        
        alerts = generate_alerts(forecast, rain)
        
        assert len(alerts) == 2
        
        # Check both alerts are present
        messages = [alert.message for alert in alerts]
        assert "Low soil moisture — irrigation needed soon." in messages
        assert "Heavy rainfall expected — flooding alert." in messages
    
    def test_flooding_risk_and_heavy_rain(self):
        """Test flooding risk and heavy rainfall alerts together."""
        forecast = 80.0
        rain = 35.0
        
        alerts = generate_alerts(forecast, rain)
        
        assert len(alerts) == 2
        
        # Check both alerts are present
        messages = [alert.message for alert in alerts]
        assert "Risk of flooding — irrigation paused." in messages
        assert "Heavy rainfall expected — flooding alert." in messages
    
    def test_all_three_alerts(self):
        """
        Test scenario where all three alerts could theoretically trigger.
        
        Note: In practice, low moisture (< 30%) and flooding risk (> 70%)
        cannot occur simultaneously, but we test the logic independently.
        """
        # This is a theoretical test - in reality, forecast can't be both < 30 and > 70
        # But we can test each condition separately
        
        # Test low moisture + heavy rain
        alerts_low = generate_alerts(25.0, 25.0)
        assert len(alerts_low) == 2
        
        # Test high moisture + heavy rain
        alerts_high = generate_alerts(75.0, 25.0)
        assert len(alerts_high) == 2


class TestBoundaryValues:
    """Tests for boundary conditions."""
    
    def test_exactly_30_percent_no_alert(self):
        """Test that exactly 30% moisture does not trigger low moisture alert."""
        forecast = 30.0
        rain = 5.0
        
        alerts = generate_alerts(forecast, rain)
        
        # Should not trigger low moisture alert (< 30, not <=)
        assert len(alerts) == 0
    
    def test_exactly_70_percent_no_alert(self):
        """Test that exactly 70% moisture does not trigger flooding alert."""
        forecast = 70.0
        rain = 5.0
        
        alerts = generate_alerts(forecast, rain)
        
        # Should not trigger flooding alert (> 70, not >=)
        assert len(alerts) == 0
    
    def test_exactly_20mm_rain_no_alert(self):
        """Test that exactly 20mm rain does not trigger heavy rainfall alert."""
        forecast = 50.0
        rain = 20.0
        
        alerts = generate_alerts(forecast, rain)
        
        # Should not trigger heavy rainfall alert (> 20, not >=)
        assert len(alerts) == 0
    
    def test_just_below_30_percent(self):
        """Test that 29.9% triggers low moisture alert."""
        forecast = 29.9
        rain = 5.0
        
        alerts = generate_alerts(forecast, rain)
        
        assert len(alerts) == 1
        assert "Low soil moisture" in alerts[0].message
    
    def test_just_above_70_percent(self):
        """Test that 70.1% triggers flooding risk alert."""
        forecast = 70.1
        rain = 5.0
        
        alerts = generate_alerts(forecast, rain)
        
        assert len(alerts) == 1
        assert "Risk of flooding" in alerts[0].message
    
    def test_just_above_20mm_rain(self):
        """Test that 20.1mm triggers heavy rainfall alert."""
        forecast = 50.0
        rain = 20.1
        
        alerts = generate_alerts(forecast, rain)
        
        assert len(alerts) == 1
        assert "Heavy rainfall expected" in alerts[0].message


class TestNoAlertsScenario:
    """Tests for scenarios where no alerts should be generated."""
    
    def test_optimal_conditions(self):
        """Test that optimal conditions generate no alerts."""
        forecast = 50.0  # Optimal moisture
        rain = 5.0  # Light rain
        
        alerts = generate_alerts(forecast, rain)
        
        assert len(alerts) == 0
    
    def test_near_optimal_low(self):
        """Test conditions just above low moisture threshold."""
        forecast = 35.0
        rain = 10.0
        
        alerts = generate_alerts(forecast, rain)
        
        assert len(alerts) == 0
    
    def test_near_optimal_high(self):
        """Test conditions just below flooding threshold."""
        forecast = 65.0
        rain = 15.0
        
        alerts = generate_alerts(forecast, rain)
        
        assert len(alerts) == 0
    
    def test_zero_values(self):
        """Test with zero forecast and rain."""
        forecast = 0.0
        rain = 0.0
        
        alerts = generate_alerts(forecast, rain)
        
        # Zero forecast should trigger low moisture alert
        assert len(alerts) == 1
        assert "Low soil moisture" in alerts[0].message
    
    def test_maximum_safe_values(self):
        """Test with maximum values that don't trigger alerts."""
        forecast = 70.0  # Exactly at threshold
        rain = 20.0  # Exactly at threshold
        
        alerts = generate_alerts(forecast, rain)
        
        assert len(alerts) == 0


class TestAlertProperties:
    """Tests for alert object properties."""
    
    def test_alert_has_timestamp(self):
        """Test that alerts include a timestamp."""
        forecast = 25.0
        rain = 5.0
        
        alerts = generate_alerts(forecast, rain)
        
        assert len(alerts) == 1
        assert alerts[0].timestamp is not None
        assert isinstance(alerts[0].timestamp, type(alerts[0].timestamp))
    
    def test_alert_notify_flag(self):
        """Test that all alerts have notify flag set to True."""
        # Test low moisture
        alerts_low = generate_alerts(25.0, 5.0)
        assert all(alert.notify is True for alert in alerts_low)
        
        # Test flooding
        alerts_flood = generate_alerts(75.0, 5.0)
        assert all(alert.notify is True for alert in alerts_flood)
        
        # Test heavy rain
        alerts_rain = generate_alerts(50.0, 25.0)
        assert all(alert.notify is True for alert in alerts_rain)
    
    def test_alert_severity_levels(self):
        """Test that alerts have correct severity levels."""
        # Low moisture and flooding are WARNING
        alerts_warning = generate_alerts(25.0, 5.0)
        assert alerts_warning[0].severity == "WARNING"
        
        alerts_flood = generate_alerts(75.0, 5.0)
        assert alerts_flood[0].severity == "WARNING"
        
        # Heavy rainfall is CRITICAL
        alerts_critical = generate_alerts(50.0, 25.0)
        assert alerts_critical[0].severity == "CRITICAL"


class TestExtremeConditions:
    """Tests for extreme weather conditions."""
    
    def test_extreme_low_moisture(self):
        """Test with extremely low moisture."""
        forecast = 0.0
        rain = 0.0
        
        alerts = generate_alerts(forecast, rain)
        
        assert len(alerts) == 1
        assert "Low soil moisture" in alerts[0].message
    
    def test_extreme_high_moisture(self):
        """Test with extremely high moisture."""
        forecast = 100.0
        rain = 0.0
        
        alerts = generate_alerts(forecast, rain)
        
        assert len(alerts) == 1
        assert "Risk of flooding" in alerts[0].message
    
    def test_extreme_rainfall(self):
        """Test with extreme rainfall."""
        forecast = 50.0
        rain = 200.0
        
        alerts = generate_alerts(forecast, rain)
        
        assert len(alerts) == 1
        assert "Heavy rainfall expected" in alerts[0].message
    
    def test_extreme_all_conditions(self):
        """Test with extreme high moisture and extreme rainfall."""
        forecast = 95.0
        rain = 150.0
        
        alerts = generate_alerts(forecast, rain)
        
        assert len(alerts) == 2
        messages = [alert.message for alert in alerts]
        assert any("flooding" in msg.lower() for msg in messages)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
