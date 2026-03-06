import os
import re


class EnvVariable:
    """A variable parsed from .env.default."""

    def __init__(self, name, default_value, example_value, description,
                 section, is_active_default):
        self.name = name
        self.default_value = default_value      # str or None (None = commented-out)
        self.example_value = example_value      # str or None (from #KEY=val lines)
        self.description = description          # comment text preceding the variable
        self.section = section                  # first comment after a blank line
        self.is_active_default = is_active_default

        # Set during merge with overrides
        self.override_value = None
        self.is_overridden = False

    @property
    def effective_value(self):
        if self.is_overridden:
            return self.override_value
        return self.default_value


# Regex patterns
_COMMENT_RE = re.compile(r'^#\s+(.+)$')
_COMMENTED_VAR_RE = re.compile(r'^#([A-Z_][A-Z0-9_]*)=(.*)$')
_ACTIVE_VAR_RE = re.compile(r'^([A-Z_][A-Z0-9_]*)=(.*)$')


def parse_env_default(path):
    """Parse .env.default into a list of EnvVariable objects.

    Handles three line types:
    - Active defaults:     KEY=value
    - Commented examples:  #KEY=value
    - Comments:            # descriptive text (becomes section headers or descriptions)
    """
    variables = []
    current_section = ""
    pending_comments = []
    after_blank = True  # treat start of file like after a blank

    with open(path) as f:
        for line in f:
            line = line.rstrip('\n')

            # Blank line: reset state, next comment starts a new section
            if not line.strip():
                after_blank = True
                pending_comments = []
                continue

            # Check for commented-out variable first (#KEY=val, no space after #)
            m = _COMMENTED_VAR_RE.match(line)
            if m:
                after_blank = False
                raw_val = m.group(2).strip('"').strip("'")
                variables.append(EnvVariable(
                    name=m.group(1),
                    default_value=None,
                    example_value=raw_val if raw_val else None,
                    description=' '.join(pending_comments),
                    section=current_section,
                    is_active_default=False,
                ))
                pending_comments = []
                continue

            # Comment line (# text, with space after #)
            m = _COMMENT_RE.match(line)
            if m:
                if after_blank:
                    current_section = m.group(1)
                    after_blank = False
                else:
                    pending_comments.append(m.group(1))
                continue

            # Active variable (KEY=value)
            m = _ACTIVE_VAR_RE.match(line)
            if m:
                after_blank = False
                variables.append(EnvVariable(
                    name=m.group(1),
                    default_value=m.group(2),
                    example_value=None,
                    description=' '.join(pending_comments),
                    section=current_section,
                    is_active_default=True,
                ))
                pending_comments = []
                continue

    return variables


def parse_env(path):
    """Parse a .env file into a dict of {KEY: VALUE} overrides."""
    overrides = {}
    if not os.path.exists(path):
        return overrides
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, _, value = line.partition('=')
                # Strip surrounding quotes if present
                value = value.strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                    value = value[1:-1]
                overrides[key.strip()] = value
    return overrides


def write_env(path, overrides):
    """Write user overrides to .env. Only non-empty overrides are written.

    Values are single-quoted to prevent shell expansion when sourced, with
    embedded single quotes escaped. Newlines are stripped to prevent file
    injection.
    """
    with open(path, 'w') as f:
        for key, value in overrides.items():
            if value is not None:
                value = value.replace('\r', '').replace('\n', '')
                value = value.replace("'", "'\\''")
                f.write(f"{key}='{value}'\n")


def merge_variables(variables, overrides):
    """Merge parsed .env.default variables with .env overrides.

    Sets override_value and is_overridden on each variable in-place.
    Returns a list of (section_name, [variables]) tuples for grouping.
    """
    for var in variables:
        if var.name in overrides:
            var.override_value = overrides[var.name]
            var.is_overridden = True

    sections = []
    seen = {}
    for var in variables:
        if var.section not in seen:
            seen[var.section] = []
            sections.append((var.section, seen[var.section]))
        seen[var.section].append(var)

    return sections
