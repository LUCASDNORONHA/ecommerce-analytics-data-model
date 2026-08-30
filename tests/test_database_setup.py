from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from database import setup


class DatabaseSetupTests(unittest.TestCase):
    def test_get_database_name(self):
        url = "postgresql://user:pass@localhost:5432/ecommerce_analytics"

        result = setup.get_database_name(url)

        self.assertEqual(result, "ecommerce_analytics")

    def test_build_admin_url_uses_postgres_database(self):
        url = "postgresql://user:pass@localhost:5432/ecommerce_analytics"

        result = setup.build_admin_url(url)

        self.assertEqual(
            result,
            "postgresql://user:pass@localhost:5432/postgres",
        )

    @patch("database.setup.database_exists", return_value=True)
    @patch("database.setup.create_database")
    def test_ensure_database_does_not_create_when_database_exists(
        self,
        create_database_mock,
        database_exists_mock,
    ):
        database_url = "postgresql://localhost/ecommerce_analytics"

        result = setup.ensure_database(database_url)

        self.assertFalse(result)
        database_exists_mock.assert_called_once_with(database_url)
        create_database_mock.assert_not_called()

    @patch("database.setup.database_exists", return_value=False)
    @patch("database.setup.create_database")
    def test_ensure_database_creates_when_database_does_not_exist(
        self,
        create_database_mock,
        database_exists_mock,
    ):
        database_url = "postgresql://localhost/ecommerce_analytics"

        result = setup.ensure_database(database_url)

        self.assertTrue(result)
        database_exists_mock.assert_called_once_with(database_url)
        create_database_mock.assert_called_once_with(database_url)

    @patch("database.setup.ensure_database", return_value=False)
    @patch("database.setup.execute_sql")
    @patch("database.setup.psycopg.connect")
    def test_setup_without_reset_does_not_drop_schema(
        self,
        connect_mock,
        execute_sql_mock,
        ensure_database_mock,
    ):
        connection = MagicMock()
        connect_mock.return_value.__enter__.return_value = connection

        database_url = "postgresql://localhost/ecommerce_analytics"

        setup.setup_database(database_url, reset=False)

        ensure_database_mock.assert_called_once_with(database_url)

        paths = [
            call.args[1]
            for call in execute_sql_mock.call_args_list
        ]

        self.assertEqual(
            paths,
            [
                setup.CREATE_SCHEMA,
                setup.CREATE_INDEXES,
                setup.VALIDATE_SCHEMA,
            ],
        )

        self.assertNotIn(setup.DROP_SCHEMA, paths)

    @patch("database.setup.ensure_database", return_value=False)
    @patch("database.setup.execute_sql")
    @patch("database.setup.psycopg.connect")
    def test_setup_with_reset_runs_scripts_in_correct_order(
        self,
        connect_mock,
        execute_sql_mock,
        ensure_database_mock,
    ):
        connection = MagicMock()
        connect_mock.return_value.__enter__.return_value = connection

        database_url = "postgresql://localhost/ecommerce_analytics"

        setup.setup_database(database_url, reset=True)

        ensure_database_mock.assert_called_once_with(database_url)

        paths = [
            call.args[1]
            for call in execute_sql_mock.call_args_list
        ]

        self.assertEqual(
            paths,
            [
                setup.DROP_SCHEMA,
                setup.CREATE_SCHEMA,
                setup.CREATE_INDEXES,
                setup.VALIDATE_SCHEMA,
            ],
        )

    @patch("database.setup.ensure_database", return_value=True)
    @patch("database.setup.execute_sql")
    @patch("database.setup.psycopg.connect")
    def test_reset_does_not_drop_schema_when_database_was_just_created(
        self,
        connect_mock,
        execute_sql_mock,
        ensure_database_mock,
    ):
        connection = MagicMock()
        connect_mock.return_value.__enter__.return_value = connection

        database_url = "postgresql://localhost/ecommerce_analytics"

        setup.setup_database(database_url, reset=True)

        ensure_database_mock.assert_called_once_with(database_url)

        paths = [
            call.args[1]
            for call in execute_sql_mock.call_args_list
        ]

        self.assertEqual(
            paths,
            [
                setup.CREATE_SCHEMA,
                setup.CREATE_INDEXES,
                setup.VALIDATE_SCHEMA,
            ],
        )

        self.assertNotIn(setup.DROP_SCHEMA, paths)

    @patch("database.setup.load_dotenv")
    @patch.dict("os.environ", {}, clear=True)
    def test_main_fails_when_database_url_is_missing(
        self,
        load_dotenv_mock,
    ):
        result = setup.main([])

        self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()