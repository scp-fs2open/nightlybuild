"""Tests for env_parser module."""

import pytest

from env_parser import EnvVariable, parse_env_default, parse_env, write_env, merge_variables


# ---------------------------------------------------------------------------
# EnvVariable
# ---------------------------------------------------------------------------

class TestEnvVariable:
    def test_effective_value_returns_default_when_not_overridden(self):
        var = EnvVariable("KEY", "default", None, "", "", True)
        assert var.effective_value == "default"

    def test_effective_value_returns_override_when_overridden(self):
        var = EnvVariable("KEY", "default", None, "", "", True)
        var.override_value = "custom"
        var.is_overridden = True
        assert var.effective_value == "custom"

    def test_effective_value_returns_none_for_commented_var(self):
        var = EnvVariable("KEY", None, "example", "", "", False)
        assert var.effective_value is None

    def test_effective_value_override_can_be_empty_string(self):
        var = EnvVariable("KEY", "default", None, "", "", True)
        var.override_value = ""
        var.is_overridden = True
        assert var.effective_value == ""

    def test_initial_override_state(self):
        var = EnvVariable("KEY", "val", None, "desc", "section", True)
        assert var.override_value is None
        assert var.is_overridden is False


# ---------------------------------------------------------------------------
# parse_env_default
# ---------------------------------------------------------------------------

class TestParseEnvDefault:
    def test_active_variable(self, tmp_path):
        f = tmp_path / ".env.default"
        f.write_text("APP_NAME=myapp\n")
        result = parse_env_default(str(f))
        assert len(result) == 1
        v = result[0]
        assert v.name == "APP_NAME"
        assert v.default_value == "myapp"
        assert v.is_active_default is True
        assert v.example_value is None

    def test_commented_variable(self, tmp_path):
        f = tmp_path / ".env.default"
        f.write_text("#SECRET_KEY=changeme\n")
        result = parse_env_default(str(f))
        assert len(result) == 1
        v = result[0]
        assert v.name == "SECRET_KEY"
        assert v.default_value is None
        assert v.example_value == "changeme"
        assert v.is_active_default is False

    def test_commented_variable_empty_value(self, tmp_path):
        f = tmp_path / ".env.default"
        f.write_text("#EMPTY_VAR=\n")
        result = parse_env_default(str(f))
        assert len(result) == 1
        assert result[0].example_value is None  # empty string becomes None

    def test_commented_variable_strips_quotes(self, tmp_path):
        f = tmp_path / ".env.default"
        f.write_text('#QUOTED="hello"\n#SINGLE=\'world\'\n')
        result = parse_env_default(str(f))
        assert result[0].example_value == "hello"
        assert result[1].example_value == "world"

    def test_section_headers(self, tmp_path):
        f = tmp_path / ".env.default"
        f.write_text(
            "# General Settings\n"
            "APP_NAME=myapp\n"
            "\n"
            "# Database Settings\n"
            "DB_HOST=localhost\n"
        )
        result = parse_env_default(str(f))
        assert result[0].section == "General Settings"
        assert result[1].section == "Database Settings"

    def test_description_from_comments(self, tmp_path):
        f = tmp_path / ".env.default"
        f.write_text(
            "# Section\n"
            "# The application name\n"
            "# used for display\n"
            "APP_NAME=myapp\n"
        )
        result = parse_env_default(str(f))
        assert result[0].description == "The application name used for display"

    def test_blank_line_resets_pending_comments(self, tmp_path):
        f = tmp_path / ".env.default"
        f.write_text(
            "# Section\n"
            "# orphan comment\n"
            "\n"
            "# New Section\n"
            "KEY=val\n"
        )
        result = parse_env_default(str(f))
        assert result[0].description == ""
        assert result[0].section == "New Section"

    def test_empty_file(self, tmp_path):
        f = tmp_path / ".env.default"
        f.write_text("")
        result = parse_env_default(str(f))
        assert result == []

    def test_multiple_variables_mixed(self, tmp_path):
        f = tmp_path / ".env.default"
        f.write_text(
            "# App Config\n"
            "# Name of the app\n"
            "APP_NAME=demo\n"
            "# Port number\n"
            "#PORT=8080\n"
            "\n"
            "# Database\n"
            "DB_HOST=localhost\n"
        )
        result = parse_env_default(str(f))
        assert len(result) == 3

        assert result[0].name == "APP_NAME"
        assert result[0].default_value == "demo"
        assert result[0].description == "Name of the app"
        assert result[0].section == "App Config"

        assert result[1].name == "PORT"
        assert result[1].default_value is None
        assert result[1].example_value == "8080"
        assert result[1].description == "Port number"
        assert result[1].section == "App Config"

        assert result[2].name == "DB_HOST"
        assert result[2].section == "Database"

    def test_active_var_with_equals_in_value(self, tmp_path):
        f = tmp_path / ".env.default"
        f.write_text("CONNECTION=host=localhost;port=5432\n")
        result = parse_env_default(str(f))
        assert result[0].default_value == "host=localhost;port=5432"

    def test_start_of_file_treated_as_after_blank(self, tmp_path):
        """First comment at start of file becomes a section header."""
        f = tmp_path / ".env.default"
        f.write_text("# First Section\nKEY=val\n")
        result = parse_env_default(str(f))
        assert result[0].section == "First Section"
        assert result[0].description == ""

    def test_empty_default_value(self, tmp_path):
        f = tmp_path / ".env.default"
        f.write_text("EMPTY_KEY=\n")
        result = parse_env_default(str(f))
        assert result[0].default_value == ""

    def test_only_comments_no_variables(self, tmp_path):
        f = tmp_path / ".env.default"
        f.write_text("# Just a comment\n# Another comment\n")
        result = parse_env_default(str(f))
        assert result == []


# ---------------------------------------------------------------------------
# parse_env
# ---------------------------------------------------------------------------

class TestParseEnv:
    def test_basic_parsing(self, tmp_path):
        f = tmp_path / ".env"
        f.write_text("HOST=localhost\nPORT=5000\n")
        result = parse_env(str(f))
        assert result == {"HOST": "localhost", "PORT": "5000"}

    def test_double_quoted_value(self, tmp_path):
        f = tmp_path / ".env"
        f.write_text('GREETING="hello world"\n')
        result = parse_env(str(f))
        assert result["GREETING"] == "hello world"

    def test_single_quoted_value(self, tmp_path):
        f = tmp_path / ".env"
        f.write_text("SECRET='s3cr3t'\n")
        result = parse_env(str(f))
        assert result["SECRET"] == "s3cr3t"

    def test_unquoted_value_with_spaces_preserved(self, tmp_path):
        f = tmp_path / ".env"
        f.write_text("MSG=hello world\n")
        result = parse_env(str(f))
        assert result["MSG"] == "hello world"

    def test_comments_skipped(self, tmp_path):
        f = tmp_path / ".env"
        f.write_text("# This is a comment\nKEY=val\n")
        result = parse_env(str(f))
        assert result == {"KEY": "val"}

    def test_blank_lines_skipped(self, tmp_path):
        f = tmp_path / ".env"
        f.write_text("A=1\n\n\nB=2\n")
        result = parse_env(str(f))
        assert result == {"A": "1", "B": "2"}

    def test_missing_file_returns_empty(self, tmp_path):
        result = parse_env(str(tmp_path / "nonexistent.env"))
        assert result == {}

    def test_value_with_equals_sign(self, tmp_path):
        f = tmp_path / ".env"
        f.write_text("CONN=host=db;port=5432\n")
        result = parse_env(str(f))
        assert result["CONN"] == "host=db;port=5432"

    def test_empty_value(self, tmp_path):
        f = tmp_path / ".env"
        f.write_text("EMPTY=\n")
        result = parse_env(str(f))
        assert result["EMPTY"] == ""

    def test_mismatched_quotes_not_stripped(self, tmp_path):
        f = tmp_path / ".env"
        f.write_text("BAD=\"hello'\n")
        result = parse_env(str(f))
        assert result["BAD"] == "\"hello'"

    def test_empty_file(self, tmp_path):
        f = tmp_path / ".env"
        f.write_text("")
        result = parse_env(str(f))
        assert result == {}

    def test_key_whitespace_stripped(self, tmp_path):
        f = tmp_path / ".env"
        f.write_text("  KEY  =value\n")
        result = parse_env(str(f))
        assert result["KEY"] == "value"


# ---------------------------------------------------------------------------
# write_env
# ---------------------------------------------------------------------------

class TestWriteEnv:
    def test_basic_output(self, tmp_path):
        f = tmp_path / ".env"
        write_env(str(f), {"APP": "myapp", "PORT": "8080"})
        content = f.read_text()
        assert "APP='myapp'\n" in content
        assert "PORT='8080'\n" in content

    def test_single_quote_escaping(self, tmp_path):
        f = tmp_path / ".env"
        write_env(str(f), {"MSG": "it's alive"})
        content = f.read_text()
        assert content == "MSG='it'\\''s alive'\n"

    def test_newline_stripping(self, tmp_path):
        f = tmp_path / ".env"
        write_env(str(f), {"VAL": "line1\nline2\r\nline3"})
        content = f.read_text()
        assert "\n" not in content.split("=", 1)[1].rstrip("\n")
        assert "line1line2line3" in content

    def test_none_values_skipped(self, tmp_path):
        f = tmp_path / ".env"
        write_env(str(f), {"KEEP": "yes", "SKIP": None})
        content = f.read_text()
        assert "KEEP='yes'" in content
        assert "SKIP" not in content

    def test_empty_overrides(self, tmp_path):
        f = tmp_path / ".env"
        write_env(str(f), {})
        assert f.read_text() == ""

    def test_empty_string_value_written(self, tmp_path):
        f = tmp_path / ".env"
        write_env(str(f), {"EMPTY": ""})
        assert f.read_text() == "EMPTY=''\n"

    def test_multiple_single_quotes(self, tmp_path):
        f = tmp_path / ".env"
        write_env(str(f), {"Q": "a'b'c"})
        content = f.read_text()
        assert content == "Q='a'\\''b'\\''c'\n"

    def test_overwrites_existing_file(self, tmp_path):
        f = tmp_path / ".env"
        f.write_text("OLD='data'\n")
        write_env(str(f), {"NEW": "data"})
        content = f.read_text()
        assert "OLD" not in content
        assert "NEW='data'" in content


# ---------------------------------------------------------------------------
# merge_variables
# ---------------------------------------------------------------------------

class TestMergeVariables:
    def _make_var(self, name, default, section=""):
        return EnvVariable(name, default, None, "", section, default is not None)

    def test_basic_merge(self):
        variables = [self._make_var("A", "1"), self._make_var("B", "2")]
        overrides = {"A": "overridden"}
        merge_variables(variables, overrides)
        assert variables[0].is_overridden is True
        assert variables[0].override_value == "overridden"
        assert variables[1].is_overridden is False

    def test_unmatched_override_keys_ignored(self):
        variables = [self._make_var("A", "1")]
        overrides = {"A": "new", "UNKNOWN": "ignored"}
        merge_variables(variables, overrides)
        assert variables[0].override_value == "new"
        # UNKNOWN simply not applied to anything

    def test_section_grouping(self):
        variables = [
            self._make_var("A", "1", section="General"),
            self._make_var("B", "2", section="General"),
            self._make_var("C", "3", section="Database"),
        ]
        sections = merge_variables(variables, {})
        assert len(sections) == 2
        assert sections[0][0] == "General"
        assert len(sections[0][1]) == 2
        assert sections[1][0] == "Database"
        assert len(sections[1][1]) == 1

    def test_section_order_preserved(self):
        variables = [
            self._make_var("X", "1", section="Beta"),
            self._make_var("Y", "2", section="Alpha"),
            self._make_var("Z", "3", section="Beta"),
        ]
        sections = merge_variables(variables, {})
        assert sections[0][0] == "Beta"
        assert sections[1][0] == "Alpha"
        # Z should be grouped under first Beta section
        assert len(sections[0][1]) == 2

    def test_empty_variables(self):
        sections = merge_variables([], {})
        assert sections == []

    def test_merge_sets_effective_value(self):
        variables = [self._make_var("K", "default")]
        merge_variables(variables, {"K": "override"})
        assert variables[0].effective_value == "override"

    def test_merge_without_override_keeps_default(self):
        variables = [self._make_var("K", "default")]
        merge_variables(variables, {})
        assert variables[0].effective_value == "default"
