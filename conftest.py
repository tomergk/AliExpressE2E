import os
import platform
import pytest
from datetime import datetime
from utils.data_loader import load_json

_config = load_json("data/config.json")

# flexibility to run different versions of the test
def pytest_addoption(parser):
    parser.addoption(
        "--profile",
        action="store",
        default="default",
        help="Test profile: default, light, full"
    )

# Hook for running when pytest parses CLI arguments
def pytest_configure(config):
    os.makedirs("reports", exist_ok=True)
    with open(os.path.join("reports", "environment.properties"), "w") as f:
        f.write(f"Browser=Chrome\n")
        f.write(f"OS={platform.system()} {platform.release()}\n")
        f.write(f"Python={platform.python_version()}\n")
        f.write(f"Base.URL={_config['base_url']}\n")


@pytest.fixture(scope="session")
def credentials():
    return load_json("data/credentials.json")

# Loading the profile we asked for in CLI
@pytest.fixture(scope="session")
def search_params(request):
    profile = request.config.getoption("--profile")
    if profile in ("light", "full"):
        return load_json(f"data/profiles/{profile}.json")
    return load_json("data/search_params.json")


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {
        **browser_type_launch_args,
        "channel": "chrome",
        "headless": _config["headless"],
        "slow_mo": _config["slow_mo"],
        # Passes a Chrome flag that hides the fact that the browser 
        # is controlled by automation — helps avoid bot detection on sites like AliExpress.
        "args": ["--disable-blink-features=AutomationControlled"], 
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": None,  # adapts to machine's actual screen; avoids off-screen element issues
        "user_agent": _config["user_agent"],
    }


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture(autouse=True)
def configure_timeouts(page):
    page.set_default_timeout(_config["timeout"]) # max time Playwright will wait for any action
    page.set_default_navigation_timeout(_config["timeout"]) # max time Playwright will wait specifically for page navigation — loading a new URL, waiting for the page to finish loading.
    yield


@pytest.fixture(autouse=True)
def screenshot_on_failure(page, request):
    yield
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        folder = os.path.join("screenshots", "error-screenshots", timestamp)
        os.makedirs(folder, exist_ok=True)
        test_name = request.node.name.replace("[", "_").replace("]", "")
        path = os.path.join(folder, f"{test_name}.png")
        page.screenshot(path=path)
        print(f"\n[Screenshot error has been taken] Saved to {path}")
