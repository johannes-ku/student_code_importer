# student_code_importer
> Utility for quickly importing student's solution and tests for it from git into one fixed location

## Setup
1. Copy `config.ini.example` to `config.ini`.
2. Configure repository URLs in `config.ini`.
3. Install dependencies for running tests by running `pip install -r requirements.txt`

## Usage
`python3 importer.py <task> [<student>] [<exercise>]`

#### Tasks

* `help` - Prints help.
* `import` - Imports students solution and tests for the exercise into "working". Requires student and exercise!
* `update` - Updates tests from tests repository. Will not update tests already in "working".
* `clean` - Cleans the "working" directory, existing student sources and tests.
* `test` - Runs tests in "working" directory.

Student's solution will be imported into `working/src` and tests for that exercise will be imported into `working/tests`.
