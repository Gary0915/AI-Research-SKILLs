from thesis_deck_system.slides import compile_slide


def test_only_two_recipes_compile_backend_neutral_specs():
    photo = compile_slide("B001", "observation", "photo_observation", 1)
    plot = compile_slide("B001", "result", "hero_plot_discussion", 1)
    assert {photo["recipe"], plot["recipe"]} == {"photo_observation", "hero_plot_discussion"}
    assert "python-pptx" not in repr(photo)


def test_unknown_recipe_rejected():
    try:
        compile_slide("B001", "observation", "timeline", 1)
    except ValueError as error:
        assert "recipe" in str(error)
    else:
        raise AssertionError("unknown recipe accepted")
