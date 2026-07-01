"""
Smart-WorkLife Database Models.

All models are imported here for easy access and to ensure
SQLAlchemy metadata is properly populated for migrations.
"""
from app.models.user import User, UserPreference
from app.models.pomodoro import PomodoroSetting, PomodoroSession
from app.models.stretching import StretchingExercise, StretchingSession, StretchingRep
from app.models.health import BMIProfile, HydrationSetting, HydrationLog
from app.models.todo import Todo
from app.models.notulen import Notulen
from app.models.chat import Friendship, ChatMessage
from app.models.rating import AppRating

__all__ = [
    "User",
    "UserPreference",
    "PomodoroSetting",
    "PomodoroSession",
    "StretchingExercise",
    "StretchingSession",
    "StretchingRep",
    "BMIProfile",
    "HydrationSetting",
    "HydrationLog",
    "Todo",
    "Notulen",
    "Friendship",
    "ChatMessage",
    "AppRating",
]
