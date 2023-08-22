from time import sleep

import pytest

from qbittorrentapi import NotFound404Error
from qbittorrentapi.search import SearchJobDictionary
from qbittorrentapi.search import SearchResultsDictionary
from qbittorrentapi.search import SearchStatusesList
from tests.utils import check
from tests.utils import get_func
from tests.utils import retry

PLUGIN_NAME = "legittorrents"
LEGIT_TORRENTS_URL = "https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines/legittorrents.py"


@pytest.mark.skipif_before_api_version("2.1.1")
@pytest.mark.parametrize(
    "client_func", ("search_update_plugins", "search.update_plugins")
)
def test_update_plugins(client, client_func):
    get_func(client, client_func)()
    check(
        lambda: any(
            entry.message.startswith("Updating plugin ")
            or entry.message == "All plugins are already up to date."
            or entry.message.endswith("content was not found at the server (404)")
            for entry in reversed(client.log.main())
        ),
        True,
    )


@pytest.mark.skipif_after_api_version("2.1.1")
@pytest.mark.parametrize(
    "client_func", ("search_update_plugins", "search.update_plugins")
)
def test_update_plugins_not_implemented(client, client_func):
    with pytest.raises(NotImplementedError):
        client.search_update_plugins()


@pytest.mark.skipif_before_api_version("2.1.1")
@pytest.mark.parametrize(
    "client_func",
    (
        ("search_plugins", "search_enable_plugin"),
        ("search.plugins", "search.enable_plugin"),
    ),
)
def test_enable_plugin(client, client_func):
    @retry()
    def enable_plugin():
        try:
            plugins = get_func(client, client_func[0])()
        except TypeError:
            plugins = get_func(client, client_func[0])
        get_func(client, client_func[1])(
            plugins=(p["name"] for p in plugins), enable=False
        )
        check(
            lambda: (p["enabled"] for p in client.search_plugins()),
            True,
            reverse=True,
            negate=True,
        )
        get_func(client, client_func[1])(
            plugins=(p["name"] for p in plugins), enable=True
        )
        check(
            lambda: (p["enabled"] for p in client.search_plugins()),
            False,
            reverse=True,
            negate=True,
        )

    enable_plugin()


@pytest.mark.skipif_after_api_version("2.1.1")
@pytest.mark.parametrize(
    "client_func", ("search_enable_plugin", "search.enable_plugin")
)
def test_enable_plugin_not_implemented(client, client_func):
    with pytest.raises(NotImplementedError):
        get_func(client, client_func)()


@pytest.mark.skipif_before_api_version("2.1.1")
@pytest.mark.parametrize(
    "client_func",
    (
        ("search_install_plugin", "search_uninstall_plugin"),
        ("search.install_plugin", "search.uninstall_plugin"),
    ),
)
def test_install_uninstall_plugin(client, client_func):
    @retry()
    def install_plugin(client, client_func):
        get_func(client, client_func[0])(sources=LEGIT_TORRENTS_URL)
        check(
            lambda: (p.name for p in client.search.plugins),
            PLUGIN_NAME,
            reverse=True,
        )

    @retry()
    def uninstall_plugin(client, client_func):
        get_func(client, client_func[1])(names=PLUGIN_NAME)
        check(
            lambda: (p.name for p in client.search.plugins),
            PLUGIN_NAME,
            reverse=True,
            negate=True,
        )

    install_plugin(client, client_func)
    uninstall_plugin(client, client_func)


@pytest.mark.skipif_after_api_version("2.1.1")
@pytest.mark.parametrize(
    "client_func",
    (
        ("search_install_plugin", "search_uninstall_plugin"),
        ("search.install_plugin", "search.uninstall_plugin"),
    ),
)
def test_install_uninstall_plugin_not_implemented(client, client_func):
    with pytest.raises(NotImplementedError):
        get_func(client, client_func[0])()
    with pytest.raises(NotImplementedError):
        get_func(client, client_func[1])()


@pytest.mark.skipif_before_api_version("2.1.1")
@pytest.mark.skipif_after_api_version("2.6")
@pytest.mark.parametrize("client_func", ("search_categories", "search.categories"))
def test_categories(client, client_func):
    check(lambda: get_func(client, client_func)(), "All categories", reverse=True)


@pytest.mark.skipif_after_api_version("2.1.1")
@pytest.mark.parametrize("client_func", ("search_categories", "search.categories"))
def test_categories_not_implemented(client, client_func):
    with pytest.raises(NotImplementedError):
        get_func(client, client_func)()


@pytest.mark.skipif_before_api_version("2.1.1")
@pytest.mark.parametrize(
    "client_func",
    (
        (
            "search_start",
            "search_status",
            "search_results",
            "search_stop",
            "search_delete",
        ),
        (
            "search.start",
            "search.status",
            "search.results",
            "search.stop",
            "search.delete",
        ),
    ),
)
def test_search(client, client_func):
    job = get_func(client, client_func[0])(
        pattern="Ubuntu", plugins="enabled", category="all"
    )
    statuses = get_func(client, client_func[1])(search_id=job["id"])
    assert statuses[0]["status"] == "Running"
    assert isinstance(job, SearchJobDictionary)
    assert isinstance(statuses, SearchStatusesList)
    results = get_func(client, client_func[2])(search_id=job["id"], limit=1)
    assert isinstance(results, SearchResultsDictionary)
    results = job.results()
    assert isinstance(results, SearchResultsDictionary)
    get_func(client, client_func[3])(search_id=job["id"])
    check(
        lambda: get_func(client, client_func[1])(search_id=job["id"])[0]["status"],
        "Stopped",
    )
    get_func(client, client_func[4])(search_id=job["id"])
    statuses = get_func(client, client_func[1])()
    assert not statuses


@pytest.mark.skipif_after_api_version("2.1.1")
@pytest.mark.parametrize(
    "client_func",
    (
        "search_start",
        "search_status",
        "search_results",
        "search_stop",
        "search_delete",
        "search.start",
        "search.status",
        "search.results",
        "search.stop",
        "search.delete",
    ),
)
def test_search_not_implemented(client, client_func):
    with pytest.raises(NotImplementedError):
        get_func(client, client_func)()


@pytest.mark.skipif_before_api_version("2.1.1")
@pytest.mark.parametrize(
    "client_func", (("search_stop", "search_start"), ("search.stop", "search.start"))
)
def test_stop(client, client_func):
    job = get_func(client, client_func[1])(
        pattern="Ubuntu", plugins="enabled", category="all"
    )
    sleep(1)
    get_func(client, client_func[0])(search_id=job.id)
    check(lambda: client.search.status(search_id=job["id"])[0]["status"], "Stopped")

    job = get_func(client, client_func[1])(
        pattern="Ubuntu", plugins="enabled", category="all"
    )
    sleep(1)
    job.stop()
    check(lambda: client.search.status(search_id=job["id"])[0]["status"], "Stopped")


@pytest.mark.skipif_after_api_version("2.1.1")
@pytest.mark.parametrize(
    "client_func", ("search_stop", "search_start", "search.stop", "search.start")
)
def test_stop_not_implemented(client, client_func):
    with pytest.raises(NotImplementedError):
        get_func(client, client_func)()


@pytest.mark.skipif_before_api_version("2.1.1")
def test_delete(client):
    job = client.search_start(pattern="Ubuntu", plugins="enabled", category="all")
    job.delete()
    with pytest.raises(NotFound404Error):
        job.status()


@pytest.mark.skipif_after_api_version("2.1.1")
def test_delete_not_implemented(client):
    with pytest.raises(NotImplementedError):
        client.search_stop(search_id=100)
