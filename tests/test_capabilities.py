from paper_digger.capabilities import detect


def test_websearch_is_unknown_until_the_host_reports_it():
    caps = detect(env={}, which=lambda _: None)
    assert caps["websearch"] is None


def test_websearch_can_be_enabled_for_hosts_with_web_tools():
    caps = detect(env={"PAPER_DIGGER_WEBSEARCH": "1"}, which=lambda _: None)
    assert caps["websearch"] is True


def test_websearch_can_be_disabled_for_hosts_without_web_tools():
    caps = detect(env={"PAPER_DIGGER_WEBSEARCH": "0"}, which=lambda _: None)
    assert caps["websearch"] is False


def test_optional_apis_from_env():
    caps = detect(
        env={"S2_API_KEY": "x", "EXA_API_KEY": "y"},
        which=lambda _: None,
    )
    assert caps["scholar_api"] is True
    assert caps["exa"] is True
    assert caps["firecrawl"] is False


def test_ssh_uses_which():
    assert detect(env={}, which=lambda name: "/usr/bin/ssh")["ssh"] is True
    assert detect(env={}, which=lambda name: None)["ssh"] is False
