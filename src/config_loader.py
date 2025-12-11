def load_rules(framework):
    # Define per-framework thresholds
    base = {"response_time_threshold": 3.0, "error_threshold": 10, "bounce_threshold": 0.55}
    if framework == "django": base["optimize_db_queries"] = True
    if framework == "react": base["prefer_function_components"] = True
    return base
