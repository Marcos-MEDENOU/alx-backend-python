# Unit Testing and Integration Testing in Python

This project focuses on understanding and implementing unit tests and integration tests in Python. It covers various testing patterns including mocking, parameterization, and fixtures.

## Learning Objectives

- Understand the difference between unit and integration tests
- Implement unit tests using Python's `unittest` framework
- Use parameterization to test multiple inputs with the same test function
- Implement mocking to isolate tests from external dependencies
- Understand and implement test fixtures
- Write documentation for test cases

## Requirements

- Python 3.7
- Ubuntu 18.04 LTS
- pycodestyle (version 2.5)
- parameterized

## Installation

```bash
pip install parameterized
```

## Running Tests

To run all tests:

```bash
python -m unittest discover -s . -p "test_*.py" -v
```

To run a specific test file:

```bash
python -m unittest test_utils.py -v
```

## File Structure

- `utils.py`: Contains utility functions to be tested
- `test_utils.py`: Contains test cases for the utility functions

## Author

ALX Student

## License

This project is licensed under the MIT License.
