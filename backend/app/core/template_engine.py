"""Template engine for communication messages with variable substitution.

Uses string.Template from stdlib with a restricted set of allowed variables.
"""

import re
import string


class TemplateVariableError(ValueError):
    """Raised when a template uses a variable that is not in the allowed set."""

    def __init__(self, variable: str):
        self.variable = variable
        super().__init__(f"Variable '{variable}' is not allowed")


class TemplateEngine:
    """Safe template engine with restricted variable substitution.

    Usage:
        engine = TemplateEngine(allowed_variables={"alumno_nombre"})
        result = engine.render(
            template="Hola $alumno_nombre",
            values={"alumno_nombre": "Juan"},
        )
    """

    def __init__(self, allowed_variables: set[str]):
        self._allowed_variables = allowed_variables
        self._var_pattern = re.compile(r"\$([a-zA-Z_][a-zA-Z0-9_]*)")

    def render(self, template: str, values: dict[str, str]) -> str:
        """Render a template by substituting variables.

        Args:
            template: String with $variable placeholders.
            values: Dict mapping variable names to their values.

        Returns:
            Rendered string with variables substituted.

        Raises:
            TemplateVariableError: If the template uses an undeclared variable.
        """
        # Find all variables used in the template
        used_vars = set(self._var_pattern.findall(template))
        if not used_vars:
            return template

        # Validate all used variables are allowed
        for var in used_vars:
            if var not in self._allowed_variables:
                raise TemplateVariableError(f"${var}")

        # Build safe substitute dict (only pass allowed vars that are used)
        safe_values = {k: v for k, v in values.items() if k in self._allowed_variables}

        # Use string.Template for substitution
        tmpl = string.Template(template)
        return tmpl.safe_substitute(**safe_values)
