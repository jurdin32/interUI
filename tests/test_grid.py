import interui as ui


def classes_of(node: ui.Component) -> list[str]:
    html = ui.render(node)
    start = html.index('class="') + len('class="')
    end = html.index('"', start)
    return html[start:end].split()


def test_row_is_twelve_column_grid():
    classes = classes_of(ui.Row(ui.Col(ui.Text("x"))))
    assert "grid" in classes
    assert "grid-cols-12" in classes


def test_col_responsive_spans():
    classes = classes_of(ui.Col(ui.Text("x"), span=12, md=6, lg=4))
    assert "col-span-12" in classes
    assert "md:col-span-6" in classes
    assert "lg:col-span-4" in classes


def test_col_offset_and_order():
    classes = classes_of(ui.Col(ui.Text("x"), span=6, offset=2, order=1))
    assert "col-start-3" in classes
    assert "order-1" in classes


def test_col_full_and_auto():
    assert "col-span-full" in classes_of(ui.Col("x", span="full"))
    assert "col-span-auto" in classes_of(ui.Col("x", span="auto"))


def test_row_gap_and_alignment():
    classes = classes_of(ui.Row("x", gap=8, align="center", justify="between"))
    assert "gap-8" in classes
    assert "items-center" in classes
    assert "justify-between" in classes


def test_stack_direction():
    row_stack = classes_of(ui.Stack("x", direction="row"))
    col_stack = classes_of(ui.Stack("x"))
    assert "flex-row" in row_stack
    assert "flex-col" in col_stack


def test_native_grid_breakpoints():
    classes = classes_of(ui.Grid("x", cols=1, md=2, lg=4))
    assert "grid-cols-1" in classes
    assert "md:grid-cols-2" in classes
    assert "lg:grid-cols-4" in classes


def test_user_class_overrides_control_default():
    html = ui.render(ui.Col(ui.Text("x"), class_="col-span-12 md:col-span-12"))
    assert "md:col-span-12" in html
    assert "md:col-span-6" not in html
