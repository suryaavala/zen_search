import pytest

from zensearch.exceptions import PrimaryKeyNotFoundError, DuplicatePrimaryKeyError


class TestPrimaryKeyNotFoundError:
    def test_primkey_error_custom_message(self):
        """Primary key error should display custom message
        """
        test_custom_error_message = "my_custom_error_message"

        with pytest.raises(PrimaryKeyNotFoundError) as error:
            raise PrimaryKeyNotFoundError(test_custom_error_message)

        assert test_custom_error_message == str(error.value)

    def test_primkey_error_default_message(self):
        """Primary key error should display default message when none's provided
        """
        default_message = "Cannot find primary key in the data point. Every data point should at least have primary key"
        with pytest.raises(PrimaryKeyNotFoundError) as error:
            raise PrimaryKeyNotFoundError()

        assert default_message == str(error.value)


class TestDuplicatePrimaryKeyError:
    def test_dup_primkey_error_custom_message(self):
        """Duplicate Primary key error should display custom message
        """
        test_custom_error_message = "my_custom_error_message"

        with pytest.raises(DuplicatePrimaryKeyError) as error:
            raise DuplicatePrimaryKeyError(test_custom_error_message)

        assert test_custom_error_message == str(error.value)

    def test_primkey_error_default_message(self):
        """Primary key error should display default message when none's provided
        """
        default_message = "Duplicate primary key value found in the data point. It's been assumed that every entity should have a unique set of primary keys"

        with pytest.raises(DuplicatePrimaryKeyError) as error:
            raise DuplicatePrimaryKeyError()

        assert default_message == str(error.value)
