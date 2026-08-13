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
    AREAS,
    SUCCESS_HEADLINE,
    ContextualNote,
    KnowledgeCheck,
    Lesson,
    MetricTarget,
    ReadinessDimension,
    SuccessCriterion,
    WalkthroughStep,
    get_contextual_notes,
    get_knowledge_checks,
    get_lesson,
    get_lessons,
    get_metric_targets,
    get_readiness_dimensions,
    get_success_criteria,
    get_walkthrough,
    grade_answer,
)

__all__ = [
    "AREAS",
    "ContextualNote",
    "KnowledgeCheck",
    "Lesson",
    "MetricTarget",
    "ReadinessDimension",
    "SUCCESS_HEADLINE",
    "SuccessCriterion",
    "WalkthroughStep",
    "get_contextual_notes",
    "get_knowledge_checks",
    "get_lesson",
    "get_lessons",
    "get_metric_targets",
    "get_readiness_dimensions",
    "get_success_criteria",
    "get_walkthrough",
    "grade_answer",
]
