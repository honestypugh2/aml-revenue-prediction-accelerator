"""Original educational content for the interactive learning experience.

This module provides repository-grounded lessons and knowledge checks. All
content is original and specific to healthcare net-revenue prediction with Azure
Machine Learning, Automated ML, code-first ML, Microsoft Fabric/OneLake, secure
infrastructure, MLOps, and model governance. It draws only *conceptual*
inspiration from the idea of contextual, in-repository learning; no third-party
source code, prose, visual design, branding, or UI was copied.
"""

from __future__ import annotations

from .content import (
    KnowledgeCheck,
    Lesson,
    get_knowledge_checks,
    get_lessons,
    grade_answer,
)

__all__ = [
    "KnowledgeCheck",
    "Lesson",
    "get_knowledge_checks",
    "get_lessons",
    "grade_answer",
]
