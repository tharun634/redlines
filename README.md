# Redlines
![Repository banner image](repository-open-graph.png)

`Redlines` produces a Markdown text showing the differences between two strings/text. The changes are represented with
strike-throughs and underlines, which looks similar to Microsoft Word's track changes. This method of showing changes is
more familiar to lawyers and is more compact for long series of characters.

Redlines uses [SequenceMatcher](https://docs.python.org/3/library/difflib.html#difflib.SequenceMatcher)
to find differences between words used.

## Example

Given an original string:

    The quick brown fox jumps over the lazy dog.

And the string to be tested with:

    The quick brown fox walks past the lazy dog.

The library gives a result of:

    The quick brown fox <del>jumps over </del><ins>walks past </ins>the lazy dog.

Which is rendered like this:

> The quick brown fox <del>jumps over </del><ins>walks past </ins>the lazy dog.

## Install

```shell
pip install redlines
```

## Usage

The library contains one class: `Redlines`, which is used to compare text.

```python
from redlines import Redlines

test = Redlines(
    "The quick brown fox jumps over the lazy dog.",
    "The quick brown fox walks past the lazy dog.",
)
assert (
        test.output_markdown
        == "The quick brown fox <del>jumps over </del><ins>walks past </ins>the lazy dog."
)
```

Alternatively, you can create Redline with the text to be tested, and compare several times to see the results.

```python
from redlines import Redlines

test = Redlines("The quick brown fox jumps over the lazy dog.")
assert (
        test.compare("The quick brown fox walks past the lazy dog.")
        == "The quick brown fox <del>jumps over </del><ins>walks past </ins>the lazy dog."
)

assert (
        test.compare("The quick brown fox jumps over the dog.")
        == "The quick brown fox jumps over the <del>lazy </del>dog."
)
```

Redlines also features a simple command line tool `redlines` to visualise the differences in text in the terminal.

```
 Usage: redlines text [OPTIONS] SOURCE TEST                                                                                                                                                                                                   
                                                                                                                                                                                                                                              
 Compares the strings SOURCE and TEST and produce a redline in the terminal. 
```

### Custom styling in markdown

By default, markdown output is styled in "red_green", like the following:

> "The quick brown fox <span style='color:red;font-weight:700;text-decoration:line-through;'>jumps
> over </span><span style='color:green;font-weight:700;'>walks past </span>the lazy dog."

Set the `markdown_style` option in the constructor or compare function to change the styling.
The available styles are "red"" and "none".

You can also use css classes to provide custom styling by setting `markdown_style` as "custom_css".
Insertions and deletions are now styled using the "redline-inserted" and "redline-deleted" CSS classes.
You can also set your own CSS classes by specifying the name of the CSS class in the options "ins_class"
and "del_class" respectively in the constructor or compare function.

**Styling will not appear in markdown environments which disallow HTML**. There is no consistent support for 
strikethroughs and colors in the markdown standard, and styling is largely accomplished through raw HTML. 
If you are using GitHub or Streamlit, you may not get the formatting you expect or see any change at all.

To get formatting working in Streamlit, you need to set the `unsafe_allow_html` argument in `st.write` or `st.markdown` to `True`.

## Uses

* View and mark changes in legislation: [PLUS Explorer](https://houfu-plus-explorer.streamlit.app/)
* Visualise changes after ChatGPT transforms a
  text: [ChatGPT Prompt Engineering for Developers](https://www.deeplearning.ai/short-courses/chatgpt-prompt-engineering-for-developers/)
  Lesson 6

## Roadmap / Contributing

Please feel free to post issues and comments. I work on this in my free time, so please excuse lack of activity.

### Nice things to do

* <s>Style the way changes are presented</s>
* Other than Markdown, have other output formats (HTML? PDF?)
* Associate changes with an author
* Show different changes by different authors or times.

If this was useful to you, please feel free to [contact me](mailto:houfu@lovelawrobots.com)!

## License

MIT License

