"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities

# Create a test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities before each test"""
    global activities
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for interscholastic play",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and compete in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["lucas@mergington.edu", "grace@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and mixed media techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in plays and develop acting skills",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["noah@mergington.edu", "mia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and critical thinking skills through debate",
            "schedule": "Mondays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 14,
            "participants": ["ryan@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["hannah@mergington.edu", "james@mergington.edu"]
        }
    })
    yield


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirect(self):
        """Test that root redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for getting activities"""
    
    def test_get_all_activities(self):
        """Test fetching all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) == 9
    
    def test_get_activities_includes_participants(self):
        """Test that activities include participant information"""
        response = client.get("/activities")
        data = response.json()
        assert "participants" in data["Chess Club"]
        assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]
    
    def test_get_activities_includes_metadata(self):
        """Test that activities include all required metadata"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


class TestSignup:
    """Tests for signing up for activities"""
    
    def test_signup_success(self):
        """Test successful signup"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_adds_participant(self):
        """Test that signup actually adds the participant"""
        client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        response = client.get("/activities")
        data = response.json()
        assert "newstudent@mergington.edu" in data["Chess Club"]["participants"]
    
    def test_signup_duplicate_email(self):
        """Test that duplicate signup is rejected"""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity(self):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_signup_multiple_activities(self):
        """Test that a student can sign up for multiple activities"""
        client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        response = client.post(
            "/activities/Programming Class/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        activities_data = client.get("/activities").json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
        assert "newstudent@mergington.edu" in activities_data["Programming Class"]["participants"]


class TestUnregister:
    """Tests for unregistering from activities"""
    
    def test_unregister_success(self):
        """Test successful unregistration"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert "michael@mergington.edu" in data["message"]
    
    def test_unregister_removes_participant(self):
        """Test that unregister actually removes the participant"""
        client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" not in data["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity(self):
        """Test unregister from non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_unregister_not_registered(self):
        """Test unregister for student not registered"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]
    
    def test_unregister_then_signup_again(self):
        """Test that student can sign up again after unregistering"""
        client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        activities_data = client.get("/activities").json()
        assert "michael@mergington.edu" in activities_data["Chess Club"]["participants"]


class TestIntegration:
    """Integration tests"""
    
    def test_full_signup_workflow(self):
        """Test full signup workflow"""
        # Get initial state
        response = client.get("/activities")
        initial_count = len(response.json()["Chess Club"]["participants"])
        
        # Sign up
        response = client.post(
            "/activities/Chess Club/signup?email=workflow@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        final_count = len(response.json()["Chess Club"]["participants"])
        assert final_count == initial_count + 1
        assert "workflow@mergington.edu" in response.json()["Chess Club"]["participants"]
    
    def test_full_unregister_workflow(self):
        """Test full unregister workflow"""
        # Sign up first
        client.post(
            "/activities/Chess Club/signup?email=workflow2@mergington.edu"
        )
        
        # Get participant count
        response = client.get("/activities")
        count_before = len(response.json()["Chess Club"]["participants"])
        
        # Unregister
        response = client.delete(
            "/activities/Chess Club/unregister?email=workflow2@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify unregister
        response = client.get("/activities")
        count_after = len(response.json()["Chess Club"]["participants"])
        assert count_after == count_before - 1
        assert "workflow2@mergington.edu" not in response.json()["Chess Club"]["participants"]
