"""Alias en minúsculas de todos los controles.

Se declaran explícitamente (no con `globals().update`) para que el editor y
los verificadores de tipos resuelvan `from interui import button` sin
marcarlo como símbolo desconocido.
"""

from __future__ import annotations

from .controls import (
    A,
    Accordion,
    Alert,
    Announcement,
    AreaChart,
    Article,
    Aside,
    Audio,
    Avatar,
    AvatarGroup,
    B,
    Badge,
    Banner,
    BarChart,
    Blockquote,
    Br,
    Breadcrumb,
    Button,
    ButtonGroup,
    Callout,
    Canvas,
    Card,
    Carousel,
    ChartCard,
    Checkbox,
    CheckboxGroup,
    Chip,
    Code,
    CodeBlock,
    CodeEditor,
    Collapse,
    ColorInput,
    ColumnChart,
    Combobox,
    CommandItem,
    CommandPalette,
    ConfirmDialog,
    CopyButton,
    DataTable,
    Datalist,
    DateInput,
    DateRangeInput,
    DateTimeInput,
    DescriptionItem,
    DescriptionList,
    Details,
    DetailsBlock,
    Div,
    DonutChart,
    Drawer,
    Dropdown,
    Dropzone,
    Em,
    EmailInput,
    EmptyState,
    Fab,
    Fieldset,
    Figcaption,
    Figure,
    FileInput,
    Footer,
    Form,
    FormField,
    Gallery,
    Gauge,
    H1,
    H2,
    H3,
    H4,
    H5,
    H6,
    Header,
    Heading,
    Hero,
    HiddenInput,
    Hint,
    Hr,
    Html,
    HtmlFigure,
    HtmlSection,
    I,
    IconBadge,
    IconButton,
    Iframe,
    Image,
    Img,
    InlineToast,
    Input,
    JsonView,
    Kbd,
    KeyValueEditor,
    KeyValueGrid,
    Label,
    Lead,
    Legend,
    Li,
    LineChart,
    Link,
    LinkButton,
    ListGroup,
    ListItem,
    LoadingOverlay,
    LogView,
    Main,
    Mark,
    Markdown,
    Menu,
    MenuItem,
    Meter,
    Modal,
    MonthInput,
    MultiSelect,
    Muted,
    Nav,
    NavLink,
    Navbar,
    NumberInput,
    Ol,
    OtpInput,
    P,
    PageHeader,
    Pagination,
    Panel,
    Paper,
    Paragraph,
    PasswordInput,
    PieChart,
    Popover,
    Pre,
    Progress,
    ProgressRing,
    ProgressTable,
    Radio,
    RadioGroup,
    RangeSlider,
    Rating,
    RichTextEditor,
    S,
    ScatterChart,
    SearchInput,
    Section,
    SegmentedControl,
    Select,
    Sheet,
    Sidebar,
    SidebarItem,
    Skeleton,
    Slider,
    Small,
    Span,
    Sparkline,
    Spinner,
    Splitter,
    Stat,
    StatGrid,
    StatusBar,
    StatusDot,
    Stepper,
    Steps,
    Strong,
    Sub,
    Summary,
    Sup,
    Switch,
    TabBar,
    Table,
    Tabs,
    TagInput,
    Template,
    Terminal,
    Text,
    TextInput,
    Textarea,
    Time,
    TimeInput,
    Timeline,
    TimelineItem,
    TitleBar,
    ToggleGroup,
    Toolbar,
    Tooltip,
    Tree,
    TreeNode,
    U,
    Ul,
    ValidationSummary,
    Video,
    WeekInput,
    Well,
)
from .grid import (
    AspectRatio,
    Center,
    Col,
    Container,
    Divider,
    Grid,
    Screen,
    ScrollArea,
    Spacer,
    Stack,
)
from .icons import (
    Icon,
)

__all__ = [
    "a",
    "accordion",
    "alert",
    "announcement",
    "area_chart",
    "article",
    "aside",
    "aspect_ratio",
    "audio",
    "avatar",
    "avatar_group",
    "b",
    "badge",
    "banner",
    "bar_chart",
    "blockquote",
    "br",
    "breadcrumb",
    "button",
    "button_group",
    "callout",
    "canvas",
    "card",
    "carousel",
    "center",
    "chart_card",
    "checkbox",
    "checkbox_group",
    "chip",
    "code",
    "code_block",
    "code_editor",
    "col",
    "collapse",
    "color_input",
    "column_chart",
    "combobox",
    "command_item",
    "command_palette",
    "confirm_dialog",
    "container",
    "copy_button",
    "data_table",
    "datalist",
    "date_input",
    "date_range_input",
    "date_time_input",
    "description_item",
    "description_list",
    "details",
    "details_block",
    "div",
    "divider",
    "donut_chart",
    "drawer",
    "dropdown",
    "dropzone",
    "em",
    "email_input",
    "empty_state",
    "fab",
    "fieldset",
    "figcaption",
    "figure",
    "file_input",
    "footer",
    "form",
    "form_field",
    "gallery",
    "gauge",
    "grid",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "heading",
    "hero",
    "hidden_input",
    "hint",
    "hr",
    "html",
    "html_figure",
    "html_section",
    "i",
    "icon",
    "icon_badge",
    "icon_button",
    "iframe",
    "image",
    "img",
    "inline_toast",
    "input",
    "json_view",
    "kbd",
    "key_value_editor",
    "key_value_grid",
    "label",
    "lead",
    "legend",
    "li",
    "line_chart",
    "link",
    "link_button",
    "list_group",
    "list_item",
    "loading_overlay",
    "log_view",
    "main",
    "mark",
    "markdown",
    "menu",
    "menu_item",
    "meter",
    "modal",
    "month_input",
    "multi_select",
    "muted",
    "nav",
    "nav_link",
    "navbar",
    "number_input",
    "ol",
    "otp_input",
    "p",
    "page_header",
    "pagination",
    "panel",
    "paper",
    "paragraph",
    "password_input",
    "pie_chart",
    "popover",
    "pre",
    "progress",
    "progress_ring",
    "progress_table",
    "radio",
    "radio_group",
    "range_slider",
    "rating",
    "rich_text_editor",
    "s",
    "scatter_chart",
    "screen",
    "scroll_area",
    "search_input",
    "section",
    "segmented_control",
    "select",
    "sheet",
    "sidebar",
    "sidebar_item",
    "skeleton",
    "slider",
    "small",
    "spacer",
    "span",
    "sparkline",
    "spinner",
    "splitter",
    "stack",
    "stat",
    "stat_grid",
    "status_bar",
    "status_dot",
    "stepper",
    "steps",
    "strong",
    "sub",
    "summary",
    "sup",
    "switch",
    "tab_bar",
    "table",
    "tabs",
    "tag_input",
    "template",
    "terminal",
    "text",
    "text_input",
    "textarea",
    "time",
    "time_input",
    "timeline",
    "timeline_item",
    "title_bar",
    "toggle_group",
    "toolbar",
    "tooltip",
    "tree",
    "tree_node",
    "u",
    "ul",
    "validation_summary",
    "video",
    "week_input",
    "well",
]

a = A
accordion = Accordion
alert = Alert
announcement = Announcement
area_chart = AreaChart
article = Article
aside = Aside
aspect_ratio = AspectRatio
audio = Audio
avatar = Avatar
avatar_group = AvatarGroup
b = B
badge = Badge
banner = Banner
bar_chart = BarChart
blockquote = Blockquote
br = Br
breadcrumb = Breadcrumb
button = Button
button_group = ButtonGroup
callout = Callout
canvas = Canvas
card = Card
carousel = Carousel
center = Center
chart_card = ChartCard
checkbox = Checkbox
checkbox_group = CheckboxGroup
chip = Chip
code = Code
code_block = CodeBlock
code_editor = CodeEditor
col = Col
collapse = Collapse
color_input = ColorInput
column_chart = ColumnChart
combobox = Combobox
command_item = CommandItem
command_palette = CommandPalette
confirm_dialog = ConfirmDialog
container = Container
copy_button = CopyButton
data_table = DataTable
datalist = Datalist
date_input = DateInput
date_range_input = DateRangeInput
date_time_input = DateTimeInput
description_item = DescriptionItem
description_list = DescriptionList
details = Details
details_block = DetailsBlock
div = Div
divider = Divider
donut_chart = DonutChart
drawer = Drawer
dropdown = Dropdown
dropzone = Dropzone
em = Em
email_input = EmailInput
empty_state = EmptyState
fab = Fab
fieldset = Fieldset
figcaption = Figcaption
figure = Figure
file_input = FileInput
footer = Footer
form = Form
form_field = FormField
gallery = Gallery
gauge = Gauge
grid = Grid
h1 = H1
h2 = H2
h3 = H3
h4 = H4
h5 = H5
h6 = H6
header = Header
heading = Heading
hero = Hero
hidden_input = HiddenInput
hint = Hint
hr = Hr
html = Html
html_figure = HtmlFigure
html_section = HtmlSection
i = I
icon = Icon
icon_badge = IconBadge
icon_button = IconButton
iframe = Iframe
image = Image
img = Img
inline_toast = InlineToast
input = Input
json_view = JsonView
kbd = Kbd
key_value_editor = KeyValueEditor
key_value_grid = KeyValueGrid
label = Label
lead = Lead
legend = Legend
li = Li
line_chart = LineChart
link = Link
link_button = LinkButton
list_group = ListGroup
list_item = ListItem
loading_overlay = LoadingOverlay
log_view = LogView
main = Main
mark = Mark
markdown = Markdown
menu = Menu
menu_item = MenuItem
meter = Meter
modal = Modal
month_input = MonthInput
multi_select = MultiSelect
muted = Muted
nav = Nav
nav_link = NavLink
navbar = Navbar
number_input = NumberInput
ol = Ol
otp_input = OtpInput
p = P
page_header = PageHeader
pagination = Pagination
panel = Panel
paper = Paper
paragraph = Paragraph
password_input = PasswordInput
pie_chart = PieChart
popover = Popover
pre = Pre
progress = Progress
progress_ring = ProgressRing
progress_table = ProgressTable
radio = Radio
radio_group = RadioGroup
range_slider = RangeSlider
rating = Rating
rich_text_editor = RichTextEditor
s = S
scatter_chart = ScatterChart
screen = Screen
scroll_area = ScrollArea
search_input = SearchInput
section = Section
segmented_control = SegmentedControl
select = Select
sheet = Sheet
sidebar = Sidebar
sidebar_item = SidebarItem
skeleton = Skeleton
slider = Slider
small = Small
spacer = Spacer
span = Span
sparkline = Sparkline
spinner = Spinner
splitter = Splitter
stack = Stack
stat = Stat
stat_grid = StatGrid
status_bar = StatusBar
status_dot = StatusDot
stepper = Stepper
steps = Steps
strong = Strong
sub = Sub
summary = Summary
sup = Sup
switch = Switch
tab_bar = TabBar
table = Table
tabs = Tabs
tag_input = TagInput
template = Template
terminal = Terminal
text = Text
text_input = TextInput
textarea = Textarea
time = Time
time_input = TimeInput
timeline = Timeline
timeline_item = TimelineItem
title_bar = TitleBar
toggle_group = ToggleGroup
toolbar = Toolbar
tooltip = Tooltip
tree = Tree
tree_node = TreeNode
u = U
ul = Ul
validation_summary = ValidationSummary
video = Video
week_input = WeekInput
well = Well

