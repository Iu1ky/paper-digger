def test_package_has_version():
    import paper_digger

    assert isinstance(paper_digger.__version__, str)
    assert paper_digger.__version__
