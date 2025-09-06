# 1. Introduction / Welcome

Thanks for your interest in Qonscious. You are welcomed to contribute with improvements, fixes, and extensions. Just keep in mind that Qonscious is in active development and it is part of a research project. In that context, we may not be able (or willing to) integrate all proposals. However, you can work on you own version of Qonsiocus is you cite this work.  

# 2.	Code of Conduct (link or summary)

* Be nice.
* Be prepare for APIs to change. 
* If you use Qonscious (or find it interesting), reference it.
* If you write an article talking about or using Qonscious, cite one of the articles listed in the project's home page. 

# 3.	How to Contribute

* Report bugs and suggest features as Github issues.
* Asking questions by email to any of the maintainers.
* Use (piecemeal) pull request to propose changes.
* Document your code as described below.

# 4.    What to contribute

Qonscious is an experimentation platform. As such, it already foresees a few extension points (where you can hang your contributions). Each of these extension point is present in the design as an abstract class, dictype or protocol that you can extend. 

* **Adapters**: Adapters (backend adapters) give Qonscious users independence from specific vendor APIs. Using adapters makes a tradeoff between abstraction (polimorphic APIs) and control (using QPU specific features). 

* **Functions of merit**: Functions of Merit (FoM's) capture the charateristics of a quantum computing platform (QPU or Simulator) that are relevant for computing. Creating and using FoM's is Qonscious way on reflecting and learning about quantum computation resources in the NISQ era.

**Notebooks**: You can also contribute with usage examples in the form of Jupyter notebooks that use Qonscious. 

**Merit compliance checks** You often use FoM's to check if a given backend (i.e., adapted backend) offers the resources your use case needs. Checks (implementes as instances of the MeritComplianceCheck class) combine a FoM with a callback function that takes the result of checking that FoM on the backend and resutls true of false. Writing these checks is a bit convoluted so having many examples is useful.

# 5.    Versioning and releasing

In the current phase of development, the design of Qonscious will change often. As we create new FoMs, provide new backend adapters, and explore usage scenarios, the API will change. There will be no PyPI version you can install with pip. For the time being, you install with `pip install -e`

# 6.	Development notes

## Typing

This project uses pyright as a typechecker (In VSCode it will work via PyLance). Settings are defined in pyrightconfig.json

## Formating and linting

This project uses ruff for formating, linting, etc.

pyproject.toml includes default configurations for ruff

Ruff is part of the [dev] dependencies.

To use ruff from the command line (and let ruff format, and tidy up code),  do as follows:

```python
ruff check . --fix
ruff format .
```

## Testing

Make sure that any extensions/improvement/changes you contribute are covered by unit tests.

Mark test methods that interact with IBM's backend (thus requiring a token) with the annotation `@pytest.mark.ibm_token_required`

Use:
* `pytest` : to run all tests
* `pytest -m "not (ibm_token_required or ionq_apikey_required)"` : to only run tests that to not interact with IBM's or IONQ`sbackend
* `pytest -m "ibm_token_required"` : to only run tests that that do interact with IBM's backend
* `pytest -m "ionq_apikey_required"` : to only run tests that that do interact with IONQ'S backend


## VisualStudio Code

There is a _vscode_example_settings.json file that you can rename to .vscode/settings.json . It provides most default settings that help VSC find tests, work with notebooks, etc. 

# Keep documentation up to date

We use mkdocs + mkdocstrings to generate documentation.

## One-time setup
- Install deps: `pip install -e ".[docs]"` (or `pip install mkdocs mkdocs-material mkdocstrings[python]`)
- Ensure you have:
  - `mkdocs.yml` at repo root
  - `docs/index.md`, `docs/reference/index.md` (with `::: qonscious`)

## Write good docstrings + type hints
- Use [Google style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) consistently.
- Public APIs should document: summary, Args, Returns, Raises, Examples.

## Preview locally while writing

```bash
mkdocs serve
```
