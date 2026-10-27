import interui as ui
from interui.context import RenderContext


def test_dynamic_tree_renders_nested_controls():
    tree = ui.Card(title="Hola")(
        ui.Row(
            ui.Col(span=6)(ui.Text("izquierda")),
            ui.Col(span=6)(ui.Button("Pulsar", icon="plus")),
        )
    )
    html = ui.render(tree)
    assert "izquierda" in html
    assert "Pulsar" in html
    assert html.count('class="') >= 5


def test_conditional_rendering():
    ctx = RenderContext()
    assert ui.render(ui.Text("oculto", visible=False), ctx) == ""
    assert ui.render(ui.Text("fuera", when=False), ctx) == ""
    assert "dentro" in ui.render(ui.Text("dentro", when=lambda: True), ctx)


def test_ids_are_stable_and_nest_by_position():
    tree = ui.Stack(ui.Text("a"), ui.Text("b"))
    first = ui.render(tree)
    second = ui.render(tree)
    assert first == second
    assert 'id="r-0"' in first
    assert 'id="r-1"' in second


def test_explicit_ids_and_keys():
    assert 'id="mi-boton"' in ui.render(ui.Button("x", id="mi-boton"))
    assert 'id="r-0-uno"' in ui.render(ui.Stack(ui.Button("x", key="uno")))


def test_event_handlers_are_bound_to_the_rendered_id():
    calls = []
    ctx = RenderContext()
    ui.render(ui.Button("uno", on_click=lambda: calls.append(1)), ctx)
    assert "click" in ctx.bindings["r"]
    ctx.bindings["r"]["click"]()
    assert calls == [1]


def test_event_attributes_are_declared_for_the_client():
    html = ui.render(ui.Input(on_input=lambda: None, on_enter=lambda: None))
    assert 'data-iui-on="enter,input"' in html


def test_form_controls_render_labels_and_help():
    html = ui.render(ui.Input("", label="Nombre", help_text="Como en tu DNI", required=True))
    assert "Nombre" in html
    assert "Como en tu DNI" in html
    assert "required" in html


def test_textarea_content_is_escaped():
    html = ui.render(ui.Textarea("</textarea><script>x</script>"))
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_table_renders_headers_and_rows():
    html = ui.render(
        ui.Table(headers=["A", "B"], rows=[["1", "2"], ["3", "4"]], footer=["total", ""])
    )
    assert "<thead" in html
    assert html.count("<tr") == 4
    assert "total" in html


def test_table_empty_state():
    html = ui.render(ui.Table(headers=["A"], rows=[], empty="nada que ver"))
    assert "nada que ver" in html


def test_charts_produce_valid_svg_geometry():
    html = ui.render(ui.LineChart({"a": [1, 5, 3]}, labels=["x", "y", "z"]))
    assert "<svg" in html
    assert "<path" in html
    assert "NaN" not in html
    assert "Infinity" not in html


def test_pie_chart_percentages():
    html = ui.render(ui.DonutChart({"uno": 25, "dos": 75}))
    assert "25%" in html
    assert "75%" in html


def test_markdown_subset():
    html = ui.render(
        ui.Markdown("# Título\n\n- uno\n- dos\n\n**fuerte** y `código`\n\n> cita")
    )
    assert "<h1" in html
    assert "<li>" in html
    assert "<strong>fuerte</strong>" in html
    assert "<code" in html
    assert "<blockquote" in html


def test_markdown_escapes_html():
    html = ui.render(ui.Markdown("<script>alert(1)</script>"))
    assert "<script>" not in html


def test_icon_falls_back_when_unknown():
    assert "<svg" in ui.render(ui.Icon("no-existe"))


def test_title_bar_exposes_native_buttons():
    html = ui.render(ui.TitleBar("Mi app", icon="layers"))
    assert 'data-iui-native="minimize"' in html
    assert 'data-iui-native="close"' in html
    assert "pywebview-drag-region" in html


def test_native_handlers_receive_events():
    received = []
    node = ui.Button("x", on_click=received.append)
    ctx = RenderContext()
    ui.render(node, ctx)
    ctx.bindings["r"]["click"]("evento")
    assert received == ["evento"]
