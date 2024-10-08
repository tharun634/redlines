from __future__ import annotations

import re

from rich.text import Text

from redlines.document import Document

tokenizer = re.compile(r"((?:[^()\s]+|[().?!-])\s*)")
"""
This regular expression matches a group of characters that can include any character except for parentheses
and whitespace characters (which include spaces, tabs, and line breaks) or any character
that is a parenthesis or punctuation mark (.?!-).
The group can also include any whitespace characters that follow these characters.

Breaking it down further:

* `(` and `)` indicate a capturing group
* `(?: )` is a non-capturing group, meaning it matches the pattern but doesn't capture the matched text
* `[^()\s]+` matches one or more characters that are not parentheses or whitespace characters
* `|` indicates an alternative pattern
* `[().?!-]` matches any character that is a parenthesis or punctuation mark `(.?!-)`
* `\s*` matches zero or more whitespace characters (spaces, tabs, or line breaks) that follow the previous pattern.
"""
# This pattern matches one or more newline characters `\n`, and any spaces between them.

paragraph_pattern = re.compile(r"((?:\n *)+)")
"""
It is used to split the text into paragraphs.

* `(?:\\n *)` is a non-capturing group that must start with a `\\n`   and be followed by zero or more spaces.
* `((?:\\n *)+)` is the previous non-capturing group repeated one or more times.
"""

space_pattern = re.compile(r"(\s+)")
"""It is used to detect space."""


def tokenize_text(text: str) -> list[str]:
    return re.findall(tokenizer, text)


def split_paragraphs(text: str) -> list[str]:
    """
    Splits a string into a list of paragraphs. One or more `\n` splits the paragraphs.
    For example, if the text is "Hello\nWorld\nThis is a test", the result will be:
    ['Hello', 'World', 'This is a test']

    :param text: The text to split.
    :return: a list of paragraphs.
    """

    split_text = re.split(paragraph_pattern, text)
    result = []
    for s in split_text:
        if s and not re.fullmatch(space_pattern, s):
            result.append(s.strip())

    return result


def concatenate_paragraphs_and_add_chr_182(text: str) -> str:
    """
    Split paragraphs and concatenate them. Then add a character '¶' between paragraphs.
    For example, if the text is "Hello\nWorld\nThis is a test", the result will be:
    "Hello¶World¶This is a test"

    :param text: The text to split.
    :return: a list of paragraphs.
    """
    paragraphs = split_paragraphs(text)

    result = []
    for p in paragraphs:
        result.append(p)
        result.append(" ¶ ")
        # Add a string ' ¶ ' between paragraphs.
    if len(paragraphs) > 0:
        result.pop()

    return "".join(result)


class Redlines:
    _source: str = None
    _test: str = None
    _seq1: list[str] = None
    _seq2: list[str] = None

    @property
    def source(self) -> str:
        """
        :return: The source text to be used as a basis for comparison.
        """
        return self._source

    @source.setter
    def source(self, value):
        self._source = value
        self._seq1 = tokenize_text(concatenate_paragraphs_and_add_chr_182(value))

    @property
    def test(self):
        """:return: The text to be compared with the source."""
        return self._test

    @test.setter
    def test(self, value):
        self._test = value
        self._seq2 = tokenize_text(concatenate_paragraphs_and_add_chr_182(value))

    def __init__(
        self, source: str | Document, test: str | Document | None = None, **options
    ):
        """
        Redline is a class used to compare text, and producing human-readable differences or deltas
        which look like track changes in Microsoft Word.

        ```python
        # import the class
        from redlines import Redlines

        # Create a Redlines object using the two strings to compare
        test = Redlines(
            "The quick brown fox jumps over the lazy dog.",
            "The quick brown fox walks past the lazy dog.",
        )

        # This produces an output in Markdown format
        test.output_markdown
        ```

        Besides strings, Redlines can also receive an input in another format if it is supported by the Document class

        ```python
        from redlines import PlainTextFile

        source = PlainTextFile("tests/documents/PlainTextFile/source.txt")
        test = PlainTextFile("tests/documents/PlainTextFile/test.txt")

        redline = Redlines(source, test)
        assert (
            redline.output_markdown
            == "The quick brown fox <span style='color:red;font-weight:700;text-decoration:line-through;'>jumps over </span><span style='color:green;font-weight:700;'>walks past </span>the lazy dog."
        )

        ```

        :param source: The source text to be used as a basis for comparison.
        :param test: Optional test text to compare with the source.
        """
        self.source = source.text if isinstance(source, Document) else source
        self.options = options
        if test:
            self.test = test.text if isinstance(test, Document) else test
            # self.compare()

    @property
    def opcodes(self) -> list[tuple[str, int, int, int, int]]:
        """
        Return list of 5-tuples describing how to turn `source` into `test`.
        Similar to [`SequenceMatcher.get_opcodes`](https://docs.python.org/3/library/difflib.html#difflib.SequenceMatcher.get_opcodes).

        ```pycon
        >>> test_string_1 = 'The quick brown fox jumps over the lazy dog.'
        ... test_string_2 = 'The quick brown fox walks past the lazy dog.'
        ... s = Redlines(test_string_1, test_string_2)
        ... s.opcodes
        [('equal', 0, 4, 0, 4), ('replace', 4, 6, 4, 6), ('equal', 6, 9, 6, 9)]
        ```
        """
        if self._seq2 is None:
            raise ValueError(
                "No test string was provided when the function was called, or during initialisation."
            )

        from difflib import SequenceMatcher

        matcher = SequenceMatcher(None, self._seq1, self._seq2)
        return matcher.get_opcodes()

    @property
    def output_markdown(self) -> str:
        """
        Returns the delta in Markdown format.

        ## Styling Markdown
        To output markdown in a particular manner, you must pass a `markdown_style` option when the `Redlines` object
        is created or when `Redlines.compare` is called.

        ```python
        from redlines import Redlines

        test = Redlines(
            "The quick brown fox jumps over the lazy dog.",
            "The quick brown fox walks past the lazy dog.",
            markdown_style="red"  # This option specifies the style as red
        )

        test.compare(markdown_style="none") # This option specifies the style as none
        ```

        ### Available styles

        | Style | Preview |
        |-------| -------|
        |red-green (**default**) | "The quick brown fox <span style='color:red;font-weight:700;text-decoration:line-through;'>jumps over </span><span style='color:green;font-weight:700;'>walks past </span>the lazy dog."|
        |none | 'The quick brown fox <del>jumps over </del><ins>walks past </ins>the lazy dog.'|
        |red | "The quick brown fox <span style='color:red;font-weight:700;text-decoration:line-through;'>jumps over </span><span style='color:red;font-weight:700;'>walks past </span>the lazy dog."|
        |ghfm (GitHub Flavored Markdown)| 'The quick brown fox ~~jumps over ~~**walks past **the lazy dog.' |
        |bbcode (BBCode) | 'The quick brown fox [s][color=red]jumps over [/color][/s][b][color=green]walks past [/color][/b]the lazy dog.' |

        ### Custom styling

        You can also use css classes to provide custom styling by setting `markdown_style` as "custom_css".
        Insertions and deletions are now styled using the "redline-inserted" and "redline-deleted" CSS classes.
        You can also set your own CSS classes by specifying the name of the CSS class in the options `ins_class`
        and `del_class` respectively in the constructor or compare function.

        ## Markdown output in specific environments

        Users have reported that the output doesn't display correctly in their environments.
        This is because styling may not appear in markdown environments which disallow HTML.
        There is no consistent support for strikethroughs and colors in the markdown standard,
        and styling is largely accomplished through raw HTML. If you are using GitHub or Streamlit, you may not get
        the formatting you expect or see any change at all.

        If you are facing this kind of difficulty, here are some recommendations. If your experience doesn't match
        the hints or description below, or you continue to face problems, please raise an issue.

        ### Jupyter Notebooks
        This library was first written for the Jupyter notebook environment, so all the available styles, including
        the default (`red-green`), `red` and `none` work.

        ### Streamlit

        Try this:

        * Enable parsing of HTML. In Streamlit, you need to set the `unsafe_allow_html` argument in `st.write` or
        `st.markdown` to `True`.
        * Use the markdown style `ghfm`

        ### Colab

        Try this:
        * Use the markdown style `none` or `ghfm`
        * `Redlines.output_rich` has been reported to work in Colab

        """
        result = []

        # default_style = "red_green"

        md_styles = {
            "ins": (
                f"<span style='color:green;font-weight:700;'>",
                "</span>",
            ),
            "del": (
                f"<span style='color:red;font-weight:700;text-decoration:line-through;'>",
                "</span>",
            ),
        }

        if "markdown_style" in self.options:
            style = self.options["markdown_style"]

            if style == "none" or style is None:
                md_styles = {"ins": ("<ins>", "</ins>"), "del": ("<del>", "</del>")}
            elif style == "red":
                md_styles = {
                    "ins": (
                        f"<span style='color:red;font-weight:700;'>",
                        "</span>",
                    ),
                    "del": (
                        f"<span style='color:red;font-weight:700;text-decoration:line-through;'>",
                        "</span>",
                    ),
                }
            elif style == "custom_css":
                ins_class = (
                    self.options["ins_class"]
                    if "ins_class" in self.options
                    else "redline-inserted"
                )
                del_class = (
                    self.options["del_class"]
                    if "del_class" in self.options
                    else "redline-deleted"
                )

                elem_attributes = {
                    "ins": f"class='{ins_class}'",
                    "del": f"class='{del_class}'",
                }

                md_styles = {
                    "ins": (
                        f"<span {elem_attributes['ins']}>",
                        "</span>",
                    ),
                    "del": (
                        f"<span {elem_attributes['del']}>",
                        "</span>",
                    ),
                }
            elif style == "ghfm":
                md_styles = {"ins": ("**", "**"), "del": ("~~", "~~")}
            elif style == "bbcode":
                md_styles = {"ins": ("[b][color=green]", "[/color][/b]"), "del": ("[s][color=red]", "[/color][/s]")}

        for tag, i1, i2, j1, j2 in self.opcodes:
            if tag == "equal":
                temp_str = "".join(self._seq1[i1:i2])
                temp_str = re.sub("¶ ", "\n\n", temp_str)
                # here we use '¶ ' instead of ' ¶ ', because the leading space will be included in the previous token,
                # according to tokenizer = re.compile(r"((?:[^()\s]+|[().?!-])\s*)")
                result.append(temp_str)
            elif tag == "insert":
                temp_str = "".join(self._seq2[j1:j2])
                splits = re.split("¶ ", temp_str)
                for split in splits:
                    result.append(f"{md_styles['ins'][0]}{split}{md_styles['ins'][1]}")
                    result.append("\n\n")
                if len(splits) > 0:
                    result.pop()
            elif tag == "delete":
                result.append(
                    f"{md_styles['del'][0]}{''.join(self._seq1[i1:i2])}{md_styles['del'][1]}"
                )
                # for 'delete', we make no change, because otherwise there will be two times '\n\n' than the original
                # text.
            elif tag == "replace":
                result.append(
                    f"{md_styles['del'][0]}{''.join(self._seq1[i1:i2])}{md_styles['del'][1]}"
                )
                temp_str = "".join(self._seq2[j1:j2])
                splits = re.split("¶ ", temp_str)
                for split in splits:
                    result.append(f"{md_styles['ins'][0]}{split}{md_styles['ins'][1]}")
                    result.append("\n\n")
                if len(splits) > 0:
                    result.pop()

        return "".join(result)

    @property
    def output_rich(self) -> Text:
        """Returns the delta in text with colors/style for the console."""
        console_text = Text()

        for tag, i1, i2, j1, j2 in self.opcodes:
            if tag == "equal":
                temp_str = "".join(self._seq1[i1:i2])
                temp_str = re.sub("¶ ", "\n\n", temp_str)
                console_text.append(temp_str)
            elif tag == "insert":
                temp_str = "".join(self._seq2[j1:j2])
                splits = re.split("¶ ", temp_str)
                for split in splits:
                    console_text.append(split, "green")
            elif tag == "delete":
                console_text.append("".join(self._seq1[i1:i2]), "strike red")
            elif tag == "replace":
                console_text.append("".join(self._seq1[i1:i2]), "strike red")
                temp_str = "".join(self._seq2[j1:j2])
                splits = re.split("¶ ", temp_str)
                for split in splits:
                    console_text.append(split, "green")

        return console_text

    def compare(self, test: str | None = None, output: str = "markdown", **options):
        """
        Compare `test` with `source`, and produce a delta in a format specified by `output`.

        :param test: Optional test string to compare. If None, uses the test string provided during initialisation.
        :param output: The format which the delta should be produced. Currently, only "markdown" is supported
        :return: The delta in the format specified by `output`.
        """
        if test:
            if self.test and test == self.test:
                return self.output_markdown
            else:
                self.test = test
        elif self.test is None:
            raise ValueError(
                "No test string was provided when the function was called, or during initialisation."
            )

        if options:
            self.options = options

        if output == "markdown":
            return self.output_markdown
